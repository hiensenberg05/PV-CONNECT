import asyncio
import logging
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add backend to path
sys.path.append(r"d:\nova\backend")

from app.state import create_initial_state
from app.graph import route_after_completeness, completeness_check_node

# Mock config to avoid env errors
with patch("app.config.settings.GEMINI_API_KEY", "mock_key"):
    from app.graph import graph_app, document_extraction_node

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ocr_flow():
    print("\n--- Testing OCR Flow ---")
    
    # Mock state with image data
    state = create_initial_state("+1234567890", "")
    state["pending_image_data"] = "mock_base64_data"
    state["current_node"] = "document_extraction"
    
    # Mock Gemini Service extraction
    mock_extraction_result = json.dumps({
        "drug_name": "Amoxicillin",
        "drug_dosage": "500mg",
        "doc_type": "prescription"
    })
    
    with patch("app.services.llm_service.gemini_service.extract_from_image") as mock_extract:
        mock_extract.return_value = mock_extraction_result
        
        # Run node manually
        result_state = await document_extraction_node(state)
        
        # Verify
        extracted = result_state.get("extracted_data", {})
        print(f"Extracted Data: {extracted}")
        
        assert extracted.get("drug_name") == "Amoxicillin"
        assert result_state["current_node"] == "completeness_check"
        print("✅ OCR Node Success")

async def test_loop_logic():
    print("\n--- Testing Intake Loop Logic ---")
    
    # Case 1: Incomplete data, user wants to continue
    state = create_initial_state("+1234567890", "I took medicine")
    state["extracted_data"] = {"drug_name": "Unknown"} # Missing timeline, symptoms
    state["current_node"] = "completeness_check"
    state["messages"] = [{"role": "user", "content": "I took medicine"}]
    
    # Run completeness node
    result_state = await completeness_check_node(state)
    
    # Check router decision
    next_node = route_after_completeness(result_state)
    print(f"Missing: {result_state.get('missing_fields')}")
    print(f"Completeness Score: {result_state.get('completeness_score')}")
    print(f"Next Node: {next_node}")
    
    assert next_node == "__end__"
    print("✅ Loop Back Success (Terminated turn safely)")

async def test_doctor_handoff():
    print("\n--- Testing Doctor Handoff Logic ---")
    
    # Case 2: Incomplete data, user says "I don't know"
    state = create_initial_state("+1234567890", "I don't know the name")
    state["extracted_data"] = {"symptoms": "headache"} 
    state["current_node"] = "completeness_check"
    state["messages"] = [{"role": "user", "content": "I don't know what it was called"}]
    
    # Run completeness node
    result_state = await completeness_check_node(state)
    next_node = route_after_completeness(result_state)
    
    print(f"User Message: {state['messages'][0]['content']}")
    print(f"Next Node: {next_node}")
    
    assert next_node == "doctor_handoff"
    print("✅ Doctor Handoff Success")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_ocr_flow())
    loop.run_until_complete(test_loop_logic())
    loop.run_until_complete(test_doctor_handoff())
    print("\n🎉 All Tests Passed!")
