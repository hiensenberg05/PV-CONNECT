
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

try:
    from app.config import settings
    uri = settings.MONGODB_URI
    db_name = settings.MONGODB_DATABASE
except:
    uri = "mongodb+srv://admin:admin@cluster0.mongodb.net/?retryWrites=true&w=majority"
    db_name = "test"

async def check_db():
    print(f"Connecting to DB: {db_name}")
    client = AsyncIOMotorClient(uri)
    db = client[db_name]
    
    collections = await db.list_collection_names()
    print("--- COLLECTIONS ---")
    for c in collections:
        print(f"- {c}")
        # If it looks like a drug collection, print a sample
        if c.lower() in ['drug', 'drugs', 'medicine', 'medicines', 'medication', 'medications', 'compounds', 'substances']:
            print(f"  Sample from {c}:")
            sample = await db[c].find_one()
            print(f"  {sample}")
    print("-------------------")

if __name__ == "__main__":
    import sys
    sys.path.append(os.getcwd())
    asyncio.run(check_db())
