"""
RAG Service for Drug Safety Database
(Placeholder - to be implemented with actual drug database)
"""
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class RAGService:
    """Service for retrieving drug safety information"""
    
    def __init__(self):
        """Initialize RAG service"""
        # We now use the shared mongodb_service
        logger.info("Initialized RAG service (MongoDB Connected)")
    
    async def get_drug_side_effects(
        self, 
        drug_name: str
    ) -> Optional[Dict[str, List[str]]]:
        """
        Get known side effects for a drug from MongoDB
        
        Args:
            drug_name: Name of the drug
            
        Returns:
            Dictionary with side effects info
        """
        try:
            from app.services.mongodb_service import mongodb_service
            
            if mongodb_service.db is None:
                await mongodb_service.connect()
            
            # Case-insensitive regex search
            regex_pattern = {"$regex": f"^{drug_name}$", "$options": "i"}
            
            # Try searching by drug_name or generic_name
            query = {
                "$or": [
                    {"drug_name": regex_pattern},
                    {"generic_name": regex_pattern}
                ]
            }
            
            drug_doc = await mongodb_service.db.drugs_database.find_one(query)
            
            if drug_doc:
                # Normalize schema to expected format
                # The DB has 'known_side_effects' (array)
                return {
                    "drug_name": drug_doc.get("drug_name"),
                    "generic_name": drug_doc.get("generic_name"),
                    "common_side_effects": drug_doc.get("known_side_effects", []),
                    "serious_side_effects": drug_doc.get("serious_side_effects", []) # May be empty
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving drug info: {str(e)}")
            return None
    
    async def check_side_effect_match(
        self,
        drug_name: str,
        symptoms: List[str]
    ) -> Dict[str, any]:
        """
        Check if symptoms match known side effects
        
        Args:
            drug_name: Name of the drug
            symptoms: List of reported symptoms
            
        Returns:
            Match analysis
        """
        try:
            drug_info = await self.get_drug_side_effects(drug_name)
            
            if not drug_info:
                return {
                    "found_in_database": False,
                    "matched_common": [],
                    "matched_serious": [],
                    "unmatched": symptoms
                }
            
            matched_common = []
            matched_serious = []
            unmatched = []
            
            common_effects = drug_info.get("common_side_effects", [])
            serious_effects = drug_info.get("serious_side_effects", [])
            
            for symptom in symptoms:
                symptom_lower = symptom.lower().strip()
                if not symptom_lower:
                    continue
                    
                # Check common side effects
                if any(symptom_lower in effect.lower() for effect in common_effects):
                    matched_common.append(symptom)
                # Check serious side effects
                elif any(symptom_lower in effect.lower() for effect in serious_effects):
                    matched_serious.append(symptom)
                else:
                    unmatched.append(symptom)
            
            return {
                "found_in_database": True,
                "matched_common": matched_common,
                "matched_serious": matched_serious,
                "unmatched": unmatched,
                "all_common_effects": common_effects,
                "all_serious_effects": serious_effects
            }
            
        except Exception as e:
            logger.error(f"Error checking side effect match: {str(e)}")
            return {
                "found_in_database": False,
                "matched_common": [],
                "matched_serious": [],
                "unmatched": symptoms
            }


# Global service instance
rag_service = RAGService()
