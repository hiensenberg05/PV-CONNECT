
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.workflows.state_save import convert_state_to_case
from app.schemas.case import CaseData

def test_fix():
    print("Testing CaseData validation fix...")
    
    # Simulate state with None values for string fields
    state = {
        "case_id": "test_case_123",
        "phone_number": "1234567890",
        "user_type": "patient",
        "extracted_data": {
            "patient_name": "Test User",
            "side_effect_description": None,  # This caused the error
            "past_disease_history": None,
            "management_action_taken": None
        }
    }
    
    try:
        # This function calls CaseData(), which triggers Pydantic validation
        case = convert_state_to_case(state)
        
        print("\n✅ SUCCESS: State converted to Case without validation error.")
        print(f"Description value: '{case.data.description}' (Type: {type(case.data.description)})")
        
        if case.data.description == "":
            print("Verified: None was converted to empty string.")
        else:
            print("Warning: Description is not empty string.")
            
    except Exception as e:
        print(f"\n❌ FAILED: Validation error persists.")
        print(e)

if __name__ == "__main__":
    test_fix()
