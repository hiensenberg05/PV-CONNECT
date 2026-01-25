"""
LangGraph workflow orchestration for NOVA Pharmacovigilance
"""
import uuid
import logging
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


# ==================== NODE FUNCTIONS ====================

async def initial_classification_node(state: NovaState) -> NovaState:
    """
    Combined node: Detect language AND classify user type in a SINGLE LLM call.
    Implements caching to skip classification if already done.
    """
    logger.info("Node: initial_classification")
    
    try:
        # Check if classification is already cached
        from app.state import should_skip_classification
        
        if should_skip_classification(state):
            logger.info(f"Classification cached - Language: {state['language']}, User type: {state['sender_type']}")
            state["current_node"] = f"{state['sender_type']}_workflow"
            return state
        
        # Get first user message
        first_message = state["messages"][0]["content"]
        
        # Perform combined classification (SINGLE LLM CALL)
        from app.services.llm_service import RateLimitError
        
        try:
            classification = await gemini_service.classify_initial_message(first_message)
            
            # Update state with both values
            state["language"] = classification["language"]
            state["sender_type"] = classification["user_type"]
            state["current_node"] = f"{classification['user_type']}_workflow"
            
            logger.info(f"Initial classification complete - Language: {classification['language']}, User type: {classification['user_type']}")
            return state
            
        except RateLimitError as rle:
            # Handle 429 errors gracefully
            logger.error(f"Rate limit hit during classification: {str(rle)}")
            
            # Set defaults and add error message to state
            state["language"] = settings.DEFAULT_LANGUAGE
            state["sender_type"] = "patient"
            
            error_msg = "I apologize, but I'm currently experiencing high demand. Please try again in a few moments."
            state = add_message_to_state(state, "assistant", error_msg)
            
            # Stop graph execution by setting status to closed
            state["status"] = "closed"
            state["current_node"] = "end"
            
            return state
        
    except Exception as e:
        logger.error(f"Error in initial_classification_node: {str(e)}")
        # Fallback to defaults
        state["language"] = settings.DEFAULT_LANGUAGE
        state["sender_type"] = "patient"
        state["current_node"] = "patient_workflow"
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
        # Load prompt
        prompt = load_prompt("doctor_workflow/prompts/license_request.txt")
        
        # Add message to state
        state = add_message_to_state(state, "assistant", prompt)
        
        state["current_node"] = "doctor_case_intake"
        state["next_action"] = "upload_license"
        
        return state
        
    except Exception as e:
        logger.error(f"Error in license_upload_request_node: {str(e)}")
        return state



async def document_extraction_node(state: NovaState) -> NovaState:
    """Process uploaded document image"""
    logger.info("Node: document_extraction")
    
    try:
        image_data = state.get("pending_image_data")
        image_url = state.get("pending_image_url")
        
        if not image_data and not image_url:
            logger.warning("No image data found for extraction")
            return state
            
        # Get extraction prompt
        from app.services.llm_service import gemini_service
        prompt = load_prompt("shared_prompts/document_extraction.txt")
        
        # Extract data
        # Note: In a real implementation, we would pass the image bytes or URL
        # For this node, we assume gemini_service can handle the data source
        # We'll use the 'messages' to simulate passing the image context if needed
        
        # This is a placeholder for the actual Vision API call
        # extraction = await gemini_service.extract_from_image(image_data, prompt)
        
        # Since we don't have the actual image bytes in state for this text-based flow check,
        # we will assume the main.py handler calls the service and puts the RESULT in state
        # OR we can actually implement the call if we have the bytes.
        
        # For now, let's assume the extraction happens here:
        if image_data:
             extraction_json = await gemini_service.extract_from_image(image_data, prompt)
             
             try:
                 extracted_update = json.loads(extraction_json)
                 
                 # Merge with existing data
                 current_data = state.get("extracted_data", {})
                 current_data.update(extracted_update)
                 state["extracted_data"] = current_data
                 
                 # Add system message about extraction
                 msg = f"I've analyzed your document. I found: {extracted_update.get('drug_name', 'some info')}. Let me verify a few details."
                 state = add_message_to_state(state, "assistant", msg)
                 
             except json.JSONDecodeError:
                 logger.error("Failed to parse extraction JSON")

        state["current_node"] = "completeness_check"
        return state

    except Exception as e:
        logger.error(f"Error in document_extraction_node: {str(e)}")
        return state


