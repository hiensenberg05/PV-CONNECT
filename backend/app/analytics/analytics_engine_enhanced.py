"""
Enhanced Analytics Engine for PV-CONNECT Dashboard
Provides VigiGrade scoring and multi-algorithm signal detection (PRR + BCPNN)
"""
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime
import math
import numpy as np

# Import BCPNN engine
try:
    from .bcpnn_engine import BCPNNEngine, run_bcpnn_analysis
    BCPNN_AVAILABLE = True
except ImportError:
    BCPNN_AVAILABLE = False


class VigiGradeScorer:
    """
    Calculates a "Completeness Score" (0.0 to 1.0) for a single adverse event case.
    
    Higher scores indicate more complete case reports with all critical fields populated.
    This score helps prioritize cases and measure data quality.
    """
    
    # Penalty weights for missing fields
    PENALTIES = {
        "onset_date": 0.2,      # Critical for temporal relationship
        "patient_age": 0.1,     # Important demographic
        "outcome": 0.1,         # Required for case assessment
        "drug_dosage": 0.1,     # Essential for causality
        "patient_sex": 0.05,    # Demographic completeness
        "severity": 0.05,       # Event classification
        "causality": 0.1,       # Assessment completeness
        "narrative": 0.1,       # Case description
    }
    
    def __init__(self):
        """Initialize the VigiGrade scorer"""
        self.max_score = 1.0
        
    def calculate_score(self, case_json: Dict[str, Any]) -> float:
        """
        Calculate completeness score for a single case.
        
        Args:
            case_json: Dictionary containing case data
            
        Returns:
            Float score between 0.0 and 1.0
        """
        score = self.max_score
        
        # Check onset_date in adverse_events
        adverse_events = case_json.get("adverse_events", [])
        has_onset_date = any(
            event.get("onset_date") is not None 
            for event in adverse_events
        ) if adverse_events else False
        if not has_onset_date:
            score -= self.PENALTIES["onset_date"]
        
        # Check patient age
        patient = case_json.get("patient", {})
        if not patient.get("age"):
            score -= self.PENALTIES["patient_age"]
        
        # Check patient sex
        if not patient.get("sex") or patient.get("sex") == "Unknown":
            score -= self.PENALTIES["patient_sex"]
        
        # Check outcome in adverse_events
        has_outcome = any(
            event.get("outcome") and event.get("outcome") != "Unknown"
            for event in adverse_events
        ) if adverse_events else False
        if not has_outcome:
            score -= self.PENALTIES["outcome"]
        
        # Check drug dosage in suspect_products
        suspect_products = case_json.get("suspect_products", [])
        has_dosage = any(
            product.get("dose") is not None 
            for product in suspect_products
        ) if suspect_products else False
        if not has_dosage:
            score -= self.PENALTIES["drug_dosage"]
        
        # Check severity in adverse_events
        has_severity = any(
            event.get("severity") and event.get("severity") != "Unknown"
            for event in adverse_events
        ) if adverse_events else False
        if not has_severity:
            score -= self.PENALTIES["severity"]
        
        # Check causality assessment
        if not case_json.get("causality_assessment"):
            score -= self.PENALTIES["causality"]
        
        # Check narrative
        narrative = case_json.get("narrative", "")
        if not narrative or len(narrative) < 20:
            score -= self.PENALTIES["narrative"]
        
        # Ensure score stays within bounds
        return max(0.0, min(1.0, round(score, 2)))
    
    def get_missing_fields(self, case_json: Dict[str, Any]) -> List[str]:
        """
        Get list of missing fields for a case.
        
        Args:
            case_json: Dictionary containing case data
            
        Returns:
            List of field names that are missing
        """
        missing = []
        
        adverse_events = case_json.get("adverse_events", [])
        patient = case_json.get("patient", {})
        suspect_products = case_json.get("suspect_products", [])
        
        # Check each field
        if not any(e.get("onset_date") for e in adverse_events):
            missing.append("onset_date")
        
        if not patient.get("age"):
            missing.append("patient_age")
        
        if not patient.get("sex") or patient.get("sex") == "Unknown":
            missing.append("patient_sex")
        
        if not any(e.get("outcome") and e.get("outcome") != "Unknown" for e in adverse_events):
            missing.append("outcome")
        
        if not any(p.get("dose") for p in suspect_products):
            missing.append("drug_dosage")
        
        if not any(e.get("severity") and e.get("severity") != "Unknown" for e in adverse_events):
            missing.append("severity")
        
        if not case_json.get("causality_assessment"):
            missing.append("causality_assessment")
        
        if not case_json.get("narrative") or len(case_json.get("narrative", "")) < 20:
            missing.append("narrative")
        
        return missing


