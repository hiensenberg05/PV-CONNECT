"""
Interactive VigiGrade Scoring Demo
Run this to test the scoring system with various scenarios
"""

import sys
sys.path.insert(0, '.')

from app.utils.scoring import calculate_completeness_score


def print_result(title, result):
    """Pretty print scoring results"""
    print(f"\n{'='*70}")
    print(f"📊 {title}")
    print(f"{'='*70}")
    print(f"Score: {result['score']} ({result['score_percentage']}%)")
    print(f"Category: {result['completeness_category']}")
    print(f"Well-Documented: {'✅ Yes' if result['is_well_documented'] else '❌ No'}")
    print(f"\nMissing Fields ({result['missing_fields_count']}):")
    if result['missing_fields']:
        for field in result['missing_fields'][:5]:
            print(f"  • {field}")
        if len(result['missing_fields']) > 5:
            print(f"  ... and {len(result['missing_fields']) - 5} more")
    else:
        print("  ✅ None - Perfect score!")
    
    if result['missing_critical_fields']:
        print(f"\n⚠️  Critical Missing ({len(result['missing_critical_fields'])}):")
        for field in result['missing_critical_fields']:
            print(f"  • {field}")


def test_scenario_1_perfect():
    """Scenario 1: Perfect Report - All fields present"""
    print("\n" + "🧪 TEST SCENARIO 1: PERFECT REPORT".center(70, "="))
    
    case_data = {
        "age": 45,
        "drug_name": "Metformin 500mg",
        "onset_date": "2024-01-15",
        "dosage": "500mg twice daily",
        "outcome": "Recovered",
        "symptoms": ["nausea", "vomiting", "dizziness"],
        "severity": "Moderate",
        "sex": "Male",
        "indication": "Type 2 Diabetes",
        "reporter": "Physician",
        "country": "India",
        "medical_history": "Hypertension",
    }
    
    result = calculate_completeness_score(case_data)
    print_result("Perfect Report - All Fields Present", result)
    
    assert result['score'] == 1.0, "Perfect score should be 1.0"
    assert result['completeness_category'] == "Well-Documented"
    print("\n✅ Test passed!")


def test_scenario_2_typical_whatsapp():
    """Scenario 2: Typical WhatsApp Report - Partial information"""
    print("\n" + "🧪 TEST SCENARIO 2: TYPICAL WHATSAPP REPORT".center(70, "="))
    
    case_data = {
        "drug_name": "Atorvastatin",
        "symptoms": ["muscle pain", "weakness"],
        "severity": "Moderate",
        "age": 58,
        # Missing: onset_date, dosage, outcome, sex, country, etc.
    }
    
    result = calculate_completeness_score(case_data)
    print_result("Typical WhatsApp Report - Partial Info", result)
    
    assert 0.4 < result['score'] < 0.7, "Typical incomplete score"
    assert result['completeness_category'] == "Incomplete"
    print("\n✅ Test passed!")


def test_scenario_3_minimal():
    """Scenario 3: Minimal Report - Only drug and symptom"""
    print("\n" + "🧪 TEST SCENARIO 3: MINIMAL REPORT".center(70, "="))
    
    case_data = {
        "drug_name": "Aspirin",
        "symptoms": ["headache"],
        # Missing almost everything
    }
    
    result = calculate_completeness_score(case_data)
    print_result("Minimal Report - Drug + Symptom Only", result)
    
    assert result['score'] < 0.5, "Should have low score"
    assert len(result['missing_critical_fields']) > 0
    print("\n✅ Test passed!")


def test_scenario_4_critical_missing():
    """Scenario 4: Missing Critical Fields"""
    print("\n" + "🧪 TEST SCENARIO 4: MISSING CRITICAL FIELDS".center(70, "="))
    
    case_data = {
        "drug_name": "Lisinopril 10mg",
        "symptoms": ["dry cough", "dizziness"],
        "sex": "Female",
        "country": "USA",
        "reporter": "Patient",
        # Missing: age, onset_date, dosage, outcome (all critical!)
    }
    
    result = calculate_completeness_score(case_data)
    print_result("Missing All Critical Fields", result)
    
    assert result['score'] < 0.6, "Should penalize missing critical fields heavily"
    assert "Patient Age" in result['missing_critical_fields']
    assert "Time-to-Onset" in result['missing_critical_fields']
    print("\n✅ Test passed!")


