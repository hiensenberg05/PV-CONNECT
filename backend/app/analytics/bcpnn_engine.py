"""
BCPNN (Bayesian Confidence Propagation Neural Network) Implementation
for Pharmacovigilance Signal Detection

This module implements the BCPNN algorithm used by the WHO Uppsala Monitoring Centre
for detecting adverse drug reaction signals in spontaneous reporting databases.

References:
- Bate et al. (1998) "A Bayesian neural network method for adverse drug reaction signal generation"
- Norén et al. (2006) "Shrinkage observed-to-expected ratios for robust and transparent large-scale pattern discovery"
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import math
import numpy as np
from loguru import logger


@dataclass
class BCPNNResult:
    """
    Results from BCPNN analysis for a drug-event pair.
    
    Attributes:
        drug: Drug name
        event: Adverse event term
        count: Number of reports with this drug-event combination
        expected_count: Expected count under independence
        ic: Information Component (log2 of observed/expected ratio)
        ic_lower: Lower bound of 95% credibility interval for IC
        ic_upper: Upper bound of 95% credibility interval for IC
        is_signal: Whether this constitutes a signal (IC_lower > 0)
        total_reports: Total number of reports in database
        drug_margin: Total reports containing this drug
        event_margin: Total reports containing this event
    """
    drug: str
    event: str
    count: int
    expected_count: float
    ic: float
    ic_lower: float
    ic_upper: float
    is_signal: bool
    total_reports: int
    drug_margin: int
    event_margin: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "drug": self.drug,
            "event": self.event,
            "count": self.count,
            "expected_count": round(self.expected_count, 2),
            "ic": round(self.ic, 3),
            "ic_lower": round(self.ic_lower, 3),
            "ic_upper": round(self.ic_upper, 3),
            "is_signal": self.is_signal,
            "signal_strength": self._classify_signal_strength(),
            "total_reports": self.total_reports,
            "drug_margin": self.drug_margin,
            "event_margin": self.event_margin
        }
    
    def _classify_signal_strength(self) -> str:
        """Classify signal strength based on IC value"""
        if not self.is_signal:
            return "No Signal"
        elif self.ic >= 3.0:
            return "Very Strong"
        elif self.ic >= 2.0:
            return "Strong"
        elif self.ic >= 1.0:
            return "Moderate"
        else:
            return "Weak"


class BCPNNEngine:
    """
    Bayesian Confidence Propagation Neural Network (BCPNN) implementation.
    
    The BCPNN algorithm calculates the Information Component (IC) which represents
    the logarithm (base 2) of the ratio between observed and expected counts for
    a drug-event combination.
    
    IC = log2(P(drug, event) / (P(drug) * P(event)))
    
    A signal is detected when the lower bound of the 95% credibility interval
    for IC is greater than 0 (IC_lower > 0).
    """
    
    def __init__(
        self,
        min_count: int = 3,
        ic_threshold: float = 0.0,
        credibility_level: float = 0.95
    ):
        """
        Initialize BCPNN engine.
        
        Args:
            min_count: Minimum number of reports required for analysis (default: 3)
            ic_threshold: IC lower bound threshold for signal detection (default: 0.0)
            credibility_level: Credibility level for intervals (default: 0.95)
        """
        self.min_count = min_count
        self.ic_threshold = ic_threshold
        self.credibility_level = credibility_level
        
        # Prior parameters for Bayesian shrinkage
        # These represent our prior belief before seeing data
        self.alpha_prior = 0.5  # Prior count for drug-event combination
        self.beta_prior = 0.5   # Prior count for drug margin
        self.gamma_prior = 0.5  # Prior count for event margin
        
        logger.info(
            f"BCPNN Engine initialized | "
            f"min_count={min_count}, ic_threshold={ic_threshold}"
        )
    
    def analyze_dataset(
        self,
        cases: List[Dict[str, Any]],
        drug_field: str = "suspect_products",
        event_field: str = "adverse_events",
        drug_name_key: str = "product_name",
        event_term_key: str = "event_term"
    ) -> List[BCPNNResult]:
        """
        Perform BCPNN analysis on a dataset of adverse event reports.
        
        Args:
            cases: List of case dictionaries from MongoDB
            drug_field: Field name containing drug information
            event_field: Field name containing event information
            drug_name_key: Key for drug name within drug objects
            event_term_key: Key for event term within event objects
            
        Returns:
            List of BCPNNResult objects for all drug-event pairs
        """
        logger.info(f"Starting BCPNN analysis on {len(cases)} cases")
        
        # Step 1: Build contingency data
        contingency_data = self._build_contingency_data(
            cases, drug_field, event_field, drug_name_key, event_term_key
        )
        
        # Step 2: Calculate BCPNN metrics for each pair
        results = []
        total_pairs = len(contingency_data["pair_counts"])
        
        for i, ((drug, event), count) in enumerate(contingency_data["pair_counts"].items(), 1):
            # Skip if below minimum count threshold
            if count < self.min_count:
                continue
            
            # Calculate BCPNN metrics
            result = self._calculate_bcpnn(
                drug=drug,
                event=event,
                count=count,
                contingency_data=contingency_data
            )
            
            results.append(result)
            
            if i % 100 == 0:
                logger.debug(f"Processed {i}/{total_pairs} drug-event pairs")
        
        # Sort by IC value (descending)
        results.sort(key=lambda x: x.ic, reverse=True)
        
        signals = [r for r in results if r.is_signal]
        logger.success(
            f"BCPNN analysis complete | "
            f"Analyzed {len(results)} pairs, detected {len(signals)} signals"
        )
        
        return results
    
    def _build_contingency_data(
        self,
        cases: List[Dict[str, Any]],
        drug_field: str,
        event_field: str,
        drug_name_key: str,
        event_term_key: str
    ) -> Dict[str, Any]:
        """
        Build contingency table data from cases.
        
        Returns:
            Dictionary containing:
            - pair_counts: {(drug, event): count}
            - drug_counts: {drug: count}
            - event_counts: {event: count}
            - total_reports: total number of reports
        """
        pair_counts = defaultdict(int)
        drug_counts = defaultdict(int)
        event_counts = defaultdict(int)
        total_reports = 0
        
        for case in cases:
            # Extract drugs from case
            drugs = set()
            drug_list = case.get(drug_field, [])
            if isinstance(drug_list, list):
                for drug_obj in drug_list:
                    drug_name = drug_obj.get(drug_name_key, "").strip()
                    if drug_name:
                        # Normalize to lowercase for consistency
                        drugs.add(drug_name.lower())
            
            # Extract events from case
            events = set()
            event_list = case.get(event_field, [])
            if isinstance(event_list, list):
                for event_obj in event_list:
                    event_term = event_obj.get(event_term_key, "").strip()
                    if event_term:
                        # Normalize to lowercase for consistency
                        events.add(event_term.lower())
            
            # Skip cases with no drugs or events
            if not drugs or not events:
                continue
            
            # Count occurrences
            total_reports += 1
            
            for drug in drugs:
                drug_counts[drug] += 1
                for event in events:
                    pair_counts[(drug, event)] += 1
            
            for event in events:
                event_counts[event] += 1
        
        return {
            "pair_counts": dict(pair_counts),
            "drug_counts": dict(drug_counts),
            "event_counts": dict(event_counts),
            "total_reports": total_reports
        }
    
    def _calculate_bcpnn(
        self,
        drug: str,
        event: str,
        count: int,
        contingency_data: Dict[str, Any]
    ) -> BCPNNResult:
        """
        Calculate BCPNN metrics for a single drug-event pair.
        
        Uses Bayesian shrinkage with informative priors to stabilize estimates
        for rare events.
        """
        total = contingency_data["total_reports"]
        drug_margin = contingency_data["drug_counts"].get(drug, 0)
        event_margin = contingency_data["event_counts"].get(event, 0)
        
        # Apply Bayesian shrinkage with priors
        # Posterior expected counts
        n_11_posterior = count + self.alpha_prior
        n_1x_posterior = drug_margin + self.beta_prior
        n_x1_posterior = event_margin + self.gamma_prior
        n_xx_posterior = total + (self.alpha_prior + self.beta_prior + self.gamma_prior)
        
        # Calculate posterior probabilities
        p_11 = n_11_posterior / n_xx_posterior  # P(drug AND event)
        p_1x = n_1x_posterior / n_xx_posterior  # P(drug)
        p_x1 = n_x1_posterior / n_xx_posterior  # P(event)
        
        # Expected count under independence
        expected = p_1x * p_x1 * n_xx_posterior
        
        # Information Component (IC)
        # IC = log2(P(drug, event) / (P(drug) * P(event)))
        if p_1x > 0 and p_x1 > 0:
            ic = math.log2(p_11 / (p_1x * p_x1))
        else:
            ic = 0.0
        
        # Calculate credibility interval for IC
        # Using variance formula from Norén et al. (2006)
        ic_lower, ic_upper = self._calculate_ic_credibility_interval(
            count=count,
            drug_margin=drug_margin,
            event_margin=event_margin,
            total=total
        )
        
        # Determine if this is a signal
        is_signal = ic_lower > self.ic_threshold
        
        return BCPNNResult(
            drug=drug.title(),
            event=event.title(),
            count=count,
            expected_count=expected,
            ic=ic,
            ic_lower=ic_lower,
            ic_upper=ic_upper,
            is_signal=is_signal,
            total_reports=total,
            drug_margin=drug_margin,
            event_margin=event_margin
        )
    
    def _calculate_ic_credibility_interval(
        self,
        count: int,
        drug_margin: int,
        event_margin: int,
        total: int
    ) -> Tuple[float, float]:
        """
        Calculate credibility interval for Information Component.
        
        Uses approximation based on variance of log-transformed proportions.
        
        Returns:
            Tuple of (ic_lower, ic_upper)
        """
        # Add priors for stability
        n_11 = count + self.alpha_prior
        n_1x = drug_margin + self.beta_prior
        n_x1 = event_margin + self.gamma_prior
        n_xx = total + (self.alpha_prior + self.beta_prior + self.gamma_prior)
        
        # Variance calculation
        # Var(IC) ≈ 1/(n_11 * ln(2)^2) + 1/(n_1x * ln(2)^2) + 1/(n_x1 * ln(2)^2)
        
        if n_11 > 0 and n_1x > 0 and n_x1 > 0:
            # Calculate variance in natural log scale
            var_log = (1.0 / n_11) + (1.0 / n_1x) + (1.0 / n_x1)
            
            # Convert to base-2 log scale
            var_ic = var_log / (math.log(2) ** 2)
            
            # Standard deviation
            sd_ic = math.sqrt(var_ic)
            
            # Calculate IC
            p_11 = n_11 / n_xx
            p_1x = n_1x / n_xx
            p_x1 = n_x1 / n_xx
            
            ic = math.log2(p_11 / (p_1x * p_x1))
            
            # Z-score for 95% credibility interval (approximately 1.96)
            z = 1.96 if self.credibility_level == 0.95 else 2.576  # 99% CI
            
            # Credibility interval
            ic_lower = ic - (z * sd_ic)
            ic_upper = ic + (z * sd_ic)
        else:
            ic = 0.0
            ic_lower = 0.0
            ic_upper = 0.0
        
        return ic_lower, ic_upper
    
    def calculate_single_pair(
        self,
        drug: str,
        event: str,
        cases: List[Dict[str, Any]],
        **kwargs
    ) -> Optional[BCPNNResult]:
        """
        Calculate BCPNN metrics for a specific drug-event pair.
        
        Args:
            drug: Drug name to analyze
            event: Event term to analyze
            cases: List of all cases for context
            **kwargs: Additional arguments passed to analyze_dataset
            
        Returns:
            BCPNNResult for the specified pair, or None if insufficient data
        """
        # Run full analysis
        all_results = self.analyze_dataset(cases, **kwargs)
        
        # Find the specific pair
        drug_lower = drug.lower()
        event_lower = event.lower()
        
        for result in all_results:
            if (result.drug.lower() == drug_lower and 
                result.event.lower() == event_lower):
                return result
        
        return None


class BCPNNIntegration:
    """
    Integration layer for BCPNN with existing signal detection framework.
    
    This class provides methods to integrate BCPNN analysis with your
    existing SignalDetectionEngine and AnalyticsAggregator.
    """
    
    def __init__(self, bcpnn_engine: Optional[BCPNNEngine] = None):
        """
        Initialize BCPNN integration.
        
        Args:
            bcpnn_engine: Optional pre-configured BCPNNEngine instance
        """
        self.bcpnn = bcpnn_engine or BCPNNEngine()
        logger.info("BCPNN Integration layer initialized")
    
    def enhance_signal_detection(
        self,
        cases: List[Dict[str, Any]],
        existing_signals: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Enhance existing signal detection with BCPNN analysis.
        
        This method can be used to add BCPNN metrics to signals detected
        by other methods (PRR, ROR).
        
        Args:
            cases: List of case dictionaries
            existing_signals: Optional list of signals from other methods
            
        Returns:
            Enhanced signal list with BCPNN metrics
        """
        # Run BCPNN analysis
        bcpnn_results = self.bcpnn.analyze_dataset(cases)
        
        # Create lookup dictionary
        bcpnn_lookup = {
            (r.drug.lower(), r.event.lower()): r
            for r in bcpnn_results
        }
        
        enhanced_signals = []
        
        # If existing signals provided, enhance them
        if existing_signals:
            for signal in existing_signals:
                drug = signal.get("drug", "").lower()
                event = signal.get("reaction", signal.get("event", "")).lower()
                
                # Look up BCPNN result
                bcpnn_result = bcpnn_lookup.get((drug, event))
                
                # Add BCPNN metrics
                enhanced = signal.copy()
                if bcpnn_result:
                    enhanced.update({
                        "ic": bcpnn_result.ic,
                        "ic_lower": bcpnn_result.ic_lower,
                        "ic_upper": bcpnn_result.ic_upper,
                        "bcpnn_signal": bcpnn_result.is_signal,
                        "expected_count": bcpnn_result.expected_count
                    })
                
                enhanced_signals.append(enhanced)
        else:
            # Use BCPNN results as primary signals
            enhanced_signals = [r.to_dict() for r in bcpnn_results if r.is_signal]
        
        return enhanced_signals
    
    def compare_algorithms(
        self,
        cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare BCPNN with other signal detection algorithms.
        
        Returns comparative statistics showing agreement/disagreement
        between methods.
        
        Args:
            cases: List of case dictionaries
            
        Returns:
            Dictionary with comparison statistics
        """
        from ..services.analytics_engine import SignalDetector
        
        # Run both algorithms
        bcpnn_results = self.bcpnn.analyze_dataset(cases)
        prr_detector = SignalDetector()
        prr_signals = prr_detector.detect_signals(cases)
        
        # Create sets of signal pairs
        bcpnn_signals = {
            (r.drug.lower(), r.event.lower())
            for r in bcpnn_results if r.is_signal
        }
        
        prr_signal_pairs = {
            (s["drug"].lower(), s["reaction"].lower())
            for s in prr_signals if s["status"] == "SIGNAL DETECTED"
        }
        
        # Calculate agreement metrics
        both = bcpnn_signals & prr_signal_pairs
        bcpnn_only = bcpnn_signals - prr_signal_pairs
        prr_only = prr_signal_pairs - bcpnn_signals
        
        total_unique = len(bcpnn_signals | prr_signal_pairs)
        agreement_rate = len(both) / total_unique if total_unique > 0 else 0
        
        return {
            "total_cases": len(cases),
            "bcpnn_signals": len(bcpnn_signals),
            "prr_signals": len(prr_signal_pairs),
            "both_methods": len(both),
            "bcpnn_only": len(bcpnn_only),
            "prr_only": len(prr_only),
            "agreement_rate": round(agreement_rate * 100, 1),
            "signals_detected_by_both": list(both)[:10]  # Sample
        }


# Convenience functions for easy integration

def run_bcpnn_analysis(
    cases: List[Dict[str, Any]],
    min_count: int = 3,
    ic_threshold: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Convenience function to run BCPNN analysis on cases.
    
    Args:
        cases: List of case dictionaries from MongoDB
        min_count: Minimum reports required
        ic_threshold: IC lower bound threshold for signals
        
    Returns:
        List of signal dictionaries
    """
    engine = BCPNNEngine(min_count=min_count, ic_threshold=ic_threshold)
    results = engine.analyze_dataset(cases)
    
    # Return only signals, converted to dicts
    return [r.to_dict() for r in results if r.is_signal]


def add_bcpnn_to_existing_signals(
    cases: List[Dict[str, Any]],
    existing_signals: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Add BCPNN metrics to signals detected by other methods.
    
    Args:
        cases: List of all cases
        existing_signals: Signals from PRR/ROR/other methods
        
    Returns:
        Enhanced signals with BCPNN metrics
    """
    integration = BCPNNIntegration()
    return integration.enhance_signal_detection(cases, existing_signals)


# Example usage
if __name__ == "__main__":
    # Example: Standalone BCPNN analysis
    sample_cases = [
        {
            "suspect_products": [{"product_name": "Aspirin"}],
            "adverse_events": [{"event_term": "Headache"}]
        },
        {
            "suspect_products": [{"product_name": "Aspirin"}],
            "adverse_events": [{"event_term": "Nausea"}]
        },
        {
            "suspect_products": [{"product_name": "Paracetamol"}],
            "adverse_events": [{"event_term": "Headache"}]
        }
    ]
    
    # Run analysis
    signals = run_bcpnn_analysis(sample_cases, min_count=1)
    
    for signal in signals:
        print(f"{signal['drug']} - {signal['event']}: IC={signal['ic']:.3f}")