class EnhancedSignalDetector:
    """
    Multi-algorithm signal detector with PRR and BCPNN support.
    
    Implements:
    - Proportional Reporting Ratio (PRR)
    - Bayesian Confidence Propagation Neural Network (BCPNN)
    - Consensus detection across algorithms
    """
    
    def __init__(
        self,
        prr_threshold: float = 2.0,
        min_case_count: int = 3,
        ic_threshold: float = 0.0,
        use_bcpnn: bool = True
    ):
        """
        Initialize the enhanced signal detector.
        
        Args:
            prr_threshold: PRR value above which a signal is detected (default: 2.0)
            min_case_count: Minimum cases required (default: 3)
            ic_threshold: BCPNN IC threshold (default: 0.0)
            use_bcpnn: Enable BCPNN analysis (default: True)
        """
        self.prr_threshold = prr_threshold
        self.min_case_count = min_case_count
        self.ic_threshold = ic_threshold
        self.use_bcpnn = use_bcpnn and BCPNN_AVAILABLE
        
        if self.use_bcpnn:
            self.bcpnn_engine = BCPNNEngine(
                min_count=min_case_count,
                ic_threshold=ic_threshold
            )
    
    def detect_signals(
        self,
        all_cases: List[Dict[str, Any]],
        algorithm: str = "all"  # "prr", "bcpnn", or "all"
    ) -> List[Dict[str, Any]]:
        """
        Detect safety signals using specified algorithm(s).
        
        Args:
            all_cases: List of case dictionaries
            algorithm: Which algorithm to use ("prr", "bcpnn", or "all")
            
        Returns:
            List of detected signals with metrics
        """
        if not all_cases:
            return []
        
        signals_dict = {}  # {(drug, event): signal_data}
        
        # Run PRR if requested
        if algorithm in ["prr", "all"]:
            prr_signals = self._detect_prr_signals(all_cases)
            for signal in prr_signals:
                key = (signal["drug"].lower(), signal["reaction"].lower())
                signals_dict[key] = signal
        
        # Run BCPNN if requested and available
        if algorithm in ["bcpnn", "all"] and self.use_bcpnn:
            bcpnn_results = self.bcpnn_engine.analyze_dataset(all_cases)
            
            for result in bcpnn_results:
                if not result.is_signal:
                    continue
                
                key = (result.drug.lower(), result.event.lower())
                
                if key in signals_dict:
                    # Merge with existing PRR signal
                    signals_dict[key].update({
                        "ic": result.ic,
                        "ic_lower": result.ic_lower,
                        "ic_upper": result.ic_upper,
                        "expected_count": result.expected_count,
                        "detection_methods": ["PRR", "BCPNN"],
                        "bcpnn_signal": True
                    })
                else:
                    # Create new BCPNN-only signal
                    signals_dict[key] = {
                        "drug": result.drug,
                        "reaction": result.event,
                        "case_count": result.count,
                        "ic": result.ic,
                        "ic_lower": result.ic_lower,
                        "ic_upper": result.ic_upper,
                        "expected_count": result.expected_count,
                        "status": "SIGNAL DETECTED",
                        "detected_at": datetime.utcnow().isoformat(),
                        "detection_methods": ["BCPNN"],
                        "bcpnn_signal": True
                    }
        
        # Convert to list and sort
        signals = list(signals_dict.values())
        
        # Sort by number of detection methods, then by IC (if available), then PRR
        def sort_key(s):
            methods = len(s.get("detection_methods", []))
            ic = s.get("ic", 0)
            prr = s.get("prr_score", 0)
            return (methods, ic, prr)
        
        signals.sort(key=sort_key, reverse=True)
        
        return signals
    
    def _detect_prr_signals(self, all_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect signals using PRR algorithm.
        
        This is the existing PRR implementation.
        """
        # Build contingency tables
        drug_reaction_counts = defaultdict(int)
        drug_counts = defaultdict(int)
        reaction_counts = defaultdict(int)
        total_cases = 0
        
        for case in all_cases:
            # Extract drugs
            drugs = set()
            for product in case.get("suspect_products", []):
                drug_name = product.get("product_name", "").strip().lower()
                if drug_name:
                    drugs.add(drug_name)
            
            # Extract reactions
            reactions = set()
            for event in case.get("adverse_events", []):
                event_term = event.get("event_term", "").strip().lower()
                if event_term:
                    reactions.add(event_term)
            
            # Count pairs
            for drug in drugs:
                drug_counts[drug] += 1
                for reaction in reactions:
                    drug_reaction_counts[(drug, reaction)] += 1
                    reaction_counts[reaction] += 1
            
            total_cases += 1
        
        # Calculate PRR for each pair
        signals = []
        
        for (drug, reaction), observed_count in drug_reaction_counts.items():
            if observed_count < self.min_case_count:
                continue
            
            # 2x2 contingency table
            a = observed_count
            b = drug_counts[drug] - a
            c = reaction_counts[reaction] - a
            d = total_cases - a - b - c
            
            # Calculate PRR
            try:
                if (a + b) == 0 or (c + d) == 0 or c == 0:
                    prr = 0.0
                else:
                    numerator = a / (a + b)
                    denominator = c / (c + d)
                    prr = numerator / denominator if denominator > 0 else 0.0
            except ZeroDivisionError:
                prr = 0.0
            
            # Determine signal status
            if prr > self.prr_threshold and observed_count >= self.min_case_count:
                status = "SIGNAL DETECTED"
                is_signal = True
            elif prr > 1.5:
                status = "UNDER MONITORING"
                is_signal = False
            else:
                status = "NO SIGNAL"
                is_signal = False
            
            if is_signal or status == "UNDER MONITORING":
                signals.append({
                    "drug": drug.title(),
                    "reaction": reaction.title(),
                    "case_count": observed_count,
                    "prr_score": round(prr, 2) if prr != float('inf') else 999.99,
                    "status": status,
                    "detected_at": datetime.utcnow().isoformat(),
                    "detection_methods": ["PRR"] if is_signal else [],
                    "contingency": {"a": a, "b": b, "c": c, "d": d}
                })
        
        return signals
    
    def calculate_prr_for_pair(
        self, 
        drug: str, 
        reaction: str, 
        all_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate PRR for a specific drug-reaction pair.
        
        Args:
            drug: Drug name to check
            reaction: Reaction term to check
            all_cases: List of all cases
            
        Returns:
            Dictionary with PRR calculation results
        """
        drug_lower = drug.lower()
        reaction_lower = reaction.lower()
        
        a = b = c = d = 0
        
        for case in all_cases:
            has_drug = any(
                p.get("product_name", "").lower() == drug_lower 
                for p in case.get("suspect_products", [])
            )
            has_reaction = any(
                e.get("event_term", "").lower() == reaction_lower 
                for e in case.get("adverse_events", [])
            )
            
            if has_drug and has_reaction:
                a += 1
            elif has_drug and not has_reaction:
                b += 1
            elif not has_drug and has_reaction:
                c += 1
            else:
                d += 1
        
        # Calculate PRR
        try:
            if (a + b) == 0 or (c + d) == 0 or c == 0:
                prr = 0.0
            else:
                prr = (a / (a + b)) / (c / (c + d))
        except ZeroDivisionError:
            prr = 0.0
        
        # Calculate BCPNN IC if available
        ic_data = {}
        if self.use_bcpnn:
            bcpnn_result = self.bcpnn_engine.calculate_single_pair(
                drug, reaction, all_cases
            )
            if bcpnn_result:
                ic_data = {
                    "ic": bcpnn_result.ic,
                    "ic_lower": bcpnn_result.ic_lower,
                    "ic_upper": bcpnn_result.ic_upper
                }
        
        return {
            "drug": drug,
            "reaction": reaction,
            "prr_score": round(prr, 2),
            "is_signal": prr > self.prr_threshold,
            "case_count": a,
            "contingency": {"a": a, "b": b, "c": c, "d": d},
            **ic_data
        }


class AnalyticsAggregator:
    """
    Aggregates analytics for dashboard display with BCPNN support.
    """
    
    def __init__(self, use_bcpnn: bool = True):
        self.vigigrade_scorer = VigiGradeScorer()
        self.signal_detector = EnhancedSignalDetector(use_bcpnn=use_bcpnn)
    
    def generate_dashboard_summary(
        self, 
        all_cases: List[Dict[str, Any]],
        signal_algorithm: str = "all"
    ) -> Dict[str, Any]:
        """
        Generate complete dashboard summary with multi-algorithm detection.
        
        Args:
            all_cases: List of all case dictionaries from MongoDB
            signal_algorithm: "prr", "bcpnn", or "all"
            
        Returns:
            Dashboard summary dictionary
        """
        if not all_cases:
            return {
                "total_cases": 0,
                "average_vigigrade": 0.0,
                "signals_detected": 0,
                "signals": [],
                "quality_distribution": {},
                "bcpnn_enabled": self.signal_detector.use_bcpnn,
                "generated_at": datetime.utcnow().isoformat()
            }
        
        # Calculate VigiGrade scores
        scores = [self.vigigrade_scorer.calculate_score(case) for case in all_cases]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # Quality distribution
        quality_dist = {
            "excellent": sum(1 for s in scores if s >= 0.9),
            "good": sum(1 for s in scores if 0.7 <= s < 0.9),
            "fair": sum(1 for s in scores if 0.5 <= s < 0.7),
            "poor": sum(1 for s in scores if s < 0.5)
        }
        
        # Detect signals with specified algorithm
        signals = self.signal_detector.detect_signals(all_cases, algorithm=signal_algorithm)
        active_signals = [s for s in signals if s.get("status") == "SIGNAL DETECTED"]
        
        # Categorize by detection method
        prr_only = sum(1 for s in active_signals if s.get("detection_methods") == ["PRR"])
        bcpnn_only = sum(1 for s in active_signals if s.get("detection_methods") == ["BCPNN"])
        both_methods = sum(1 for s in active_signals if len(s.get("detection_methods", [])) > 1)
        
        # Cases requiring review
        cases_needing_review = sum(
            1 for case in all_cases 
            if case.get("requires_human_review", False)
        )
        
        # Status distribution
        status_dist = defaultdict(int)
        for case in all_cases:
            status = case.get("status", "Pending")
            status_dist[status] += 1
        
        return {
            "total_cases": len(all_cases),
            "average_vigigrade": round(avg_score, 2),
            "quality_distribution": quality_dist,
            "signals_detected": len(active_signals),
            "signals_monitoring": len(signals) - len(active_signals),
            "signals": signals[:20],  # Top 20 signals
            "signal_breakdown": {
                "prr_only": prr_only,
                "bcpnn_only": bcpnn_only,
                "detected_by_both": both_methods
            },
            "cases_pending_review": cases_needing_review,
            "status_distribution": dict(status_dist),
            "bcpnn_enabled": self.signal_detector.use_bcpnn,
            "algorithm_used": signal_algorithm,
            "generated_at": datetime.utcnow().isoformat()
        }


# Maintain backward compatibility - alias to original class name
SignalDetector = EnhancedSignalDetector
