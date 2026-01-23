import asyncio
import json
import os
import sys

# Add backend directory to path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.services.mongodb_service import get_db

async def seed_data():
    print("Connecting to MongoDB...")
    db = await get_db()
    if db is None:
        print("Failed to connect to MongoDB.")
        return

    # 1. Seed Doctors
    try:
        doctor_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "doctor_registry_realistic_200_india.json")
        print(f"Reading doctors from {doctor_file_path}...")
        
        with open(doctor_file_path, "r", encoding="utf-8") as f:
            doctors = json.load(f)
            
        if doctors:
            print(f"Found {len(doctors)} doctors. Clearing old data...")
            await db.doctors.delete_many({})
            await db.doctors.insert_many(doctors)
            print(f"✅ Successfully seeded {len(doctors)} doctors.")
            
            # Create index on phone number for fast lookup
            await db.doctors.create_index("phone_number")
            print("Created index on doctors.phone_number")
            
    except Exception as e:
        print(f"❌ Error seeding doctors: {e}")

    # 2. Seed Drugs
    try:
        drug_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "drug_reference_realistic_40000.json")
        print(f"Reading drugs from {drug_file_path}...")
        
        with open(drug_file_path, "r", encoding="utf-8") as f:
            drugs = json.load(f)
            
        if drugs:
            print(f"Found {len(drugs)} drugs. Clearing old data...")
            await db.drugs_database.delete_many({})
            
            # Insert in chunks to avoid message size limits if necessary, though insert_many handles reasonably large lists
            # For 40k items, it might be safer to chunk
            chunk_size = 1000
            for i in range(0, len(drugs), chunk_size):
                chunk = drugs[i:i + chunk_size]
                await db.drugs_database.insert_many(chunk)
                print(f"Inserted chunk {i//chunk_size + 1}/{(len(drugs) + chunk_size - 1)//chunk_size}")
                
            print(f"✅ Successfully seeded {len(drugs)} drugs.")
            
            # Create text index on drug_name for search
            await db.drugs_database.create_index([("drug_name", "text"), ("generic_name", "text")])
            print("Created text index on drugs_database")
            
    except Exception as e:
        print(f"❌ Error seeding drugs: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_data())
