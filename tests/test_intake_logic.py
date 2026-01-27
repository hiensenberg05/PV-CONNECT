
import asyncio
import sys
import os
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.join(os.getcwd(), "backend"))
load_dotenv(os.path.join(os.getcwd(), "backend", ".env"))

from app.state import NovaState
from app.graph import completeness_check_node

async def test_completeness_logic():
    print("\n--- Testing Completeness & Looping Logic ---")
    
    # Scenario 1: User provided Drug only (Missing Age, Gender, Timeline)
    state_partial = {
        "extracted_data": {
            "drug_name": "Dolo 650",
            "patient_age": None, # Missing
            "patient_gender": None, # Missing
            "symptoms": ["Headache"],
            "timeline": "Yesterday"
        },
        "sender_type": "patient",
        "messages": [{"role": "user", "content": "I took Dolo"}]
    }
    
    print("\nScenario 1: Partial Data (Missing Age/Gender)")
    result_1 = await completeness_check_node(state_partial)
    
    score_1 = result_1.get("completeness_score", 0.0)
    next_node_1 = result_1.get("current_node")
    missing_1 = result_1.get("missing_fields", [])
    
    print(f"Score: {score_1}")
    print(f"Missing Fields: {missing_1}")
    print(f"Next Node: {next_node_1}")
    
    if "patient_age" in missing_1 and next_node_1 == "patient_intake":
        print("✅ SUCCESS: System detected missing Age and looped back to Intake.")
    else:
        print("❌ FAILURE: Logic did not loop back correctly.")

    # Scenario 2: All Data provided
    state_complete = {
        "extracted_data": {
            "drug_name": "Dolo 650",
            "patient_age": "25 years",
            "patient_gender": "Male",
            "symptoms": ["Rashes"],
            "timeline": "2 days ago"
        },
        "sender_type": "patient",
        "messages": [{"role": "user", "content": "Here is all info"}]
    }
    
    print("\nScenario 2: Complete Data")
    result_2 = await completeness_check_node(state_complete)
    
    next_node_2 = result_2.get("current_node")
    
    print(f"Next Node: {next_node_2}")
    
    if next_node_2 == "clinical_triage":
         print("✅ SUCCESS: System detected completeness and moved to Triage.")
    else:
         print(f"❌ FAILURE: Expected 'clinical_triage' but got '{next_node_2}'")

if __name__ == "__main__":
    asyncio.run(test_completeness_logic())
