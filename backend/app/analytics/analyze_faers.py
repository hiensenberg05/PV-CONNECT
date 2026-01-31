
import pandas as pd
import asyncio
import logging
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.analytics.bcpnn_engine import BCPNNEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def analyze_faers_data():
    """
    Ingest FAERS Excel data, perform BCPNN analysis, and store results in MongoDB.
    """
    try:
        file_path = 'app/analytics/faers_random_1000.xlsx'
        logger.info(f"Reading FAERS data from {file_path}")
        
        # Read Excel
        df = pd.read_excel(file_path)
        df = df.fillna('') # Replace NaNs with empty strings
        
        logger.info(f"Loaded {len(df)} rows")

        # Convert to case format expected by BCPNN
        cases = []
        
        # Group by some ID if available, otherwise treat each row as a report/case
        # FAERS data is often row-per-drug-reaction or denormalized. 
        # Assuming row-per-report or we treat each row as an event.
        # Let's inspect if there is a Case ID. The columns list didn't show one explicitly 
        # but 'primaryid' is common. If not, we treat each row as a case.
        # Based on columns seen: patient_sex, patient_age... 
        # We will treat each row as a distinct case for this purpose unless we see an ID.
        
        for index, row in df.iterrows():
            drug_name = str(row.get('drug_name', '')).strip()
            reaction = str(row.get('reaction_pt', '')).strip()
            
            if not drug_name or not reaction:
                continue

            case = {
                "case_id": f"FAERS-{index}",
                "suspect_products": [{"product_name": drug_name}],
                "adverse_events": [{"event_term": reaction}],
                # Add other useful metadata for dashboard
                "patient_sex": row.get('patient_sex'),
                "patient_age": row.get('patient_age'),
                "country": row.get('reporter_country'),
                "outcome": row.get('reaction_outcome'),
                "data_source": "FAERS"
            }
            cases.append(case)
        
        logger.info(f"Processed {len(cases)} valid cases for analysis")

        # Initialize BCPNN Engine
        # Lower min_count since dataset is small (1000 rows)
        engine = BCPNNEngine(min_count=2, ic_threshold=0.0)
        
        # Run Analysis
        results = engine.analyze_dataset(cases)
        
        # Connect to DB
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_DATABASE]
        
        # Store Raw Cases (Optional, for drill down)
        if cases:
            await db.faers_cases.delete_many({}) # Clear old
            await db.faers_cases.insert_many(cases)
            logger.info("Stored raw FAERS cases to MongoDB")

        # Store Signal Results
        signals_data = [r.to_dict() for r in results]
        
        if signals_data:
            await db.analytics_signals.delete_many({"source": "FAERS"}) # Clear old FAERS signals
            
            # Add metadata
            for s in signals_data:
                s["source"] = "FAERS"
                s["analysis_date"] = pd.Timestamp.now().isoformat()
            
            await db.analytics_signals.insert_many(signals_data)
            logger.info(f"Stored {len(signals_data)} analysis results to MongoDB")
            
        client.close()
        return len(signals_data)

    except Exception as e:
        logger.error(f"Error analyzing FAERS data: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(analyze_faers_data())
