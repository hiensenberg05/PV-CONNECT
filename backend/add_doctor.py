"""
Helper script to add doctors to the registry
Run this to add verified doctors who can skip license verification
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.mongodb_service import mongodb_service
from app.schemas.doctor_schemas import DoctorRegistry


async def add_doctor(
    phone_number: str,
    full_name: str,
    license_number: str,
    specialty: str = None,
    institution: str = None,
    country: str = "US",
    verified: bool = True
):
    """
    Add a doctor to the registry
    
    Args:
        phone_number: Doctor's phone number (e.g., "+1234567890")
        full_name: Doctor's full name
        license_number: Medical license number
        specialty: Medical specialty (optional)
        institution: Hospital/clinic name (optional)
        country: Country code (default: US)
        verified: Verification status (default: True)
    """
    try:
        # Connect to MongoDB
        await mongodb_service.connect()
        
        # Create doctor record
        doctor = DoctorRegistry(
            phone_number=phone_number,
            full_name=full_name,
            license_number=license_number,
            specialty=specialty,
            institution=institution,
            country=country,
            verified=verified,
            verification_date=datetime.utcnow() if verified else None,
            verified_by="admin" if verified else None
        )
        
        # Save to database
        success = await mongodb_service.save_doctor(doctor)
        
        if success:
            print(f"✅ Doctor added successfully!")
            print(f"   Phone: {phone_number}")
            print(f"   Name: {full_name}")
            print(f"   License: {license_number}")
            print(f"   Verified: {verified}")
        else:
            print(f"❌ Failed to add doctor")
        
        # Disconnect
        await mongodb_service.disconnect()
        
        return success
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def list_doctors():
    """List all doctors in the registry"""
    try:
        await mongodb_service.connect()
        
        cursor = mongodb_service.db.doctors.find()
        doctors = await cursor.to_list(length=100)
        
        if not doctors:
            print("No doctors in registry")
        else:
            print(f"\n{'='*70}")
            print(f"{'DOCTOR REGISTRY':<70}")
            print(f"{'='*70}")
            for i, doc in enumerate(doctors, 1):
                print(f"\n{i}. {doc.get('full_name', 'N/A')}")
                print(f"   Phone: {doc.get('phone_number', 'N/A')}")
                print(f"   License: {doc.get('license_number', 'N/A')}")
                print(f"   Specialty: {doc.get('specialty', 'N/A')}")
                print(f"   Verified: {'✅ Yes' if doc.get('verified') else '❌ No'}")
            print(f"\n{'='*70}\n")
        
        await mongodb_service.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def check_doctor(phone_number: str):
    """Check if a doctor is in the registry"""
    try:
        await mongodb_service.connect()
        
        doctor = await mongodb_service.check_doctor_registry(phone_number)
        
        if doctor:
            print(f"\n✅ Doctor found in registry:")
            print(f"   Name: {doctor.get('full_name', 'N/A')}")
            print(f"   Phone: {doctor.get('phone_number', 'N/A')}")
            print(f"   License: {doctor.get('license_number', 'N/A')}")
            print(f"   Specialty: {doctor.get('specialty', 'N/A')}")
            print(f"   Verified: {'✅ Yes' if doctor.get('verified') else '❌ No'}")
            if doctor.get('verification_date'):
                print(f"   Verified on: {doctor.get('verification_date')}")
        else:
            print(f"\n❌ Doctor not found: {phone_number}")
        
        await mongodb_service.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def main():
    """Main function with interactive menu"""
    print("\n" + "="*70)
    print("NOVA Doctor Registry Manager")
    print("="*70)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            await list_doctors()
        
        elif command == "check" and len(sys.argv) > 2:
            await check_doctor(sys.argv[2])
        
        elif command == "add" and len(sys.argv) >= 5:
            # Usage: python add_doctor.py add "+1234567890" "Dr. John Doe" "MD123456" "Cardiology" "City Hospital"
            phone = sys.argv[2]
            name = sys.argv[3]
            license = sys.argv[4]
            specialty = sys.argv[5] if len(sys.argv) > 5 else None
            institution = sys.argv[6] if len(sys.argv) > 6 else None
            
            await add_doctor(phone, name, license, specialty, institution)
        
        else:
            print("Invalid command")
            print_usage()
    
    else:
        # Interactive mode
        print("\nWhat would you like to do?")
        print("1. Add a doctor")
        print("2. List all doctors")
        print("3. Check a doctor")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            print("\n--- Add Doctor ---")
            phone = input("Phone number (e.g., +1234567890): ").strip()
            name = input("Full name: ").strip()
            license = input("License number: ").strip()
            specialty = input("Specialty (optional): ").strip() or None
            institution = input("Institution (optional): ").strip() or None
            
            await add_doctor(phone, name, license, specialty, institution)
        
        elif choice == "2":
            await list_doctors()
        
        elif choice == "3":
            phone = input("\nEnter phone number: ").strip()
            await check_doctor(phone)
        
        elif choice == "4":
            print("Goodbye!")
        
        else:
            print("Invalid choice")


def print_usage():
    """Print usage instructions"""
    print("\nUsage:")
    print("  Interactive mode:")
    print("    python add_doctor.py")
    print("\n  Command line:")
    print("    python add_doctor.py list")
    print("    python add_doctor.py check '+1234567890'")
    print("    python add_doctor.py add '+1234567890' 'Dr. John Doe' 'MD123456' 'Cardiology' 'City Hospital'")


if __name__ == "__main__":
    asyncio.run(main())
