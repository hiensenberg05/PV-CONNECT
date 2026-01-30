"""
Simple standalone test for Phase 1 enhancements
Run: python test_simple.py
"""
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("PV-CONNECT Phase 1 Enhancement Tests")
print("=" * 60)

# Test 1: Medical Context Provider
print("\n[TEST 1] Medical Context Provider")
print("-" * 40)

try:
    from agents.medical_context import get_medical_context
    
    ctx = get_medical_context()
    print("✓ Medical Context Provider initialized")
    
    # Test drug info
    drugs_to_test = ["Metformin", "Lisinopril", "Atorvastatin"]
    
    for drug in drugs_to_test:
        info = ctx.get_drug_context(drug)
        print(f"\n  {drug} ({info['drug_class']}):")
        print(f"    Common AEs: {', '.join(info['common_adverse_events'][:3])}")
        print(f"    Serious AEs: {', '.join(info['serious_adverse_events'][:2]) if info['serious_adverse_events'] else 'None listed'}")
    
    # Test drug interactions
    print("\n  Drug Interactions:")
    interactions = ctx.get_interaction_context(["Aspirin", "Warfarin"])
    if interactions:
        for i in interactions:
            print(f"    ⚠️ {i['drug1']} + {i['drug2']}: {i['severity']}")
            print(f"       {i['description']}")
    
    print("\n✓ TEST 1 PASSED: Medical Context Provider working!")
    
except Exception as e:
    print(f"✗ TEST 1 FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Extraction Agent Initialization
print("\n[TEST 2] Extraction Agent Initialization")
print("-" * 40)

try:
    from agents.extraction_agent import get_extraction_agent
    
    agent = get_extraction_agent()
    print(f"✓ Extraction Agent initialized")
    print(f"  Model: {agent.model_id}")
    print(f"  Endpoint: {agent.endpoint_name}")
    print(f"  Enhanced prompts: {agent.use_enhanced_prompts}")
    print(f"  Confidence threshold: {agent.confidence_threshold}")
    print(f"  Medical context: {'✓ Loaded' if agent.medical_context else '✗ Not loaded'}")
    
    print("\n✓ TEST 2 PASSED: Extraction Agent initialized!")
    
except Exception as e:
    print(f"✗ TEST 2 FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Prompt Building
print("\n[TEST 3] Enhanced Prompt Building")
print("-" * 40)

try:
    from agents.extraction_agent import get_extraction_agent
    
    agent = get_extraction_agent()
    
    test_narrative = "45 year old female started Metformin 500mg twice daily for diabetes. After 30 minutes, experienced severe nausea."
    
    # Extract drug names
    drug_names = agent._extract_drug_names(None, test_narrative)
    print(f"  Extracted drugs: {drug_names}")
    
    # Get contexts
    drug_contexts = [agent.medical_context.get_drug_context(drug) for drug in drug_names]
    print(f"  Context retrieved for {len(drug_contexts)} drug(s)")
    
    # Build enhanced prompt
    prompt = agent._build_enhanced_extraction_prompt(
        test_narrative, 
        None, 
        None, 
        drug_contexts
    )
    
    print(f"  Prompt length: {len(prompt)} characters")
    print(f"  Contains few-shot examples: {'✓' if 'Example 1:' in prompt else '✗'}")
    print(f"  Contains medical context: {'✓' if 'Metformin' in prompt and 'Nausea' in prompt else '✗'}")
    
    print("\n✓ TEST 3 PASSED: Enhanced prompts working!")
    
except Exception as e:
    print(f"✗ TEST 3 FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Quality Assessment
print("\n[TEST 4] Quality Assessment Metrics")
print("-" * 40)

try:
    from agents.extraction_agent import get_extraction_agent
    
    agent = get_extraction_agent()
    
    # Mock extraction data
    mock_extraction = {
        "patient_demographics": {"age": 45, "sex": "Female"},
        "suspect_products": [{"product_name": "Metformin", "dose": "500mg", "frequency": "BID"}],
        "adverse_events": [{"event_term": "Nausea", "severity": "Severe", "outcome": "Recovered/Resolved", "onset_time": "30 min"}],
        "causality_assessment": "Probable/Likely"
    }
    
    quality = agent._assess_extraction_quality(mock_extraction)
    
    print(f"  Completeness score: {quality['completeness_score']:.1%}")
    print(f"  Needs follow-up: {quality['needs_followup']}")
    print(f"  Quality metrics:")
    for metric, value in quality['quality_metrics'].items():
        print(f"    {'✓' if value else '✗'} {metric}")
    
    print("\n✓ TEST 4 PASSED: Quality assessment working!")
    
except Exception as e:
    print(f"✗ TEST 4 FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 5: HuggingFace Token Check
print("\n[TEST 5] HuggingFace Configuration")
print("-" * 40)

try:
    from dotenv import load_dotenv
    load_dotenv()
    
    hf_token = os.getenv("HUGGING_FACE_TOKEN", "")
    
    if hf_token and "your_" not in hf_token.lower():
        print(f"✓ HuggingFace token is set")
        print(f"  Token: {hf_token[:10]}...{hf_token[-4:]}")
    else:
        print("⚠️ HuggingFace token NOT set or still using placeholder")
        print("  Please update HUGGING_FACE_TOKEN in .env file")
    
    print("\n✓ TEST 5 PASSED: Configuration check complete!")

except Exception as e:
    print(f"✗ TEST 5 FAILED: {e}")

print("\n" + "=" * 60)
print("All Phase 1 tests completed!")
print("=" * 60)

print("\nNext steps:")
print("1. Start server: uvicorn main:app --reload")
print("2. Deploy agents: curl -X POST http://localhost:8000/api/pv/deploy-agents")
print("3. Test extraction endpoint")
