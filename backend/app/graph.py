"""
LangGraph workflow orchestration for NOVA Pharmacovigilance
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Literal
import json
from pathlib import Path
from langgraph.graph import StateGraph, END
from app.state import NovaState, create_initial_state, add_message_to_state
from app.services.llm_service import gemini_service
from app.services.mongodb_service import mongodb_service
from app.schemas.case_schemas import ExtractedData, CaseDocument
from app.config import settings

logger = logging.getLogger(__name__)

# Load prompts
PROMPTS_DIR = Path(__file__).parent


def load_prompt(filepath: str) -> str:
    """Load prompt from file"""
    try:
        with open(PROMPTS_DIR / filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading prompt {filepath}: {str(e)}")
        return ""


async def save_state(state: NovaState):
    """Utility to persist current state to MongoDB"""
    from app.schemas.case_schemas import CaseDocument, ExtractedData
    from app.services.mongodb_service import mongodb_service
    
    try:
        case = CaseDocument(
            case_id=state["case_id"],
            sender_phone=state["sender_phone"],
            sender_type=state.get("sender_type", "patient"),
            language=state.get("language", "en"),
            verified_doctor=state.get("verified_doctor", False),
            license_status=state.get("license_status"),
            extracted_data=ExtractedData(**state.get("extracted_data", {})),
            completeness_score=state.get("completeness_score", 0.0),
            confidence_score=state.get("confidence_score", 0.0),
            triage_classification=state.get("triage_classification"),
            messages=state.get("messages", []),
            attachments=state.get("attachments", []),
            status=state.get("status", "open"),
            current_node=state.get("current_node")
        )
        await mongodb_service.save_case(case)
        logger.debug(f"State persisted for {state['case_id']}")
    except Exception as e:
        logger.error(f"Failed to auto-save state: {e}")


# ==================== NODE FUNCTIONS ====================

async def initial_classification_node(state: NovaState) -> NovaState:
    """
    Step 1: Detect Language AND Greet for user type.
    Language detection is done via LLM, but user-type selection is deterministic.
    """
    # 1. Generate Case ID if not exists
    if not state.get("case_id"):
        state["case_id"] = f"CASE-{uuid.uuid4().hex[:12].upper()}"
        logger.info(f"Generated new Case ID: {state['case_id']}")

    # 2. Detect Language if not already set
    if not state.get("language"):
        first_msg = state["messages"][0]["content"]
        try:
            # Quick LLM call for language ONLY
            lang_json = await gemini_service.generate_text(
                prompt=f"Detect the language of this text and return ONLY a JSON object with 'language' (ISO 639-1 code). Text: \"{first_msg}\"",
                response_schema={"type": "object", "properties": {"language": {"type": "string"}}}
            )
            data = json.loads(lang_json)
            state["language"] = data.get("language", "en")
            logger.info(f"Detected language: {state['language']}")
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            state["language"] = "en"

    # 2. Prioritize Image/OCR
    if state.get("pending_image_data"):
        state["current_node"] = "document_extraction"
        return state

    # 4. Check if we're continuing an existing workflow
    # If current_node is set and we're not at the start, route directly to that node
    current_node = state.get("current_node")
    if current_node and current_node not in ["initial_classification", "awaiting_user_type"]:
        # We're continuing an existing workflow - skip re-classification
        logger.info(f"Continuing existing workflow at node: {current_node}")
        return state

    # 5. Save intermediate state to MongoDB before waiting
    await save_state(state)

    # 6. Handle Role Selection
    if state.get("sender_type"):
        return state

    # Check if this is the start or if we just asked
    messages = state.get("messages", [])
    user_messages = [m for m in messages if m["role"] == "user"]
    
    # If the user just said "hii" and we haven't asked yet
    if len(user_messages) == 1:
        welcome_msg = "Welcome to NOVA Pharmacovigilance. To assist you better, are you a **Patient** or a **Healthcare Professional (Doctor)**?"
        state = add_message_to_state(state, "assistant", welcome_msg)
        state["current_node"] = "awaiting_user_type"
        return state

    # If they replied, try to identify the choice
    last_msg = user_messages[-1]["content"].lower()
    if "patient" in last_msg:
        state["sender_type"] = "patient"
        state["current_node"] = "patient_doc_request"
    elif "doctor" in last_msg or "professional" in last_msg or "physician" in last_msg:
        state["sender_type"] = "doctor"
        state["current_node"] = "doctor_registry_check"
    
    # If we identified it, proceed
    if state.get("sender_type"):
        return state
    else:
        # Re-ask if they didn't specify clearly
        follow_up = "I'm sorry, I didn't catch that. Please let me know if you are a **Patient** or a **Doctor**."
        state = add_message_to_state(state, "assistant", follow_up)
        state["current_node"] = "awaiting_user_type"

    return state


async def patient_doc_request_node(state: NovaState) -> NovaState:
    """
    Request prescription or bill from patient.
    Allows skipping if patient doesn't have document.
    Uses LLM to detect if patient wants to skip.
    """
    logger.info("Node: patient_doc_request")
    
    # If an image was just uploaded, we move to extraction
    if state.get("pending_image_data"):
        state["current_node"] = "document_extraction"
        return state

    # Check user's last message to see if they want to skip
    messages = state.get("messages", [])
    user_messages = [m for m in messages if m["role"] == "user"]
    last_user_msg = user_messages[-1]["content"] if user_messages else ""
    
    # Check if we've already asked about the document
    last_assistant_msg = next((m["content"] for m in reversed(messages) if m["role"] == "assistant"), "")
    
    # Use LLM to determine if user wants to skip document upload
    if last_user_msg and last_assistant_msg and "upload a photo" in last_assistant_msg.lower():
        # User has responded after we asked for document - check their intent
        try:
            from app.services.llm_service import RateLimitError
            
            intent_prompt = f"""Analyze the user's message and determine if they are indicating they don't have the document/prescription/medical bill, or if they want to skip uploading it and proceed with manual entry.

