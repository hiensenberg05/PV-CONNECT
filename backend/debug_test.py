"""
Quick debug to capture exact error in pv_followup_agent
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.workflows.keep_workflow import process_message
from app.workflows.cache_store import clear_all_states
from app.db.mongo_db import mongodb_service

async def main():
    # Connect to DB
    await mongodb_service.connect()
    print("Connected to MongoDB")
    
    # Clear cache for fresh start
    clear_all_states()
    
    phone = "+919800000001"
    
    # Step 1: Send hi
    print("\n--- Step 1: Sending 'hii' ---")
    result = await process_message(phone, "hii")
    print(f"Reply: {result['reply'][:100]}...")
    
    # Step 2: Select patient (1)
    print("\n--- Step 2: Sending '1' (patient) ---")
    try:
        result = await process_message(phone, "1")
        print(f"Reply: {result['reply'][:100]}...")
        print(f"Stage: {result['state'].get('workflow_stage')}")
        print(f"User Type: {result['state'].get('user_type')}")
    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()
    
    await mongodb_service.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
