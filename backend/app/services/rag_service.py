"""
RAG Service for Drug Safety Database
Uses Sentence Transformers for semantic side effect matching
"""
import logging
from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)


class RAGService:
    """Service for retrieving drug safety information"""
    
    def __init__(self):
        """Initialize RAG service with Embedding Model"""
        # We now use the shared mongodb_service
        try:
            logger.info("Loading Sentence Transformer model (all-MiniLM-L6-v2)...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.threshold = 0.6 # Similarity threshold
            logger.info("Sentence Transformer model loaded.")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer: {e}")
            self.model = None

    
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
        Check if symptoms match known side effects using Semantic Search
        
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
            
            common_effects = drug_info.get("common_side_effects", [])
            serious_effects = drug_info.get("serious_side_effects", [])
            
            # Combine all known effects for embedding
            # Keep track of which list they came from
            all_known = []
            effect_type_map = {} # index -> 'common' or 'serious'
            
            for effect in common_effects:
                all_known.append(effect)
                effect_type_map[len(all_known)-1] = 'common'
                
            for effect in serious_effects:
                all_known.append(effect)
                effect_type_map[len(all_known)-1] = 'serious'
            
            if not all_known or not self.model:
                # Fallback to simple string matching if no model or no effects
                return self._fallback_keyword_match(symptoms, common_effects, serious_effects)

            # Compute embeddings
            # 1. Embed known effects (doc)
            known_embeddings = self.model.encode(all_known, convert_to_tensor=True)
            
            # 2. Embed user symptoms (query)
            symptom_embeddings = self.model.encode(symptoms, convert_to_tensor=True)
            
            # Compute cosine similarities
            cosine_scores = util.cos_sim(symptom_embeddings, known_embeddings)
            
            matched_common = []
            matched_serious = []
            unmatched = []
            
            # For each symptom, check max similarity
            for i, symptom in enumerate(symptoms):
                scores = cosine_scores[i]
                best_score_idx = np.argmax(scores.cpu().numpy())
                best_score = scores[best_score_idx].item()
                
                if best_score >= self.threshold:
                    matched_effect = all_known[best_score_idx]
                    effect_type = effect_type_map[best_score_idx]
                    
                    logger.info(f"Semantic match: '{symptom}' ~= '{matched_effect}' (score: {best_score:.2f})")
                    
                    if effect_type == 'common':
                        if matched_effect not in matched_common: # Avoid dupes
                            matched_common.append(matched_effect) 
                            # Note: we return the OFFICIAL matched name, or user name? 
                            # Usually helpful to return matching official term, 
                            # but for user confirmation maybe user term is better.
                            # Let's return the user's symptom but log the match.
                    else:
                        if matched_effect not in matched_serious:
                            matched_serious.append(matched_effect)
                else:
                    unmatched.append(symptom)
            
            return {
                "found_in_database": True,
                "matched_common": matched_common, # Returning lists of matched EFFECT names (or input symptoms?)
                                                  # Let's return the KNOWN effects needed for Triage comparison
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

    def _fallback_keyword_match(self, symptoms, common, serious):
        """Fallback if model fails"""
        matched_common = []
        matched_serious = []
        unmatched = []
        
        for symptom in symptoms:
            s_lower = symptom.lower()
            if any(s_lower in e.lower() for e in common):
                matched_common.append(symptom) # Here we just appended user symptom
            elif any(s_lower in e.lower() for e in serious):
                matched_serious.append(symptom)
            else:
                unmatched.append(symptom)
                
        return {
            "found_in_database": True,
            "matched_common": matched_common,
            "matched_serious": matched_serious,
            "unmatched": unmatched,
            "all_common_effects": common,
            "all_serious_effects": serious
        }


# Global service instance
rag_service = RAGService()
