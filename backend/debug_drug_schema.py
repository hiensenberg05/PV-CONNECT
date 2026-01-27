
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

async def check_schema():
    print(f"Connecting to DB: {db_name}")
    client = AsyncIOMotorClient(uri)
    db = client[db_name]
    
    doc = await db.drugs_database.find_one()
    print("--- SAMPLE DRUG ---")
    print(doc)
    print("-------------------")

if __name__ == "__main__":
    import sys
    sys.path.append(os.getcwd())
    asyncio.run(check_schema())
