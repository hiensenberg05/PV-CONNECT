import asyncio
import sys
import os
from uuid import uuid4

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.db.mongo_db import mongodb_service
from app.schemas.case import Case

async def test_mongo_connection():
    print("🔌 CONNECTING TO MONGODB...")
    try:
        await mongodb_service.connect()
        print("✅ CONNECTED.")
        
        # Create Dummy Case
        dummy_case = Case(
            case_id=uuid4(),
            patient_phone="1234567890",
            reporter_type="patient",
            data={"note": "This is a connection test"},
            is_complete=True
        )
        
        print(f"💾 SAVING TEST CASE: {dummy_case.case_id}")
        doc_id = await mongodb_service.save_case(dummy_case)
        print(f"✅ SAVED. Doc ID: {doc_id}")
        
        # Retrieve
        print(f"🔍 RETRIEVING CASE: {doc_id}")
        retrieved = await mongodb_service.get_case(dummy_case.case_id)
        if retrieved:
            print(f"✅ FOUND: {retrieved.get('case_id')}")
            print(f"   Data: {retrieved.get('data')}")
        else:
            print("❌ RETRIEVAL FAILED.")
            
        await mongodb_service.disconnect()
        print("✅ DISCONNECTED.")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mongo_connection())