User message: "{last_user_msg}"

Respond with JSON:
{{
    "wants_to_skip": true/false,
    "reason": "brief explanation"
}}

Examples:
- "I don't have it" → {{"wants_to_skip": true, "reason": "user doesn't have document"}}
- "I donot have it" → {{"wants_to_skip": true, "reason": "user doesn't have document"}}
- "No prescription" → {{"wants_to_skip": true, "reason": "user doesn't have prescription"}}
- "Skip" → {{"wants_to_skip": true, "reason": "user wants to skip"}}
- "Here's the photo" → {{"wants_to_skip": false, "reason": "user is providing document"}}
- "I'll upload it later" → {{"wants_to_skip": false, "reason": "user will provide later"}}
"""
            
            intent_json = await gemini_service.generate_text(
                prompt=intent_prompt,
                response_schema={
                    "type": "object",
                    "properties": {
                        "wants_to_skip": {"type": "boolean"},
                        "reason": {"type": "string"}
                    },
                    "required": ["wants_to_skip", "reason"]
                }
            )
            
            intent_data = json.loads(intent_json)
            wants_to_skip = intent_data.get("wants_to_skip", False)
            logger.info(f"LLM detected skip intent: {wants_to_skip}, reason: {intent_data.get('reason')}")
            
            if wants_to_skip:
                # User doesn't have document - proceed to manual intake
                skip_msg = "No problem! I'll help you fill in the information manually. Let's start by gathering the details about your medication and symptoms."
                state = add_message_to_state(state, "assistant", skip_msg)
                state["current_node"] = "patient_intake"
                await save_state(state)
                return state
                
        except RateLimitError:
            # If LLM quota exceeded, fall back to keyword matching
            logger.warning("LLM quota exceeded, falling back to keyword matching")
            skip_keywords = ["don't have", "dont have", "donot have", "no prescription", "no bill", "skip"]
            wants_to_skip = any(keyword in last_user_msg.lower() for keyword in skip_keywords)
            if wants_to_skip:
                skip_msg = "No problem! I'll help you fill in the information manually. Let's start by gathering the details about your medication and symptoms."
                state = add_message_to_state(state, "assistant", skip_msg)
                state["current_node"] = "patient_intake"
                await save_state(state)
                return state
        except Exception as e:
            logger.error(f"Error detecting skip intent: {e}")
            # Continue to ask for document on error
    
    # Otherwise, ask for document (but make it optional)
    doc_request_msg = "To help process your report accurately, please upload a photo of your **prescription, medical bill, or medicine packaging** if you have it. If you don't have it, just let me know and I'll help you fill in the information manually."
    
    if doc_request_msg not in last_assistant_msg:
        state = add_message_to_state(state, "assistant", doc_request_msg)
    
    state["current_node"] = "awaiting_patient_doc"
    await save_state(state)
    return state


async def doctor_registry_check_node(state: NovaState) -> NovaState:
    """Check if doctor is in verified registry"""
    logger.info("Node: doctor_registry_check")
    
    try:
        phone = state.get("sender_phone")
        
        # Check registry
        doctor = await mongodb_service.check_doctor_registry(phone)
        
        if doctor and doctor.get("verified"):
            state["verified_doctor"] = True
            state["license_status"] = "approved"
            state["current_node"] = "doctor_case_intake"
        else:
            state["verified_doctor"] = False
            state["license_status"] = "pending"
            state["current_node"] = "license_upload_request"
        
        logger.info(f"Doctor verified: {state['verified_doctor']}")
        return state
        
    except Exception as e:
        logger.error(f"Error in doctor_registry_check_node: {str(e)}")
        state["verified_doctor"] = False
        return state


async def license_upload_request_node(state: NovaState) -> NovaState:
    """Request license upload from unverified doctor"""
    logger.info("Node: license_upload_request")
    
    try:
        # If they just uploaded an image (license)
        if state.get("pending_image_data"):
            # Upload to Cloudinary (as done in document_extraction)
            from app.services.cloudinary_service import cloudinary_service
            image_data = state["pending_image_data"]
            
            image_url = await cloudinary_service.upload_image(
                image_data=image_data,
                filename=f"license_{uuid.uuid4().hex[:8]}",
                folder="nova/licenses"
            )
            
            if image_url:
                state["license_status"] = "pending_verification"
                msg = "Thank you. I have received your license for verification. You may proceed with the report."
                state = add_message_to_state(state, "assistant", msg)
                state["current_node"] = "doctor_case_intake"
                # Clear pending image so it doesn't trigger other nodes
                state["pending_image_data"] = None
                return state

        # Otherwise, ask for it
        if "Please upload a photo of your medical license" not in str(state.get("messages", [])):
            # Don't send the raw prompt text! Send a nice message.
            msg = "I notice your number is not in our verified registry. To continue, please upload a clear photo of your **Medical License** for verification."
            state = add_message_to_state(state, "assistant", msg)
        
        # STAY on this node
        state["current_node"] = "license_upload_request"
        await save_state(state)
        
        return state
        
    except Exception as e:
        logger.error(f"Error in license_upload_request_node: {str(e)}")
        return state



async def document_extraction_node(state: NovaState) -> NovaState:
    """Process uploaded document image using Gemini Vision OCR"""
    logger.info("Node: document_extraction")
    
    try:
        image_data = state.get("pending_image_data")
        
        if not image_data:
            logger.warning("No image data found for extraction")
            return state
            
        # 1. Upload to Cloudinary
        from app.services.cloudinary_service import cloudinary_service
        image_url = await cloudinary_service.upload_image(
            image_data=image_data,
            filename=f"doc_{uuid.uuid4().hex[:8]}"
        )
        
        if image_url:
            attachments = state.get("attachments", [])
            attachments.append({
                "type": "document",
                "url": image_url,
                "timestamp": datetime.utcnow().isoformat()
            })
            state["attachments"] = attachments
            logger.info(f"Image uploaded to Cloudinary: {image_url}")

        # 2. Define the schema for Gemini to return structured JSON
        # Use simple types (not arrays) to avoid "unhashable type: list" error
        extraction_schema = {
            "type": "object",
            "properties": {
                "drug_name": {"type": "string"},
                "drug_dosage": {"type": "string"},
                "drug_frequency": {"type": "string"},
                "drug_route": {"type": "string"},
                "symptoms": {"type": "array", "items": {"type": "string"}},
                "indication": {"type": "string"},
                "clinic_name": {"type": "string"},
                "prescription_date": {"type": "string"}
            }
        }
        
        # Get extraction prompt
        from app.services.llm_service import gemini_service
        prompt = load_prompt("shared_prompts/document_extraction.txt")
        
        # Extract data via OCR (Gemini Vision with Strict Schema)
        extraction_json = await gemini_service.extract_from_image(
            image_data=image_data, 
            prompt=prompt,
            response_schema=extraction_schema
        )
             
        try:
            extracted_update = json.loads(extraction_json)
            
            # Merge with existing data
            current_data = state.get("extracted_data", {})
            for key, value in extracted_update.items():
                # Only update if value is not None, not empty string, and not empty list
                if value is not None and value != "" and value != []:
                    current_data[key] = value
            state["extracted_data"] = current_data
            
            # Reset pending image so we don't process it twice
            state["pending_image_data"] = None
            
            # Confirmation message
            found_fields = [k for k, v in extracted_update.items() if v]
            msg = f"I've analyzed your document and extracted details for: {', '.join(found_fields)}. Let me verify a few more details."
            state = add_message_to_state(state, "assistant", msg)
            
        except json.JSONDecodeError:
            logger.error("Failed to parse extraction JSON")
            state = add_message_to_state(state, "assistant", "I had some trouble reading that document. Could you please provide a clearer photo or type the medicine name?")

        state["current_node"] = "completeness_check"
        return state

    except Exception as e:
        logger.error(f"Error in document_extraction_node: {str(e)}")
        
        # Check if it's a rate limit/quota error
        from app.services.llm_service import RateLimitError
        if isinstance(e, RateLimitError) or "quota" in str(e).lower() or "429" in str(e):
            # Quota exceeded - allow manual entry instead
            error_msg = (
                "I'm currently experiencing high demand and cannot process images right now. "
                "No worries! I'll help you fill in the information manually. "
                "Please tell me about the medicine you took and any symptoms you're experiencing."
            )
            state = add_message_to_state(state, "assistant", error_msg)
            state["current_node"] = "patient_intake"
            # Clear pending image so we don't retry
            state["pending_image_data"] = None
        else:
            # Other error - ask for clearer photo or manual entry
            error_msg = (
                "I had some trouble reading that document. "
                "You can either try uploading a clearer photo, or just tell me the information and I'll help you fill it in manually."
            )
            state = add_message_to_state(state, "assistant", error_msg)
            state["current_node"] = "awaiting_patient_doc"
        
        await save_state(state)
        return state


async def patient_intake_node(state: NovaState) -> NovaState:
    """Collect information from patient"""
    logger.info("Node: patient_intake")
    
    try:

        extracted_data = state.get("extracted_data", {})
        missing_fields = state.get("missing_fields", settings.REQUIRED_FIELDS)
        
        # Decide which prompt to use
        # If we have some data but missing fields, use the strict follow-up prompt
        # If we have no data yet (start of convo), use the general intake prompt
        has_partial_data = any(extracted_data.values())
        
        if has_partial_data and missing_fields:
            prompt_file = "patient_workflow/prompts/followup_questions.txt"
            instruction_suffix = f"\n\nContext: You are following up with a patient. Current extracted information: {json.dumps(extracted_data)}. Missing fields: {json.dumps(missing_fields)}. Ask for the next priority missing field."
        else:
            prompt_file = "patient_workflow/prompts/patient_intake.txt"
            instruction_suffix = f"\n\nContext: Initial patient intake. Current information: {json.dumps(extracted_data)}. Your goal is to collect all required fields: {json.dumps(settings.REQUIRED_FIELDS)}."

        system_prompt = load_prompt(prompt_file)
        
        messages = state.get("messages", [])
        last_message = messages[-1]["content"] if messages else ""
        
        # We don't need formatted_prompt replacement for followup_questions.txt as it doesn't have placeholders
        # But for patient_intake.txt it does. Let's handle generic replacement safely.
        formatted_prompt = system_prompt
        if "{{EXTRACTED_DATA}}" in system_prompt:
             formatted_prompt = formatted_prompt.replace("{{EXTRACTED_DATA}}", json.dumps(extracted_data, indent=2))
        if "{{MISSING_FIELDS}}" in system_prompt:
             formatted_prompt = formatted_prompt.replace("{{MISSING_FIELDS}}", json.dumps(missing_fields, indent=2))
             
        from app.services.llm_service import RateLimitError
        
        try:
             # Combined prompt construction for Gemini
            combined_prompt = f"""{formatted_prompt}
{instruction_suffix}

