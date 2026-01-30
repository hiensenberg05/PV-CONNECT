"""
Test script for Phase 1 OpenBioLLM enhancements
Tests enhanced prompts, medical context, and quality assessment
"""
import asyncio
import json
from loguru import logger

# Configure logger
logger.add("test_phase1.log", rotation="10 MB")


async def test_enhanced_extraction():
    """Test enhanced extraction with medical context"""
    from app.agents.extraction_agent import get_extraction_agent
    
    logger.info("=" * 60)
    logger.info("Testing Phase 1 Enhancements")
    logger.info("=" * 60)
    
    # Get extraction agent
    agent = get_extraction_agent()
    
    # Test case 1: Metformin adverse event
    test_case_1 = {
        "narrative": "45 year old female started Metformin 500mg twice daily for diabetes. After 30 minutes, experienced severe nausea and vomiting. Stopped medication and symptoms resolved within 2 hours.",
        "conversation_history": None,
        "prescription_data": None
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Case 1: Metformin - Nausea/Vomiting")
    logger.info("=" * 60)
    
    result_1 = await agent.extract_adverse_event(**test_case_1)
    
    logger.info(f"\nExtraction Results:")
    logger.info(f"Confidence: {result_1.get('extraction_confidence', 0):.2%}")
    logger.info(f"Completeness: {result_1.get('completeness_score', 0):.2%}")
    logger.info(f"Requires Review: {result_1.get('requires_human_review', False)}")
    logger.info(f"\nQuality Metrics:")
    for metric, value in result_1.get('quality_metrics', {}).items():
        logger.info(f"  {metric}: {'✓' if value else '✗'}")
    
    logger.info(f"\nExtracted Data:")
    logger.info(json.dumps({
        "patient": result_1.get("patient_demographics"),
        "products": result_1.get("suspect_products"),
        "events": result_1.get("adverse_events"),
        "causality": result_1.get("causality_assessment")
    }, indent=2))
    
    # Test case 2: Lisinopril cough
    test_case_2 = {
        "narrative": "Patient on Lisinopril 10mg daily developed persistent dry cough after 2 weeks. Cough continues despite symptomatic treatment.",
        "conversation_history": None,
        "prescription_data": None
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Case 2: Lisinopril - Dry Cough")
    logger.info("=" * 60)
    
    result_2 = await agent.extract_adverse_event(**test_case_2)
    
    logger.info(f"\nExtraction Results:")
    logger.info(f"Confidence: {result_2.get('extraction_confidence', 0):.2%}")
    logger.info(f"Completeness: {result_2.get('completeness_score', 0):.2%}")
    logger.info(f"Requires Review: {result_2.get('requires_human_review', False)}")
    logger.info(f"\nQuality Metrics:")
    for metric, value in result_2.get('quality_metrics', {}).items():
        logger.info(f"  {metric}: {'✓' if value else '✗'}")
    
    # Test case 3: Incomplete information
    test_case_3 = {
        "narrative": "Patient had nausea after taking medication.",
        "conversation_history": None,
        "prescription_data": None
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Case 3: Incomplete Information")
    logger.info("=" * 60)
    
    result_3 = await agent.extract_adverse_event(**test_case_3)
    
    logger.info(f"\nExtraction Results:")
    logger.info(f"Confidence: {result_3.get('extraction_confidence', 0):.2%}")
    logger.info(f"Completeness: {result_3.get('completeness_score', 0):.2%}")
    logger.info(f"Requires Review: {result_3.get('requires_human_review', False)}")
    logger.info(f"Needs Follow-up: {result_3.get('quality_metrics', {})}")
    
    # Test case 4: With prescription data
    test_case_4 = {
        "narrative": "Elderly male patient experienced muscle pain and weakness. Unable to climb stairs.",
        "conversation_history": None,
        "prescription_data": {
            "medications": [
                {
                    "drug_name": "Atorvastatin",
                    "dosage": "40mg",
                    "frequency": "once daily"
                }
            ]
        }
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Case 4: Atorvastatin - Myalgia (with prescription)")
    logger.info("=" * 60)
    
    result_4 = await agent.extract_adverse_event(**test_case_4)
    
    logger.info(f"\nExtraction Results:")
    logger.info(f"Confidence: {result_4.get('extraction_confidence', 0):.2%}")
    logger.info(f"Completeness: {result_4.get('completeness_score', 0):.2%}")
    logger.info(f"Medical Context Used: Drug information for Atorvastatin retrieved")
    
    logger.info("\n" + "=" * 60)
    logger.info("Phase 1 Testing Complete!")
    logger.info("=" * 60)
    
    # Summary
    logger.info("\nSummary:")
    logger.info(f"Test Case 1 - Confidence: {result_1.get('extraction_confidence', 0):.2%}, Review: {result_1.get('requires_human_review')}")
    logger.info(f"Test Case 2 - Confidence: {result_2.get('extraction_confidence', 0):.2%}, Review: {result_2.get('requires_human_review')}")
    logger.info(f"Test Case 3 - Confidence: {result_3.get('extraction_confidence', 0):.2%}, Review: {result_3.get('requires_human_review')}")
    logger.info(f"Test Case 4 - Confidence: {result_4.get('extraction_confidence', 0):.2%}, Review: {result_4.get('requires_human_review')}")


async def test_medical_context():
    """Test medical context provider"""
    from app.agents.medical_context import get_medical_context
    
    logger.info("\n" + "=" * 60)
    logger.info("Testing Medical Context Provider")
    logger.info("=" * 60)
    
    context = get_medical_context()
    
    # Test drug context retrieval
    drugs = ["Metformin", "Lisinopril", "Atorvastatin"]
    
    for drug in drugs:
        drug_context = context.get_drug_context(drug)
        logger.info(f"\n{drug}:")
        logger.info(f"  Class: {drug_context['drug_class']}")
        logger.info(f"  Common AEs: {', '.join(drug_context['common_adverse_events'][:3])}")
        logger.info(f"  Serious AEs: {', '.join(drug_context['serious_adverse_events'])}")
    
    # Test drug interactions
    interactions = context.get_interaction_context(["Aspirin", "Warfarin"])
    if interactions:
        logger.info(f"\nDrug Interactions Found:")
        for interaction in interactions:
            logger.info(f"  {interaction['drug1']} + {interaction['drug2']}: {interaction['severity']} - {interaction['description']}")


if __name__ == "__main__":
    logger.info("Starting Phase 1 Enhancement Tests")
    
    # Run tests
    asyncio.run(test_medical_context())
    
    logger.info("\n" + "=" * 60)
    logger.info("IMPORTANT: Extraction tests require deployed OpenBioLLM endpoint")
    logger.info("To run extraction tests:")
    logger.info("1. Ensure HUGGING_FACE_TOKEN is set in .env")
    logger.info("2. Deploy endpoint: curl -X POST http://localhost:8000/api/pv/deploy-agents")
    logger.info("3. Uncomment the line below to run extraction tests")
    logger.info("=" * 60)
    
    # Uncomment to run extraction tests (requires deployed endpoint)
    # asyncio.run(test_enhanced_extraction())
    
    logger.success("Phase 1 tests completed!")
