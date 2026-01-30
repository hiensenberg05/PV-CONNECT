"""
Doctor workflow debug test
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.workflows.keep_workflow import process_message
from app.workflows.cache_store import clear_all_states, get_state
from app.db.mongo_db import mongodb_service

async def main():
    await mongodb_service.connect()
    print("Connected to MongoDB")
    
    clear_all_states()
    phone = "+919800000002"
    
    # Step 1: Send hi
    print("\n--- Step 1: Sending 'hii' ---")
    result = await process_message(phone, "hii")
    print(f"Reply: {result['reply'][:80]}...")
    print(f"Cache state: {get_state(phone)}")
    
    # Step 2: Select doctor
    print("\n--- Step 2: Sending 'doctor' ---")
    result = await process_message(phone, "doctor")
    print(f"Reply: {result['reply'][:80]}...")
    state = get_state(phone)
    print(f"Cache state exists: {state is not None}")
    if state:
        print(f"  user_type: {state.get('user_type')}")
        print(f"  verified_doctor: {state.get('verified_doctor')}")
    
    # Step 3: Send license document
    print("\n--- Step 3: Sending 'doc LICENSE123' ---")
    result = await process_message(phone, None, doc_id="LICENSE123")
    print(f"Reply: {result['reply'][:80]}...")
    state = get_state(phone)
    print(f"Cache state exists: {state is not None}")
    if state:
        print(f"  user_type: {state.get('user_type')}")
        print(f"  verified_doctor: {state.get('verified_doctor')}")
        print(f"  license_id: {state.get('license_id')}")
    
    await mongodb_service.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