User message: {last_message}

You must respond with JSON containing:
1. "response": Your conversational reply to the user (friendly, empathetic)
2. "extracted_data": Any pharmacovigilance data found in the user's message

For extracted_data, include these fields (use null if not mentioned):
- drug_name: medicine name
- drug_dosage: dosage amount
- symptoms: what they're experiencing  
- timeline: when symptoms started

Respond as NOVA with both the conversational response AND extracted data."""

            # Fix schema format - use simple types (not arrays) to avoid "unhashable type: list" error
            response_json = await gemini_service.generate_text(
                prompt=combined_prompt,
                response_schema={
                    "type": "object",
                    "properties": {
                        "response": {"type": "string"},
                        "extracted_data": {
                            "type": "object",
                            "properties": {
                                "drug_name": {"type": "string"},
                                "drug_dosage": {"type": "string"},
                                "symptoms": {"type": "array", "items": {"type": "string"}},
                                "timeline": {"type": "string"},
                                "patient_age": {"type": "string"},
                                "patient_gender": {"type": "string"}
                            }
                        }
                    },
                    "required": ["response", "extracted_data"]
                }
            )
            
            result = json.loads(response_json)
            
            # Add conversational response to state
            state = add_message_to_state(state, "assistant", result["response"])
            
            # Update extracted data
            new_data = result.get("extracted_data", {})
            current_data = state.get("extracted_data", {})
            
            for key, value in new_data.items():
                # Sanitize "null" strings
                if isinstance(value, str) and value.lower().strip() == "null":
                    value = None
                
                if value is not None:
                    # Handle different data types
                    if key == "symptoms":
                        # Symptoms should be an array
                        if isinstance(value, list):
                            # Filter out empty strings
                            symptoms_list = [s for s in value if s and str(s).strip()]
                            if symptoms_list:
                                current_data[key] = symptoms_list
                        elif isinstance(value, str) and value.strip():
                            # If LLM returns string, convert to array
                            current_data[key] = [value.strip()]
                    
                    elif key == "patient_age":
                        # Attempt to parse age as int
                        if isinstance(value, int):
                            current_data[key] = value
                        elif isinstance(value, str):
                            # Extract first number found
                            import re
                            match = re.search(r'\d+', value)
                            if match:
                                current_data[key] = int(match.group())
                            else:
                                current_data[key] = None # Invalid age format
                                
                    elif key == "patient_gender":
                        # Normalize gender
                        if isinstance(value, str):
                            val_lower = value.lower().strip()
                            if val_lower in ["male", "female", "other"]:
                                current_data[key] = val_lower
                            else:
                                current_data[key] = None # Invalid gender
                                
                    else:
                        # For other fields, check if it's a non-empty string
                        if isinstance(value, str) and value.strip():
                            current_data[key] = value.strip()
                        elif value:  # Handle other non-string types
                            current_data[key] = value
                else:
                    # Explicitly set to None if "null" was returned, to ensure missing check works
                    # Only overwrite if key doesn't exist yet? No, if LLM says null, it means null.
                    # But we prefer cumulative updates. 
                    # If we already have "Dolo" and LLM sends "drug_name": "null", should we erase?
                    # Generally, we shouldn't erase unless we are sure.
                    # But for now, let's just NOT add it if it's None.
                    pass
            
            state["extracted_data"] = current_data
            logger.info(f"Extracted data: {current_data}")
            
            state["current_node"] = "completeness_check"
            await save_state(state)
            
            return state
            
        except RateLimitError as rle:
            logger.error(f"Rate limit in patient_intake: {str(rle)}")
            error_msg = "I apologize, but I'm currently experiencing high demand. Your information has been saved. Please try again shortly."
            state = add_message_to_state(state, "assistant", error_msg)
            state["status"] = "closed"
            state["current_node"] = "end"
            return state
        
    except Exception as e:
        logger.error(f"Error in patient_intake_node: {str(e)}")
        return state


async def doctor_case_intake_node(state: NovaState) -> NovaState:
    """Collect information from doctor"""
    logger.info("Node: doctor_case_intake")
    
    try:
        # Load prompt
        system_prompt = load_prompt("doctor_workflow/prompts/doctor_intake.txt")
        
        # Get conversation history
        messages = state.get("messages", [])
        last_message = messages[-1]["content"] if messages else ""
        
        # Generate response
        from app.services.llm_service import RateLimitError
        
        try:
            response = await gemini_service.generate_text(
                prompt=f"User: {last_message}\n\nRespond as NOVA:",
                system_instruction=system_prompt
            )
            
            # Add response to state
            state = add_message_to_state(state, "assistant", response)
            
            state["current_node"] = "completeness_check"
            await save_state(state)
            
            return state
            
        except RateLimitError as rle:
            logger.error(f"Rate limit in doctor_case_intake: {str(rle)}")
            error_msg = "I apologize, but I'm currently experiencing high demand. Your case information has been saved. Please try again shortly."
            state = add_message_to_state(state, "assistant", error_msg)
            state["status"] = "closed"
            state["current_node"] = "end"
            return state
        
    except Exception as e:
        logger.error(f"Error in doctor_case_intake_node: {str(e)}")
        return state



async def doctor_handoff_node(state: NovaState) -> NovaState:
    """Hand off incomplete case to a doctor"""
    logger.info("Node: doctor_handoff")
    
    try:
        # Generate case ID if needed
        if not state.get("case_id"):
            state["case_id"] = f"CASE-{uuid.uuid4().hex[:12].upper()}"
            
        handoff_msg = (
            f"I understand. Because some details are still missing, I'd like to have a doctor review your case "
            f"to ensure we give you the best care. Your case ID is {state['case_id']}. "
            "A healthcare professional will review your report and may contact you for clarification."
        )
        
        state = add_message_to_state(state, "assistant", handoff_msg)
        state["status"] = "pending_doctor_review"
        state["current_node"] = "persist_case"  # Save the incomplete case
        
        return state
        
    except Exception as e:
        logger.error(f"Error in doctor_handoff_node: {str(e)}")
        return state


async def completeness_check_node(state: NovaState) -> NovaState:
    """Check if required fields are complete"""
    logger.info("Node: completeness_check")
    
    try:
        extracted_data = state.get("extracted_data", {})
        
        # Check required fields
        required_fields = settings.REQUIRED_FIELDS
        missing_fields = [
            field for field in required_fields 
            if not extracted_data.get(field)
        ]
        
        completeness_score = 1.0 - (len(missing_fields) / len(required_fields))
        
        state["missing_fields"] = missing_fields
        state["completeness_score"] = completeness_score
        
        # Decision Logic
        if completeness_score >= settings.COMPLETENESS_THRESHOLD:
            # Good enough -> Triage
            state["current_node"] = "clinical_triage"
        else:
            # Not enough data -> Decide whether to Loop or Handoff
            
            # Check for "I don't know" or "stop" intent in last user message
            messages = state.get("messages", [])
            last_user_msg = messages[-1]["content"].lower() if messages else ""
            
            give_up_phrases = ["i don't know", "unsure", "stop", "cancel", "idk", "skip"]
            
            if any(phrase in last_user_msg for phrase in give_up_phrases):
                # User wants to give up or doesn't know -> Handoff
                state["current_node"] = "doctor_handoff"
            else:
                # User is cooperative -> Loop back to ask more questions
                # But check for infinite loops (e.g. if we asked same thing 3 times)
                # For now, simple loop back
                if state.get("sender_type") == "doctor":
                     state["current_node"] = "doctor_case_intake"
                else:
                     state["current_node"] = "patient_intake"
        
        logger.info(f"Completeness score: {completeness_score}, Next: {state['current_node']}")
        await save_state(state)
        return state
        
    except Exception as e:
        logger.error(f"Error in completeness_check_node: {str(e)}")
        return state



async def clinical_triage_node(state: NovaState) -> NovaState:
    """Perform clinical triage using RAG to cross-reference known side effects"""
    logger.info("Node: clinical_triage")
    
    try:
        from app.services.rag_service import rag_service
        triage_prompt = load_prompt("shared_prompts/clinical_triage.txt")
        extracted_data = state.get("extracted_data", {})
        
        drug_name = extracted_data.get("drug_name")
        symptoms = extracted_data.get("symptoms", [])
        
        # 1. RAG Enrichment: Check database for matches
        rag_analysis = {}
        if drug_name:
            rag_analysis = await rag_service.check_side_effect_match(drug_name, symptoms)
            logger.info(f"RAG Analysis for {drug_name}: Found={rag_analysis.get('found_in_database')}")

        # 2. LLM Triage with RAG Context
        triage_schema = {
            "type": "object",
            "properties": {
                "classification": {"type": "string", "enum": ["known", "unusual", "severe"]},
                "reasoning": {"type": "string"}
            }
        }
        
        # Combine RAG data into the prompt
        enhanced_prompt = f"""
        User Reported Data: {json.dumps(extracted_data)}
        Medical Database (RAG) Findings: {json.dumps(rag_analysis)}
        
        Analyze if this case is a 'known' side effect, an 'unusual' one, or a 'severe' risk.
        """
        
        triage_response = await gemini_service.generate_text(
            prompt=enhanced_prompt,
            system_instruction=triage_prompt,
            response_schema=triage_schema
        )
        
        triage_data = json.loads(triage_response)
        state["triage_classification"] = triage_data.get("classification", "known")
        
        # Save RAG verification data for confidence scoring
        state["rag_verification"] = {
            "drug_verified": rag_analysis.get("found_in_database", False),
            "symptoms_matched": bool(rag_analysis.get("matched_common") or rag_analysis.get("matched_serious")),
            "match_details": rag_analysis
        }
        
        state["current_node"] = "confidence_scoring"
        return state
        
    except Exception as e:
        logger.error(f"Error in clinical_triage_node: {str(e)}")
        return state


async def confidence_scoring_node(state: NovaState) -> NovaState:
    """Calculate confidence score"""
    logger.info("Node: confidence_scoring")
    
    try:
        # Enhanced Confidence Scoring Logic (Math/Stats based)
        extracted_data = state.get("extracted_data", {})
        rag_verification = state.get("rag_verification", {})
        
        # 1. Base Score: Completeness (40%)
        # completeness_score is already calculated (0.0 to 1.0)
        base_score = state.get("completeness_score", 0.0) * 0.4
        
        # 2. Credibility Score: Source Verification (20%)
        # If doctor is verified, full points. If patient, check if contact info is provided.
        credibility_score = 0.0
        if state.get("verified_doctor"):
            credibility_score = 0.2
        elif state.get("sender_type") == "patient":
            # For patients, maybe slightly less weight, but if they gave phone/email it helps
            # For now, we give 0.1 for patients as baseline, 0.2 for Verified Doctors
            credibility_score = 0.1
            
        # 3. Validity Score: Drug Verification (20%)
        # Check if drug exists in official database
        validity_score = 0.0
        if rag_verification.get("drug_verified"):
            validity_score = 0.2
        elif extracted_data.get("drug_name"):
            # If we extracted a name but it wasn't in DB, maybe partial credit?
            # Sticking to strict verification for high confidence
            validity_score = 0.05
            
        # 4. Consistency Score: Symptom Matching (20%)
        # Check if reported symptoms match known side effects
        consistency_score = 0.0
        if rag_verification.get("symptoms_matched"):
            consistency_score = 0.2
        elif not rag_verification.get("drug_verified"):
            # If drug not known, we can't verify consistency
            consistency_score = 0.0
        
        # Calculate Total Score
        total_confidence = base_score + credibility_score + validity_score + consistency_score
        
        # Round to 2 decimal places
        state["confidence_score"] = round(min(total_confidence, 1.0), 2)
        state["current_node"] = "persist_case"
        
        logger.info(f"Confidence Scoring: Base={base_score:.2f}, Cred={credibility_score:.2f}, Valid={validity_score:.2f}, Consist={consistency_score:.2f} -> Total={state['confidence_score']}")
        return state
        
    except Exception as e:
        logger.error(f"Error in confidence_scoring_node: {str(e)}")
        return state


async def persist_case_node(state: NovaState) -> NovaState:
    """Save final case to database and mark as closed"""
    logger.info("Node: persist_case")
    
    try:
        if not state.get("case_id"):
            state["case_id"] = f"CASE-{uuid.uuid4().hex[:12].upper()}"
        
        # Mark as closed if we reached here via the completion path
        if state.get("current_node") not in ["patient_doc_request", "initial_classification"]:
            state["status"] = "closed"
            # Add a final closing message so the user knows it's done
            final_msg = f"Thank you. Your report has been successfully logged (Case ID: {state['case_id']}). Our team will review it shortly. Take care!"
            
            # Avoid ensuring duplicate final messages if retrying
            messages = state.get("messages", [])
            last_msg = messages[-1]["content"] if messages else ""
            if "successfully logged" not in last_msg:
                 state = add_message_to_state(state, "assistant", final_msg)

        case = CaseDocument(
            case_id=state["case_id"],
            sender_phone=state["sender_phone"],
            sender_type=state["sender_type"],
            language=state["language"],
            verified_doctor=state.get("verified_doctor", False),
            license_status=state.get("license_status"),
            extracted_data=ExtractedData(**state.get("extracted_data", {})),
            completeness_score=state["completeness_score"],
            confidence_score=state["confidence_score"],
            triage_classification=state.get("triage_classification"),
            messages=state.get("messages", []),
            attachments=state.get("attachments", []),
            status=state.get("status", "open")
        )
        
        await mongodb_service.save_case(case)
        logger.info(f"Persisted final case state: {state['case_id']}")
        
        # Explicitly set current_node to END to stop the graph execution cleanly (if not already handled by return)
        # However, typically we just return state. The router/graph definition handles the end.
        
        return state
        
    except Exception as e:
        logger.error(f"Error in persist_case_node: {str(e)}")
        return state


# ==================== ROUTING FUNCTIONS ====================

def route_after_user_type(state: NovaState) -> str:
    """Route to designated next step after role selection"""
    # If we're continuing an existing workflow, route to current_node
    current_node = state.get("current_node")
    if current_node and current_node not in ["initial_classification", "awaiting_user_type"]:
        # Map current_node to actual graph node names
        node_mapping = {
            "patient_doc_request": "patient_doc_request",
            "patient_intake": "patient_intake",
            "awaiting_patient_doc": "patient_doc_request",  # Still waiting for doc
            "document_extraction": "document_extraction",
            "completeness_check": "completeness_check",
            "doctor_registry_check": "doctor_registry_check",
            "license_upload_request": "license_upload_request",
            "doctor_case_intake": "doctor_case_intake",
            "clinical_triage": "clinical_triage",
            "confidence_scoring": "confidence_scoring",
            "persist_case": "persist_case"
        }
        mapped_node = node_mapping.get(current_node)
        if mapped_node:
            logger.info(f"Routing to existing workflow node: {current_node} -> {mapped_node}")
            return mapped_node
    
    # New workflow - check for pending image
    if state.get("pending_image_data"):
        return "document_extraction"

    user_type = state.get("sender_type")
    
    if user_type == "doctor":
        return "doctor_registry_check"
    elif user_type == "patient":
        # Check if we have extracted data already. If not, we MUST go to doc request.
        if not state.get("extracted_data") or not state["extracted_data"].get("drug_name"):
            return "patient_doc_request"
        return "patient_intake"
    else:
        return "awaiting_user_type"


def route_after_completeness(state: NovaState) -> Literal["clinical_triage", "patient_intake", "doctor_case_intake", "doctor_handoff", "__end__"]:
    """Route based on completeness check result"""
    node = state.get("current_node")
    
    # Map the node name set in completeness_check to the actual node name
    if node == "clinical_triage":
        return "clinical_triage"
    elif node == "doctor_handoff":
        return "doctor_handoff"
    elif node == "patient_intake":
        # We end the turn here, waiting for next user input which will route back to patient_intake
        return END
    elif node == "doctor_case_intake":
        # Same for doctor
        return END
    else:
        # Fallback
        return "clinical_triage"


def route_after_registry_check(state: NovaState) -> str:
    """Route based on doctor verification status"""
    if state.get("verified_doctor"):
        return "doctor_case_intake"
    else:
        return "license_upload_request"


# ==================== GRAPH CONSTRUCTION ====================

def create_graph() -> StateGraph:
    """Create and compile the LangGraph workflow"""
    
    # Create graph
    workflow = StateGraph(NovaState)
    
    # Add nodes
    workflow.add_node("initial_classification", initial_classification_node)
    workflow.add_node("patient_doc_request", patient_doc_request_node)
    workflow.add_node("doctor_registry_check", doctor_registry_check_node)
    workflow.add_node("license_upload_request", license_upload_request_node)
    workflow.add_node("document_extraction", document_extraction_node)
    workflow.add_node("doctor_handoff", doctor_handoff_node)
    workflow.add_node("patient_intake", patient_intake_node)
    workflow.add_node("doctor_case_intake", doctor_case_intake_node)
    workflow.add_node("completeness_check", completeness_check_node)
    workflow.add_node("clinical_triage", clinical_triage_node)
    workflow.add_node("confidence_scoring", confidence_scoring_node)
    workflow.add_node("persist_case", persist_case_node)
    
    # Set entry point
    workflow.set_entry_point("initial_classification")
    
    # Add edges
    workflow.add_conditional_edges(
        "initial_classification",
        route_after_user_type,
        {
            "patient_doc_request": "patient_doc_request",
            "patient_intake": "patient_intake",
            "doctor_registry_check": "doctor_registry_check",
            "doctor_case_intake": "doctor_case_intake",
            "document_extraction": "document_extraction",
            "completeness_check": "completeness_check",
            "clinical_triage": "clinical_triage",
            "confidence_scoring": "confidence_scoring",
            "persist_case": "persist_case",
            "awaiting_user_type": END
        }
    )
    
    def route_after_patient_doc_request(state: NovaState) -> str:
        """Route after patient doc request"""
        if state.get("pending_image_data"):
            return "document_extraction"
        elif state.get("current_node") == "patient_intake":
            return "patient_intake"
        else:
            return END
    
    workflow.add_conditional_edges(
        "patient_doc_request",
        route_after_patient_doc_request,
        {
            "document_extraction": "document_extraction",
            "patient_intake": "patient_intake",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "doctor_registry_check",
        route_after_registry_check,
        {
            "doctor_case_intake": "doctor_case_intake",
            "license_upload_request": "license_upload_request"
        }
    )
    
    workflow.add_conditional_edges(
        "license_upload_request",
        lambda x: "doctor_case_intake" if x.get("license_status") == "pending_verification" else END,
        {
            "doctor_case_intake": "doctor_case_intake",
            END: END
        }
    )
    workflow.add_edge("patient_intake", "completeness_check")
    workflow.add_edge("doctor_case_intake", "completeness_check")
    # Completeness check logic and looping
    workflow.add_conditional_edges(
        "completeness_check",
        route_after_completeness,
        {
            "clinical_triage": "clinical_triage",
            "patient_intake": END, # Loop happens on next turn
            "doctor_case_intake": END, # Loop happens on next turn
            "doctor_handoff": "doctor_handoff",
            END: END
        }
    )
    
    # New edges
    def route_after_document_extraction(state: NovaState) -> str:
        """Route after document extraction"""
        # If we set current_node to patient_intake (due to error or skip), go there
        if state.get("current_node") == "patient_intake":
            return "patient_intake"
        # Otherwise, proceed to completeness check
        return "completeness_check"
    
    workflow.add_conditional_edges(
        "document_extraction",
        route_after_document_extraction,
        {
            "patient_intake": "patient_intake",
            "completeness_check": "completeness_check"
        }
    )
    workflow.add_edge("doctor_handoff", "persist_case")
    workflow.add_edge("clinical_triage", "confidence_scoring")
    workflow.add_edge("confidence_scoring", "persist_case")
    workflow.add_edge("persist_case", END)
    
    # Compile graph
    app = workflow.compile()
    
    logger.info("LangGraph workflow compiled successfully with optimized classification")
    return app


# Global graph instance
graph_app = create_graph()
