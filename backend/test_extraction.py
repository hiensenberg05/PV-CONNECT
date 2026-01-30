"""
Quick test to verify see_useless and fill_data work correctly.
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.see_useless import see_useless_yes
from app.services.fill_data import fill_data_remove_missing

async def test_see_useless():
    print("=" * 60)
    print("Testing see_useless.py")
    print("=" * 60)
    
    test_cases = [
        ("mera naam Rahul hai", ["patient_name", "patient_age_value"], "Should be USEFUL (NO)"),
        ("25 saal ka hun", ["patient_age_value", "patient_age_unit"], "Should be USEFUL (NO)"),
        ("years", ["patient_age_unit"], "Should be USEFUL (NO)"),
        ("bhawasir ki problem thi", ["reason_for_medicine"], "Should be USEFUL (NO)"),
        ("ok", ["patient_name"], "Should be USELESS (YES)"),
        ("haan", ["patient_name"], "Should be USELESS (YES)"),
    ]
    
    for text, missing, expected in test_cases:
        result = see_useless_yes(text, missing)
        status = "✅" if (result and "YES" in expected) or (not result and "NO" in expected) else "❌"
        print(f"\n{status} Input: '{text}'")
        print(f"   Missing: {missing}")
        print(f"   Result: {'USELESS (YES)' if result else 'USEFUL (NO)'}")
        print(f"   Expected: {expected}")

async def test_fill_data():
    print("\n" + "=" * 60)
    print("Testing fill_data.py")
    print("=" * 60)
    
    test_cases = [
        {
            "text": "mera naam Rahul hai aur mai 25 saal ka hun",
            "missing": ["patient_name", "patient_age_value", "patient_age_unit", "patient_gender"],
            "expected_extractions": ["patient_name", "patient_age_value", "patient_age_unit"]
        },
        {
            "text": "male hun",
            "missing": ["patient_gender", "patient_name"],
            "expected_extractions": ["patient_gender"]
        },
    ]
    
    for test in test_cases:
        print(f"\n\nInput: '{test['text']}'")
        print(f"Missing: {test['missing']}")
        
        result = await fill_data_remove_missing(test['text'], test['missing'])
        
        print(f"Extracted: {result}")
        print(f"Expected to extract: {test['expected_extractions']}")
        
        # Check if expected fields were extracted
        for field in test['expected_extractions']:
            if field in result and result[field] is not None:
                print(f"  ✅ {field}: {result[field]}")
            else:
                print(f"  ❌ {field}: NOT EXTRACTED")

async def main():
    await test_see_useless()
    await test_fill_data()
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
