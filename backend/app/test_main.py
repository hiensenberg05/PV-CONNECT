# backend/app/test_main.py
"""
Interactive CLI for testing PV-CONNECT Workflow.
Simulates a WhatsApp user chatting with the bot.
"""

import asyncio
import uuid
import sys
import os

# Ensure backend root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.workflows.keep_workflow import process_message
from app.workflows.cache_store import get_state, clear_all_states
from app.db.mongo_db import mongodb_service


async def main():
    print("\n🏥 PV-CONNECT Workflow Tester")
    print("----------------------------")
    print("Connecting to MongoDB...")
    
    # Initialize DB connection!
    await mongodb_service.connect()
    print("✅ MongoDB Connected")

    print("\nSimulating a new WhatsApp conversation...")
    
    # Generate random phone number for this session
    phone_number = f"+9198{str(uuid.uuid4().int)[:8]}"
    print(f"User Phone: {phone_number}")
    
    # Clear previous cache for clean test
    clear_all_states()
    
    print("\nType your message below (or 'exit' to quit)")
    print("Use command 'doc <license_id>' to simulate sending a license")
    print("Use command 'img <doc_id>' to simulate sending a prescription")
    print("------------------------------------------------------------\n")

    while True:
        try:
            # Use asyncio.to_thread to make input() non-blocking mostly for Windows compatibility
            user_input = await asyncio.to_thread(input, "\nYou: ")
        except EOFError:
            break
            
        if user_input.lower() in ["exit", "quit"]:
            break
            
        # Parse inputs
        text_content = user_input
        doc_id = None
        
        # Simulate attachments
        if user_input.startswith("doc "):
            doc_id = user_input.split(" ")[1]
            text_content = None
            print(f"[System] Sending document/license: {doc_id}")
            
        elif user_input.startswith("img "):
            doc_id = user_input.split(" ")[1]
            text_content = None
            print(f"[System] Sending prescription image: {doc_id}")

        try:
            # Call Workflow
            result = await process_message(
                phone_number=phone_number,
                text_content=text_content,
                doc_id=doc_id
            )
            
            # Print Bot Reply
            reply = result["reply"]
            print(f"\nBot: {reply}")
            
            # Debug: Show State
            state = result["state"]
            if state:
                print(f"\n[Debug State]")
                print(f"Stage: {state.get('workflow_stage')}")
                if state.get("user_type"):
                    print(f"User Type: {state.get('user_type')}")
                if state.get("missing"):
                    print(f"Missing Fields: {len(state.get('missing'))}")
                if state.get("verified_doctor") is not None:
                    print(f"Verified Doctor: {state.get('verified_doctor')}")
                
                # Check for completion
                if state.get("case_complete"):
                    print("\n✅ CASE COMPLETED AND SAVED!")
                    print("Exiting test...")
                    break
                    
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

    # Cleanup
    await mongodb_service.disconnect()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
