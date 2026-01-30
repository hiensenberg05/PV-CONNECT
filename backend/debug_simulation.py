
import asyncio
import json
from app.workflows.keep_workflow import create_initial_state, process_message, set_state, get_state, delete_state

# Simulate the user's conversation
CONVERSATION_FLOW = [
    "1",
    "mere pas nahi hai",
    "uttkarsh solanki",
    "male",
    "23 years",
    "i was having backpain",
    "my doctor",
    "ibrufen 500mg pain killer",
    "tablet", 
    "not talking it today",
    "i took it for last 2 days"
]

async def run_simulation():
    phone_number = "+919999999999"
    
    # 1. Clean start
    delete_state(phone_number)
    state = create_initial_state(phone_number, "patient")
    set_state(phone_number, state)
    
    print(f"--- STARTING SIMULATION ({len(CONVERSATION_FLOW)} turns) ---")
    
    for i, user_input in enumerate(CONVERSATION_FLOW):
        print(f"\n\n[TURN {i+1}] User: {user_input}")
        
        # Process message
        # FIXED ARGUMENT ORDER: process_message(phone_number, text_content=...)
        result = await process_message(phone_number, text_content=user_input)
        current_state = result["state"]
        
        extracted = current_state.get("extracted_data", {})
        missing = current_state.get("missing", [])
        
        print(f"Bot: {result['reply']}")
        print(f"--- STATE CHECK ---")
        print(f"EXTRACTED ({len(extracted)}): {json.dumps(extracted, indent=2)}")
        print(f"MISSING ({len(missing)}): {missing}")
        
        # Specific check for medicine_name
        if "ibrufen" in user_input.lower():
            if "medicine_name" not in extracted:
                print("!!! WARNING: 'medicine_name' WAS MISSED HERE !!!")
            else:
                print(f"SUCCESS: medicine_name = {extracted['medicine_name']}")

if __name__ == "__main__":
    asyncio.run(run_simulation())
