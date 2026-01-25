"""
Test script for NOVA LangGraph workflow
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.graph import graph_app
from app.state import create_initial_state
from app.services.mongodb_service import mongodb_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_patient_flow():
    """Test patient workflow"""
    logger.info("=" * 60)
    logger.info("TESTING PATIENT FLOW")
    logger.info("=" * 60)
    
    # Create initial state
    state = create_initial_state(
        sender_phone="+1234567890",
        initial_message="I took aspirin and got a rash"
    )
    
    # Run graph
    result = await graph_app.ainvoke(state)
    
    # Print results
    logger.info(f"\nCase ID: {result.get('case_id')}")
    logger.info(f"Language: {result.get('language')}")
    logger.info(f"Sender Type: {result.get('sender_type')}")
    logger.info(f"Completeness Score: {result.get('completeness_score')}")
    logger.info(f"Confidence Score: {result.get('confidence_score')}")
    logger.info(f"Status: {result.get('status')}")
    logger.info(f"\nMessages:")
    for msg in result.get('messages', []):
        logger.info(f"  {msg['role']}: {msg['content'][:100]}...")
    
    return result


async def test_doctor_flow():
    """Test doctor workflow"""
    logger.info("=" * 60)
    logger.info("TESTING DOCTOR FLOW")
    logger.info("=" * 60)
    
    # Create initial state
    state = create_initial_state(
        sender_phone="+1987654321",
        initial_message="Reporting ADR: Patient on metformin 500mg BID developed hypoglycemia. 65F, moderate severity."
    )
    
    # Run graph
    result = await graph_app.ainvoke(state)
    
    # Print results
    logger.info(f"\nCase ID: {result.get('case_id')}")
    logger.info(f"Language: {result.get('language')}")
    logger.info(f"Sender Type: {result.get('sender_type')}")
    logger.info(f"Verified Doctor: {result.get('verified_doctor')}")
    logger.info(f"Completeness Score: {result.get('completeness_score')}")
    logger.info(f"Confidence Score: {result.get('confidence_score')}")
    logger.info(f"Status: {result.get('status')}")
    logger.info(f"\nMessages:")
    for msg in result.get('messages', []):
        logger.info(f"  {msg['role']}: {msg['content'][:100]}...")
    
    return result


async def main():
    """Run all tests"""
    try:
        # Connect to MongoDB
        await mongodb_service.connect()
        
        # Run tests
        await test_patient_flow()
        print("\n")
        await test_doctor_flow()
        
        logger.info("\n" + "=" * 60)
        logger.info("ALL TESTS COMPLETED")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
    finally:
        # Disconnect from MongoDB
        await mongodb_service.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