def test_scenario_5_well_documented():
    """Scenario 5: Well-Documented Report (just above threshold)"""
    print("\n" + "🧪 TEST SCENARIO 5: WELL-DOCUMENTED REPORT".center(70, "="))
    
    case_data = {
        "age": 52,
        "drug_name": "Warfarin 5mg",
        "onset_date": "2024-01-20",
        "dosage": "5mg daily",
        "outcome": "Recovering",
        "symptoms": ["minor bruising", "bleeding gums"],
        "severity": "Mild",
        "sex": "Male",
        # Missing some optional fields
    }
    
    result = calculate_completeness_score(case_data)
    print_result("Well-Documented Report", result)
    
    assert result['score'] > 0.8, "Should be above well-documented threshold"
    assert result['completeness_category'] == "Well-Documented"
    print("\n✅ Test passed!")


def test_scenario_6_empty_values():
    """Scenario 6: Empty/Null Values Handling"""
    print("\n" + "🧪 TEST SCENARIO 6: EMPTY VALUES HANDLING".center(70, "="))
    
    case_data = {
        "age": 45,
        "drug_name": "",  # Empty string
        "symptoms": [],   # Empty list
        "onset_date": None,  # None
        "country": "   ",  # Whitespace
        "indication": "unknown",  # Placeholder
        "sex": "N/A",  # Placeholder
    }
    
    result = calculate_completeness_score(case_data)
    print_result("Empty/Null Values Test", result)
    
    assert "Drug Name" in result['missing_fields']
    assert "Adverse Event" in result['missing_fields']
    assert "Time-to-Onset" in result['missing_fields']
    print("\n✅ Test passed!")


def test_scenario_7_realistic_followup():
    """Scenario 7: Realistic Case Needing Follow-up"""
    print("\n" + "🧪 TEST SCENARIO 7: CASE NEEDING FOLLOW-UP".center(70, "="))
    
    case_data = {
        "drug_name": "Metoprolol",
        "symptoms": ["fatigue", "dizziness"],
        "age": 67,
        "sex": "Female",
        # Missing: onset_date, dosage, outcome, severity
    }
    
    result = calculate_completeness_score(case_data)
    print_result("Case Needing Follow-up", result)
    
    print(f"\n💬 Follow-up Strategy:")
    print(f"   Requires follow-up: {'Yes' if result['score'] < 0.8 else 'No'}")
    if result['missing_critical_fields']:
        print(f"   Priority questions for:")
        for field in result['missing_critical_fields'][:3]:
            print(f"     • {field}")
    
    assert result['score'] < 0.8, "Should require follow-up"
    print("\n✅ Test passed!")


def run_all_tests():
    """Run all test scenarios"""
    print("\n" + "🚀 VIGIGRADE SCORING SYSTEM - COMPREHENSIVE TEST SUITE".center(70, "="))
    print("Testing completeness scoring with various real-world scenarios\n")
    
    try:
        test_scenario_1_perfect()
        test_scenario_2_typical_whatsapp()
        test_scenario_3_minimal()
        test_scenario_4_critical_missing()
        test_scenario_5_well_documented()
        test_scenario_6_empty_values()
        test_scenario_7_realistic_followup()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!".center(70))
        print("="*70)
        print("\n📊 Summary:")
        print("   • Perfect score handling: ✅")
        print("   • Typical WhatsApp cases: ✅")
        print("   • Minimal data handling: ✅")
        print("   • Critical field penalties: ✅")
        print("   • Well-documented threshold: ✅")
        print("   • Empty value detection: ✅")
        print("   • Follow-up logic: ✅")
        print("\n🎉 VigiGrade scoring system is working correctly!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
