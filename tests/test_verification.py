
import asyncio
import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), "backend", ".env"))

# Add project root to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.state import NovaState
from app.graph import confidence_scoring_node, clinical_triage_node, patient_intake_node
from app.services.llm_service import gemini_service
from app.services.mongodb_service import mongodb_service
from app.services.rag_service import rag_service

# Mock services to avoid real API calls for unit testing logic where possible
# But here we want to verifying the INTEGRATION with RAG and Confidence

async def test_confidence_scoring():
    print("\n--- Testing Confidence Scoring ---")
    
    # 1. Test High Confidence Case
    state_high = {
        "case_id": "TEST-HIGH",
        "sender_type": "doctor",
        "verified_doctor": True,
        "completeness_score": 1.0, # Base = 0.4
        "rag_verification": {
            "drug_verified": True, # +0.2
            "symptoms_matched": True # +0.2
        },
        "extracted_data": {"drug_name": "Panmed-0"}
    }
    
    # Expected: 0.4 + 0.2 + 0.2 + 0.2 = 1.0
    result_high = await confidence_scoring_node(state_high)
    print(f"High Confidence Score: {result_high['confidence_score']} (Expected ~1.0)")
    
    # 2. Test Low Confidence Case
    state_low = {
        "case_id": "TEST-LOW",
        "sender_type": "patient",
        "verified_doctor": False, # +0.1 (patient)
        "completeness_score": 0.5, # Base = 0.2
        "rag_verification": {
            "drug_verified": False, # 0
            "symptoms_matched": False # 0
        },
        "extracted_data": {"drug_name": "UnknownDrug"}
    }
    # Expected: 0.2 + 0.1 + 0.05 (maybe) + 0 = 0.35
    result_low = await confidence_scoring_node(state_low)
    print(f"Low Confidence Score: {result_low['confidence_score']} (Expected ~0.3)")

async def test_rag_integration():
    print("\n--- Testing RAG Integration (Real MongoDB) ---")
    # Verify we can find "Panmed-0" as seen in debug output
    drug_name = "Panmed-0"
    symptoms = ["nausea", "dizziness"] # These are in the "known_side_effects" from debug output
    
    analysis = await rag_service.check_side_effect_match(drug_name, symptoms)
    print("RAG Analysis Result:", json.dumps(analysis, indent=2))
    
    if analysis["found_in_database"] and len(analysis["matched_common"]) > 0:
        print("SUCCESS: RAG found drug and matched symptoms.")
    else:
        print("FAILURE: RAG did not find drug or match symptoms.")

async def test_followup_prompt_selection():
    print("\n--- Testing Follow-up Prompt Selection ---")
    
    # Simulate state where we have partial data (drug known) but missing timeline
    state = {
        "messages": [{"role": "user", "content": "I took Panmed-0"}],
        "extracted_data": {"drug_name": "Panmed-0"},
        "missing_fields": ["timeline", "symptoms"], # Timeline is missing
        "sender_type": "patient"
    }
    
    # We expect patient_intake_node to use followup_questions.txt
    # and generated response should likely ask for symptoms or timeline with specific format
    # Since we can't easily mock the LLM response content without mocking the service,
    # we will rely on the fact that the node runs without error and we can inspect the logs if needed.
    # However, to properly verify, we should check if the SYSTEM prompt loaded is the correct one.
    # The current graph.py implementation loads the file contents.
    
    # Let's run the node
    result_state = await patient_intake_node(state)
    
    response = result_state["messages"][-1]["content"]
    print(f"Bot Response: {response}")
    
    # We can't strictly assert the content without a real LLM call (which we have enabled via dotenv)
    # If the LLM follows instructions, it should ask for "Describe the side effect" or date in "DD/MM/YYYY"
    
    if "DD/MM/YYYY" in response or "Describe the side effect" in response or "Medicine name" in response:
        print("SUCCESS: Bot used PvPI phrasing.")
    else:
        print("WARNING: Bot response might not have used strict PvPI phrasing. Check logs/implementation.")

if __name__ == "__main__":
    asyncio.run(test_rag_integration())
    asyncio.run(test_confidence_scoring())
    asyncio.run(test_followup_prompt_selection())
