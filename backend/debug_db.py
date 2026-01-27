
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Use hardcoded URI if env var not set, or try to load from config
# Assuming config.py has the URI, let's try to import it or just use the likely default if not found
try:
    from app.config import settings
    uri = settings.MONGODB_URI
    db_name = settings.MONGODB_DATABASE
except:
    uri = "mongodb+srv://admin:admin@cluster0.mongodb.net/?retryWrites=true&w=majority" # Placeholder/Fallback
    # Actually, I should check config.py content again to get the URI or how it's loaded.
    # But since I can't easily see the .env file content (security), I'll rely on app.config.

async def check_db():
    print(f"Connecting to {uri}...")
    client = AsyncIOMotorClient(uri)
    db = client[db_name]
    
    collections = await db.list_collection_names()
    print(f"Collections: {collections}")
    
    if "doctors" in collections:
        doc = await db.doctors.find_one()
        print("\nDoctor Sample:", doc)
        
    if "drugs" in collections:
        drug = await db.drugs.find_one()
        print("\nDrug Sample:", drug)
    elif "medicines" in collections:
         drug = await db.medicines.find_one()
         print("\nMedicine Sample:", drug)
    else:
        print("\nNo drugs/medicines collection found.")

if __name__ == "__main__":
    # We need to make sure we can import app.config
    # Add parent dir to path
    import sys
    sys.path.append(os.getcwd())
    asyncio.run(check_db())
