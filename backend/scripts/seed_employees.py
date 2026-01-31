# backend/scripts/seed_employees.py
"""
Seed script to create 10 employees with bcrypt-hashed passwords.
Run with: python -m scripts.seed_employees
"""

import asyncio
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

# Default password for all employees
DEFAULT_PASSWORD = "nova2025"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


async def seed_employees():
    """Create 10 employees in the database."""
    print("🔌 Connecting to MongoDB...")
    print(f"   URI: {settings.MONGODB_URI[:40]}...")
    print(f"   Database: {settings.MONGODB_DATABASE}")
    
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DATABASE]
    
    # Hash the default password
    password_hash = hash_password(DEFAULT_PASSWORD)
    print(f"🔐 Password hash generated for: {DEFAULT_PASSWORD}")
    
    # Create 10 employees
    employees = []
    for i in range(1, 11):
        employee = {
            "employee_id": f"EMP{i:03d}",  # EMP001, EMP002, etc.
            "password_hash": password_hash,
            "name": f"Employee {i}",
            "role": "analyst",
            "active": True
        }
        employees.append(employee)
    
    # Clear existing employees and insert new ones
    print("🗑️  Clearing existing employees...")
    await db.employees.delete_many({})
    
    print("👤 Inserting 10 employees...")
    result = await db.employees.insert_many(employees)
    
    print(f"✅ Successfully created {len(result.inserted_ids)} employees!")
    print("\n📋 Employee Credentials:")
    print("-" * 40)
    for emp in employees:
        print(f"   ID: {emp['employee_id']}  |  Password: {DEFAULT_PASSWORD}")
    print("-" * 40)
    
    client.close()
    print("\n🎉 Seed complete!")


if __name__ == "__main__":
    asyncio.run(seed_employees())