async def patient_intake_node(state: NovaState) -> NovaState:
    """Collect information from patient"""
    logger.info("Node: patient_intake")
    
    try:
        system_prompt = load_prompt("patient_workflow/prompts/patient_intake.txt")
        
        messages = state.get("messages", [])
        last_message = messages[-1]["content"] if messages else ""
        
        extracted_data = state.get("extracted_data", {})
        missing_fields = state.get("missing_fields", settings.REQUIRED_FIELDS)
        
        formatted_prompt = system_prompt.replace(
            "{{EXTRACTED_DATA}}", 
            json.dumps(extracted_data, indent=2)
        ).replace(
            "{{MISSING_FIELDS}}", 
            json.dumps(missing_fields, indent=2)
        )
        
        from app.services.llm_service import RateLimitError
        
        try:
            # OPTIMIZED: Single call with structured output (response + extraction)
            combined_prompt = f"""{formatted_prompt}

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

            response_json = await gemini_service.generate_text(
                prompt=combined_prompt,
                response_schema={
                    "type": "object",
                    "properties": {
                        "response": {"type": "string"},
                        "extracted_data": {
                            "type": "object",
                            "properties": {
                                "drug_name": {"type": ["string", "null"]},
                                "drug_dosage": {"type": ["string", "null"]},
                                "symptoms": {"type": ["string", "null"]},
                                "timeline": {"type": ["string", "null"]}
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
                if value and value.strip():
                    current_data[key] = value
            
            state["extracted_data"] = current_data
            logger.info(f"Extracted data: {current_data}")
            
            state["current_node"] = "completeness_check"
            
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
        return state
        
    except Exception as e:
        logger.error(f"Error in completeness_check_node: {str(e)}")
        return state



async def clinical_triage_node(state: NovaState) -> NovaState:
    """Perform clinical triage"""
    logger.info("Node: clinical_triage")
    
    try:
        # Load prompt
        triage_prompt = load_prompt("shared_prompts/clinical_triage.txt")
        
        # Get extracted data
        extracted_data = state.get("extracted_data", {})
        
        # Perform triage (simplified)
        # In production, this would use RAG for drug safety database
        state["triage_classification"] = "known"  # Placeholder
        state["current_node"] = "confidence_scoring"
        
        return state
        
    except Exception as e:
        logger.error(f"Error in clinical_triage_node: {str(e)}")
        return state


async def confidence_scoring_node(state: NovaState) -> NovaState:
    """Calculate confidence score"""
    logger.info("Node: confidence_scoring")
    
    try:
        # Simple confidence scoring based on completeness and data quality
        completeness = state.get("completeness_score", 0.0)
        has_timeline = bool(state.get("extracted_data", {}).get("timeline"))
        has_dosage = bool(state.get("extracted_data", {}).get("drug_dosage"))
        
        confidence = completeness * 0.6
        if has_timeline:
            confidence += 0.2
        if has_dosage:
            confidence += 0.2
        
        state["confidence_score"] = min(confidence, 1.0)
        state["current_node"] = "persist_case"
        
        logger.info(f"Confidence score: {state['confidence_score']}")
        return state
        
    except Exception as e:
        logger.error(f"Error in confidence_scoring_node: {str(e)}")
        return state


async def persist_case_node(state: NovaState) -> NovaState:
    """Save case to database"""
    logger.info("Node: persist_case")
    
    try:
        # Generate case ID if not exists
        if not state.get("case_id"):
            state["case_id"] = f"CASE-{uuid.uuid4().hex[:12].upper()}"
        
        # Create case document
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
            status=state.get("status", "open")
        )
        
        # Save to MongoDB
        await mongodb_service.save_case(case)
        
        state["current_node"] = "end"
        state["status"] = "closed"
        
        logger.info(f"Saved case: {state['case_id']}")
        return state
        
    except Exception as e:
        logger.error(f"Error in persist_case_node: {str(e)}")
        return state


# ==================== ROUTING FUNCTIONS ====================

def route_after_user_type(state: NovaState) -> str:
    """Route to patient or doctor workflow"""
    user_type = state.get("sender_type", "patient")
    
    if user_type == "doctor":
        return "doctor_registry_check"
    else:
        return "patient_intake"


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


# ==================== GRAPH CONSTRUCTION ====================

def create_graph() -> StateGraph:
    """Create and compile the LangGraph workflow"""
    
    # Create graph
    workflow = StateGraph(NovaState)
    
    # Add nodes
    workflow.add_node("initial_classification", initial_classification_node)  # Combined node
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
    workflow.set_entry_point("initial_classification")  # Changed from "language_detection"
    
    # Add edges
    # After initial classification, route to patient or doctor workflow
    workflow.add_conditional_edges(
        "initial_classification",  # Changed from "user_type_detection"
        route_after_user_type,
        {
            "patient_intake": "patient_intake",
            "doctor_registry_check": "doctor_registry_check"
        }
    )
    workflow.add_edge("doctor_registry_check", "doctor_case_intake")
    workflow.add_edge("license_upload_request", "doctor_case_intake")
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
    workflow.add_edge("document_extraction", "completeness_check")
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
