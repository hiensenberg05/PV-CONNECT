"""
Test file for Analytics Module Integration
Run this to verify all imports and basic functionality work correctly.

Usage: py test_analytics_integration.py
"""

import sys
print("=" * 60)
print("PV-CONNECT Analytics Integration Test")
print("=" * 60)

# Test 1: Basic Imports
print("\n[1/5] Testing basic imports...")
try:
    from app.analytics.scoring import VigiGradeScorer, calculate_score
    print("  ✓ scoring.py imports OK")
except Exception as e:
    print(f"  ✗ scoring.py import FAILED: {e}")
    sys.exit(1)

# Test 2: Signal Detection Imports
print("\n[2/5] Testing signal detection imports...")
try:
    from app.schemas.pv_models import DrugEventPair, CaseReport
    print("  ✓ pv_models.py imports OK")
except Exception as e:
    print(f"  ✗ pv_models.py import FAILED: {e}")
    sys.exit(1)

# Test 3: VigiGrade Router Import
print("\n[3/5] Testing vigigrade router import...")
try:
    from app.analytics.vigigrade import router as vigigrade_router
    print("  ✓ vigigrade.py router OK")
except Exception as e:
    print(f"  ✗ vigigrade.py import FAILED: {e}")
    sys.exit(1)

# Test 4: VigiGrade Scoring
print("\n[4/5] Testing VigiGrade scoring...")
try:
    scorer = VigiGradeScorer()
    
    # Test with sample case data
    sample_case = {
        "case_id": "TEST-001",
        "data": {
            "patient_details": {
                "gender": "Male",
                "age_value": 35
            },
            "medicine_details": [
                {
                    "name": "Metformin",
                    "start_date": "2026-01-01"
                }
            ],
            "reaction_details": {
                "start_date": "2026-01-15"
            },
            "severity": ["Mild"],
            "description": "Patient experienced mild nausea after taking the medication."
        }
    }
    
    result = scorer.calculate_score(sample_case)
    print(f"  ✓ VigiGrade scoring OK")
    print(f"    - Score: {result['score']}")
    print(f"    - Grade: {result['grade']}")
    print(f"    - Missing fields: {result['missing_fields']}")
except Exception as e:
    print(f"  ✗ VigiGrade scoring FAILED: {e}")
    sys.exit(1)

# Test 5: DrugEventPair Model
print("\n[5/5] Testing DrugEventPair model...")
try:
    pair = DrugEventPair(
        drug_name="Metformin",
        event_term="Nausea",
        count=5,
        prr=2.5,
        is_signal=True
    )
    print(f"  ✓ DrugEventPair model OK")
    print(f"    - Drug: {pair.drug_name}")
    print(f"    - Event: {pair.event_term}")
    print(f"    - PRR: {pair.prr}")
    print(f"    - Is Signal: {pair.is_signal}")
except Exception as e:
    print(f"  ✗ DrugEventPair model FAILED: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nThe analytics module is properly integrated.")
print("\nNext steps:")
print("  1. Run the server: py -m uvicorn app.main:app --reload")
print("  2. Test the endpoint: http://localhost:8000/api/v1/vigigrade/health")
print("=" * 60)
