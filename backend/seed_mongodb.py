"""
Seed MongoDB with local JSON reference data.

This script loads:
- doctor_registry_realistic_200_india.json  ->  doctors collection
- drug_reference_realistic_40000.json       ->  drugs_database collection

It uses the same MONGODB_URI and MONGODB_DATABASE that the app uses
via app.config, so make sure your .env is configured first.

Run from the backend directory:

    cd backend
    python seed_mongodb.py
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import MONGODB_URI, MONGODB_DATABASE


ROOT_DIR = Path(__file__).resolve().parent.parent
DOCTORS_FILE = ROOT_DIR / "doctor_registry_realistic_200_india.json"
DRUGS_FILE = ROOT_DIR / "drug_reference_realistic_40000.json"


async def seed_doctors(client: AsyncIOMotorClient) -> None:
    """Seed doctors collection from doctor_registry_realistic_200_india.json"""
    if not DOCTORS_FILE.exists():
        print(f"[doctors] File not found: {DOCTORS_FILE}")
        return

    db = client[MONGODB_DATABASE]
    collection = db.doctors

    with DOCTORS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("[doctors] Expected a JSON array at top level; nothing seeded.")
        return

    # Optional: clear existing docs
    await collection.delete_many({})

    # Insert in batches to avoid memory spikes (though 200 docs is small)
    batch_size = 100
    total = 0
    for i in range(0, len(data), batch_size):
        batch: List[Dict[str, Any]] = data[i : i + batch_size]
        if batch:
            result = await collection.insert_many(batch)
            total += len(result.inserted_ids)

    print(f"[doctors] Seeded {total} documents into 'doctors' collection.")


async def seed_drugs(client: AsyncIOMotorClient) -> None:
    """Seed drugs_database collection from drug_reference_realistic_40000.json"""
    if not DRUGS_FILE.exists():
        print(f"[drugs] File not found: {DRUGS_FILE}")
        return

    db = client[MONGODB_DATABASE]
    collection = db.drugs_database

    # This file is a single-line JSON array; load it in one go
    with DRUGS_FILE.open("r", encoding="utf-8") as f:
        content = f.read()
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"[drugs] Failed to parse JSON: {e}")
            return

    if not isinstance(data, list):
        print("[drugs] Expected a JSON array at top level; nothing seeded.")
        return

    # Optional: clear existing docs
    await collection.delete_many({})

    batch_size = 1000
    total = 0
    for i in range(0, len(data), batch_size):
        batch: List[Dict[str, Any]] = data[i : i + batch_size]
        if batch:
            result = await collection.insert_many(batch)
            total += len(result.inserted_ids)

    print(f"[drugs] Seeded {total} documents into 'drugs_database' collection.")


async def main() -> None:
    print(f"Connecting to MongoDB at {MONGODB_URI}, database '{MONGODB_DATABASE}'")
    client = AsyncIOMotorClient(MONGODB_URI)

    try:
        await seed_doctors(client)
        await seed_drugs(client)
        print("Seeding complete.")
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())

