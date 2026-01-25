"""
View saved pharmacovigilance cases from MongoDB
"""
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from app.services.mongodb_service import mongodb_service


async def view_all_cases():
    """View all cases in the database"""
    try:
        await mongodb_service.connect()
        
        cases = await mongodb_service.db.cases.find().to_list(100)
        
        if not cases:
            print("\n📭 No cases found in database")
            print("Run the server and test endpoints to create cases")
        else:
            print(f"\n{'='*80}")
            print(f"PHARMACOVIGILANCE CASES ({len(cases)} total)")
            print(f"{'='*80}\n")
            
            for i, case in enumerate(cases, 1):
                print(f"{i}. Case ID: {case.get('case_id', 'N/A')}")
                print(f"   Phone: {case.get('sender_phone', 'N/A')}")
                print(f"   Type: {case.get('sender_type', 'N/A')}")
                print(f"   Language: {case.get('language', 'N/A')}")
                print(f"   Status: {case.get('status', 'N/A')}")
                
                # Extracted data
                extracted = case.get('extracted_data', {})
                if extracted:
                    print(f"\n   📊 Extracted Data:")
                    if extracted.get('drug_name'):
                        print(f"      Drug: {extracted.get('drug_name')}")
                    if extracted.get('drug_dosage'):
                        print(f"      Dosage: {extracted.get('drug_dosage')}")
                    if extracted.get('symptoms'):
                        print(f"      Symptoms: {', '.join(extracted.get('symptoms', []))}")
                    if extracted.get('timeline'):
                        print(f"      Timeline: {extracted.get('timeline')}")
                
                # Scores
                print(f"\n   📈 Quality Scores:")
                print(f"      Completeness: {case.get('completeness_score', 0):.2f}")
                print(f"      Confidence: {case.get('confidence_score', 0):.2f}")
                
                # Triage
                if case.get('triage_classification'):
                    print(f"      Triage: {case.get('triage_classification')}")
                
                # Messages
                messages = case.get('messages', [])
                print(f"\n   💬 Messages: {len(messages)}")
                
                # Timestamps
                created = case.get('created_at')
                if created:
                    print(f"   🕐 Created: {created}")
                
                print(f"\n{'-'*80}\n")
        
        await mongodb_service.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def view_case_json(case_id: str):
    """View a specific case as JSON"""
    try:
        await mongodb_service.connect()
        
        case = await mongodb_service.get_case(case_id)
        
        if not case:
            print(f"❌ Case not found: {case_id}")
        else:
            # Convert ObjectId to string for JSON serialization
            if '_id' in case:
                case['_id'] = str(case['_id'])
            
            # Pretty print JSON
            print(json.dumps(case, indent=2, default=str))
        
        await mongodb_service.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def view_cases_by_phone(phone: str):
    """View all cases for a phone number"""
    try:
        await mongodb_service.connect()
        
        cases = await mongodb_service.get_cases_by_phone(phone)
        
        if not cases:
            print(f"\n📭 No cases found for {phone}")
        else:
            print(f"\n{'='*80}")
            print(f"CASES FOR {phone} ({len(cases)} total)")
            print(f"{'='*80}\n")
            
            for case in cases:
                print(f"Case ID: {case.get('case_id')}")
                print(f"Status: {case.get('status')}")
                print(f"Drug: {case.get('extracted_data', {}).get('drug_name', 'N/A')}")
                print(f"Created: {case.get('created_at')}")
                print(f"{'-'*80}\n")
        
        await mongodb_service.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            await view_all_cases()
        
        elif command == "json" and len(sys.argv) > 2:
            await view_case_json(sys.argv[2])
        
        elif command == "phone" and len(sys.argv) > 2:
            await view_cases_by_phone(sys.argv[2])
        
        else:
            print("Usage:")
            print("  python view_cases.py list                    # View all cases")
            print("  python view_cases.py json CASE-ID            # View case as JSON")
            print("  python view_cases.py phone +1234567890       # View cases by phone")
    
    else:
        # Default: list all
        await view_all_cases()


if __name__ == "__main__":
    asyncio.run(main())
