"""
Test script for Analytics Engine
Tests VigiGradeScorer and SignalDetector
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.analytics_engine import VigiGradeScorer, SignalDetector, AnalyticsAggregator

print("=" * 60)
print("Analytics Engine Test")
print("=" * 60)

# Test VigiGradeScorer
print("\n[TEST 1] VigiGrade Scorer")
print("-" * 40)

scorer = VigiGradeScorer()

# Complete case
complete_case = {
    "patient": {"age": 45, "sex": "Female"},
    "suspect_products": [{"product_name": "Metformin", "dose": "500mg"}],
    "adverse_events": [
        {
            "event_term": "Nausea",
            "onset_date": "2026-01-15",
            "severity": "Moderate",
            "outcome": "Recovered/Resolved"
        }
    ],
    "causality_assessment": "Probable/Likely",
    "narrative": "Patient experienced nausea 30 minutes after taking medication."
}

score = scorer.calculate_score(complete_case)
print(f"Complete case score: {score} (expected: 1.0)")

# Incomplete case
incomplete_case = {
    "patient": {"sex": "Unknown"},
    "suspect_products": [{"product_name": "Unknown Drug"}],
    "adverse_events": [{"event_term": "Headache"}],
    "narrative": "Had a headache."
}

score2 = scorer.calculate_score(incomplete_case)
missing = scorer.get_missing_fields(incomplete_case)
print(f"Incomplete case score: {score2} (expected: low)")
print(f"Missing fields: {missing}")

# Test SignalDetector
print("\n[TEST 2] Signal Detector (PRR Algorithm)")
print("-" * 40)

detector = SignalDetector(prr_threshold=2.0, min_case_count=2)

# Create test cases
test_cases = [
    # Cases with Metformin + Nausea (should show signal)
    {"suspect_products": [{"product_name": "Metformin"}], "adverse_events": [{"event_term": "Nausea"}]},
    {"suspect_products": [{"product_name": "Metformin"}], "adverse_events": [{"event_term": "Nausea"}]},
    {"suspect_products": [{"product_name": "Metformin"}], "adverse_events": [{"event_term": "Nausea"}]},
    {"suspect_products": [{"product_name": "Metformin"}], "adverse_events": [{"event_term": "Diarrhea"}]},
    
    # Cases with Lisinopril + Cough
    {"suspect_products": [{"product_name": "Lisinopril"}], "adverse_events": [{"event_term": "Cough"}]},
    {"suspect_products": [{"product_name": "Lisinopril"}], "adverse_events": [{"event_term": "Cough"}]},
    {"suspect_products": [{"product_name": "Lisinopril"}], "adverse_events": [{"event_term": "Dizziness"}]},
    
    # Other cases
    {"suspect_products": [{"product_name": "Aspirin"}], "adverse_events": [{"event_term": "Headache"}]},
    {"suspect_products": [{"product_name": "Aspirin"}], "adverse_events": [{"event_term": "Nausea"}]},
    {"suspect_products": [{"product_name": "Atorvastatin"}], "adverse_events": [{"event_term": "Myalgia"}]},
]

signals = detector.detect_signals(test_cases)
print(f"Total signals detected: {len(signals)}")
print("\nDetected Signals:")
for signal in signals:
    print(f"  {signal['drug']} + {signal['reaction']}")
    print(f"    PRR: {signal['prr_score']}, Cases: {signal['case_count']}, Status: {signal['status']}")

# Test specific pair
print("\n[TEST 3] Calculate PRR for specific pair")
print("-" * 40)

result = detector.calculate_prr_for_pair("Metformin", "Nausea", test_cases)
print(f"Metformin + Nausea:")
print(f"  PRR Score: {result['prr_score']}")
print(f"  Case Count: {result['case_count']}")
print(f"  Is Signal: {result['is_signal']}")
print(f"  Contingency Table: {result['contingency']}")

# Test AnalyticsAggregator
print("\n[TEST 4] Dashboard Aggregator")
print("-" * 40)

aggregator = AnalyticsAggregator()
dashboard = aggregator.generate_dashboard_summary(test_cases)

print(f"Total Cases: {dashboard['total_cases']}")
print(f"Average VigiGrade: {dashboard['average_vigigrade']}")
print(f"Signals Detected: {dashboard['signals_detected']}")
print(f"Quality Distribution: {dashboard['quality_distribution']}")

print("\n" + "=" * 60)
print("✅ Analytics Engine Test Complete!")
print("=" * 60)

print("\nAPI Endpoints available:")
print("  GET /api/analytics/dashboard     - Dashboard summary")
print("  GET /api/analytics/vigigrade/{case_id} - Case score")
print("  GET /api/analytics/signals       - All signals")
print("  GET /api/analytics/signals/{drug} - Drug signals")
print("  POST /api/analytics/signals/check - Check specific pair")
print("  GET /api/analytics/quality-summary - Quality metrics")
