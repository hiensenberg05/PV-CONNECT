import asyncio
import json
from app.services.llm_service import llm_service
from app.config import settings

async def test_extraction():
    print("Testing Age Extraction...")
    
    # Mock context
    user_input = "21 3 01/2026"
    extracted_data = {"drug_name": "Dollo", "drug_dosage": "600mg"}
    missing_fields = ["patient_age", "patient_gender", "symptoms"]
    
    # Replicate prompt construction from patient_intake_node
    # We don't have the file loaded, so I'll approximate the prompt structure based on the code I saw
    
    instruction_suffix = f"\n\nContext: You are following up with a patient. Current extracted information: {json.dumps(extracted_data)}. Missing fields: {json.dumps(missing_fields)}. Ask for the next priority missing field."
    
    # Simple base prompt since we can't easily load the file without the whole app context
    formatted_prompt = "You are a medical assistant collecting information." 
    
    combined_prompt = f"""{formatted_prompt}
{instruction_suffix}

User message: {user_input}

You must respond with JSON containing:
1. "response": Your conversational reply to the user (friendly, empathetic)
2. "extracted_data": Any pharmacovigilance data found in the user's message

For extracted_data, include these fields (use null if not mentioned):
- drug_name: medicine name
- drug_dosage: dosage amount
- symptoms: what they're experiencing  
- timeline: when symptoms started
- patient_age: age in years
- patient_gender: gender

Respond as NOVA with both the conversational response AND extracted data."""

    print("\nPrompting LLM...")
    try:
        response_json = await llm_service.generate_text(
            prompt=combined_prompt,
            response_schema={
                "type": "object",
                "properties": {
                    "response": {"type": "string"},
                    "extracted_data": {
                        "type": "object",
                        "properties": {
                            "patient_age": {"type": "string"},
                            "patient_gender": {"type": "string"}
                        }
                    }
                }
            }
        )
        
        print(f"\nResponse:\n{response_json}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_extraction())
