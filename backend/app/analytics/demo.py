"""
VigiGrade Example Usage Script

This script demonstrates all major features of the VigiGrade system.
"""

import asyncio
import logging
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from app.services.scoring import (
    VigiGradeScorer,
    calculate_score,
    update_case_score,
    batch_update_scores
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Sample case data
SAMPLE_CASES = [
    {
        "case_id": "CASE-EXAMPLE-001",
        "data": {
            "patient_details": {
                "name": "Rahul Kumar",
                "gender": "Male",
                "age_value": 25,
                "age_unit": "years"
            },
            "medicine_details": [
                {
                    "name": "Paracetamol",
                    "quantity_taken": "500mg",
                    "start_date": "2024-01-15"
                }
            ],
            "reaction_details": {
                "start_date": "2024-01-16",
                "continuing": True
            },
            "severity": ["Hospitalized"],
            "description": "Patient developed severe allergic reaction 24 hours after taking medication."
        }
    },
    {
        "case_id": "CASE-EXAMPLE-002",
        "data": {
            "patient_details": {
                "name": "Priya Sharma",
                "gender": "Female",
                # age_value missing - will be penalized
            },
            "medicine_details": [
                {
                    "name": "Aspirin",
                    # start_date missing - will be penalized
                }
            ],
            "reaction_details": {
                "start_date": "2024-01-20"
            },
            "severity": ["Mild"],
            "description": "Patient reported mild headache and nausea."
        }
    },
    {
        "case_id": "CASE-EXAMPLE-003",
        "data": {
            "patient_details": {},
            "medicine_details": [],  # Empty - will be penalized
            "reaction_details": {},  # No start_date - will be penalized
            "severity": [],
            "description": "Minimal information available."
        }
    }
]


async def example_1_basic_scoring():
    """
    Example 1: Basic score calculation without database
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Score Calculation")
    print("="*60)
    
    scorer = VigiGradeScorer()
    
    for case in SAMPLE_CASES:
        result = scorer.calculate_score(case)
        
        print(f"\nCase ID: {case['case_id']}")
        print(f"Score: {result['score']:.2f}")
        print(f"Grade: {result['grade']}")
        print(f"Missing Fields: {', '.join(result['missing_fields']) if result['missing_fields'] else 'None'}")
        
        if result['penalty_breakdown']:
            print(f"Penalty Breakdown:")
            for section, penalty in result['penalty_breakdown'].items():
                print(f"  - {section}: -{penalty}")


async def example_2_async_scoring():
    """
    Example 2: Using async wrapper function
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Async Score Calculation")
    print("="*60)
    
    for case in SAMPLE_CASES[:1]:  # Just first case
        result = await calculate_score(case)
        
        print(f"\nCase ID: {case['case_id']}")
        print(f"Async Score Result: {result['score']:.2f} ({result['grade']})")


async def example_3_database_operations():
    """
    Example 3: Database operations - insert and update scores
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Database Operations")
    print("="*60)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.pharmacovigilance_demo
    
    try:
        # Clear any existing demo data
        await db.cases.delete_many({"case_id": {"$regex": "^CASE-EXAMPLE-"}})
        
        # Insert sample cases
        print("\nInserting sample cases...")
        await db.cases.insert_many(SAMPLE_CASES)
        print(f"Inserted {len(SAMPLE_CASES)} cases")
        
        # Update scores for each case
        print("\nUpdating scores...")
        for case in SAMPLE_CASES:
            result = await update_case_score(case["case_id"], db)
            
            if result:
                print(f"\n✓ {case['case_id']}: {result['score']:.2f} ({result['grade']})")
            else:
                print(f"\n✗ {case['case_id']}: Update failed")
        
        # Retrieve and display updated documents
        print("\n\nUpdated Documents:")
        async for doc in db.cases.find({"case_id": {"$regex": "^CASE-EXAMPLE-"}}):
            print(f"\nCase: {doc['case_id']}")
            print(f"  Confidence Score: {doc.get('confidence_score', 'N/A')}")
            print(f"  Quality Report: {doc.get('data_quality_report', {})}")
    
    finally:
        client.close()


async def example_4_batch_processing():
    """
    Example 4: Batch score updates
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Batch Processing")
    print("="*60)
    
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.pharmacovigilance_demo
    
    try:
        # Ensure sample data exists
        existing_count = await db.cases.count_documents(
            {"case_id": {"$regex": "^CASE-EXAMPLE-"}}
        )
        
        if existing_count == 0:
            await db.cases.insert_many(SAMPLE_CASES)
            print(f"Inserted {len(SAMPLE_CASES)} sample cases")
        
        # Run batch update
        print("\nRunning batch update...")
        case_ids = [case["case_id"] for case in SAMPLE_CASES]
        summary = await batch_update_scores(db, case_ids)
        
        print(f"\nBatch Update Summary:")
        print(f"  Total Processed: {summary['total_processed']}")
        print(f"  Successful: {summary['successful']}")
        print(f"  Failed: {summary['failed']}")
        
        if summary['errors']:
            print(f"\nErrors:")
            for error in summary['errors']:
                print(f"  - {error['case_id']}: {error['error']}")
    
    finally:
        client.close()


async def example_5_quality_statistics():
    """
    Example 5: Analyze quality statistics
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Quality Statistics")
    print("="*60)
    
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.pharmacovigilance_demo
    
    try:
        # Aggregate statistics
        pipeline = [
            {
                "$match": {
                    "confidence_score": {"$exists": True}
                }
            },
            {
                "$group": {
                    "_id": "$data_quality_report.grade",
                    "count": {"$sum": 1},
                    "avg_score": {"$avg": "$confidence_score"},
                    "min_score": {"$min": "$confidence_score"},
                    "max_score": {"$max": "$confidence_score"}
                }
            },
            {
                "$sort": {"avg_score": -1}
            }
        ]
        
        results = await db.cases.aggregate(pipeline).to_list(length=None)
        
        total_cases = sum(r["count"] for r in results)
        
        print(f"\nTotal Cases Scored: {total_cases}")
        print("\nDistribution by Grade:")
        print(f"{'Grade':<15} {'Count':<10} {'Percentage':<15} {'Avg Score':<15} {'Range'}")
        print("-" * 70)
        
        for result in results:
            grade = result["_id"]
            count = result["count"]
            percentage = (count / total_cases * 100) if total_cases > 0 else 0
            avg_score = result["avg_score"]
            min_score = result["min_score"]
            max_score = result["max_score"]
            
            print(
                f"{grade:<15} {count:<10} {percentage:>6.1f}%        "
                f"{avg_score:>6.2f}          {min_score:.2f} - {max_score:.2f}"
            )
    
    finally:
        client.close()


async def example_6_custom_penalties():
    """
    Example 6: Customize penalty weights
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Custom Penalty Configuration")
    print("="*60)
    
    # Create scorer with default penalties
    default_scorer = VigiGradeScorer()
    
    # Create scorer with custom penalties
    custom_scorer = VigiGradeScorer()
    custom_scorer.PENALTIES["reaction_start_date"] = 0.30  # Increase importance
    custom_scorer.PENALTIES["patient_gender"] = 0.02  # Decrease importance
    
    # Test case with missing reaction date and gender
    test_case = {
        "case_id": "CASE-CUSTOM-TEST",
        "data": {
            "patient_details": {
                "age_value": 30
                # gender missing
            },
            "medicine_details": [
                {
                    "name": "TestDrug",
                    "start_date": "2024-01-01"
                }
            ],
            "reaction_details": {
                # start_date missing
            },
            "severity": ["Mild"],
            "description": "Test case for custom penalties."
        }
    }
    
    default_result = default_scorer.calculate_score(test_case)
    custom_result = custom_scorer.calculate_score(test_case)
    
    print("\nDefault Penalties:")
    print(f"  Score: {default_result['score']:.2f}")
    print(f"  Breakdown: {default_result['penalty_breakdown']}")
    
    print("\nCustom Penalties:")
    print(f"  Score: {custom_result['score']:.2f}")
    print(f"  Breakdown: {custom_result['penalty_breakdown']}")
    
    print("\nDifference:")
    print(f"  Score Change: {custom_result['score'] - default_result['score']:+.2f}")


async def example_7_edge_cases():
    """
    Example 7: Handling edge cases
    """
    print("\n" + "="*60)
    print("EXAMPLE 7: Edge Cases and Error Handling")
    print("="*60)
    
    scorer = VigiGradeScorer()
    
    edge_cases = [
        {
            "name": "Completely Empty Data",
            "case": {
                "case_id": "EDGE-001",
                "data": {}
            }
        },
        {
            "name": "Missing Data Section",
            "case": {
                "case_id": "EDGE-002"
            }
        },
        {
            "name": "Unknown Values",
            "case": {
                "case_id": "EDGE-003",
                "data": {
                    "patient_details": {
                        "gender": "Unknown",
                        "age_value": "Unknown"
                    },
                    "medicine_details": [],
                    "reaction_details": {
                        "start_date": "Unknown"
                    },
                    "severity": [],
                    "description": "Unknown"
                }
            }
        },
        {
            "name": "Whitespace Only",
            "case": {
                "case_id": "EDGE-004",
                "data": {
                    "patient_details": {
                        "gender": "   ",
                        "age_value": 25
                    },
                    "medicine_details": [
                        {"name": "Drug", "start_date": "2024-01-01"}
                    ],
                    "reaction_details": {
                        "start_date": "2024-01-02"
                    },
                    "severity": ["Mild"],
                    "description": "     "
                }
            }
        }
    ]
    
    for edge_case in edge_cases:
        print(f"\n{edge_case['name']}:")
        try:
            result = scorer.calculate_score(edge_case['case'])
            print(f"  ✓ Handled successfully")
            print(f"  Score: {result['score']:.2f}, Grade: {result['grade']}")
            print(f"  Missing: {len(result['missing_fields'])} fields")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")


async def main():
    """Run all examples"""
    print("\n")
    print("="*60)
    print("    VigiGrade Confidence Scoring Engine - Examples")
    print("="*60)
    
    try:
        # Run all examples
        await example_1_basic_scoring()
        await example_2_async_scoring()
        await example_3_database_operations()
        await example_4_batch_processing()
        await example_5_quality_statistics()
        await example_6_custom_penalties()
        await example_7_edge_cases()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Example execution failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
