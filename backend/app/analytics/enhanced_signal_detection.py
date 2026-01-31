"""
Enhanced Signal Detection Module with BCPNN Integration
Performs comprehensive statistical disproportionality analysis for pharmacovigilance

Implements:
- Proportional Reporting Ratio (PRR)
- Reporting Odds Ratio (ROR)  
- Bayesian Confidence Propagation Neural Network (BCPNN)
- Multi-algorithm consensus detection
"""
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger

# Import BCPNN engine
from bcpnn_engine import BCPNNEngine, BCPNNResult, BCPNNIntegration

# Note: vigipy needs to be installed from GitHub
# pip install git+https://github.com/Shakesbeery/vigipy.git
try:
    from vigipy import disproportionality
    VIGIPY_AVAILABLE = True
except ImportError:
    logger.warning("vigipy not installed. Signal detection will use fallback implementation.")
    VIGIPY_AVAILABLE = False


class DrugEventPair:
    """Data model for drug-event signal results"""
    def __init__(
        self,
        drug_name: str,
        event_term: str,
        count: int,
        prr: Optional[float] = None,
        prr_ci_lower: Optional[float] = None,
        prr_ci_upper: Optional[float] = None,
        ror: Optional[float] = None,
        ror_ci_lower: Optional[float] = None,
        ror_ci_upper: Optional[float] = None,
        ic: Optional[float] = None,
        ic_ci_lower: Optional[float] = None,
        ic_ci_upper: Optional[float] = None,
        is_signal: bool = False,
        signal_detected_date: Optional[datetime] = None,
        signal_status: str = "New",
        detection_methods: Optional[List[str]] = None
    ):
        self.drug_name = drug_name
        self.event_term = event_term
        self.count = count
        self.prr = prr
        self.prr_ci_lower = prr_ci_lower
        self.prr_ci_upper = prr_ci_upper
        self.ror = ror
        self.ror_ci_lower = ror_ci_lower
        self.ror_ci_upper = ror_ci_upper
        self.ic = ic
        self.ic_ci_lower = ic_ci_lower
        self.ic_ci_upper = ic_ci_upper
        self.is_signal = is_signal
        self.signal_detected_date = signal_detected_date or datetime.utcnow()
        self.signal_status = signal_status
        self.detection_methods = detection_methods or []
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "drug_name": self.drug_name,
            "event_term": self.event_term,
            "count": self.count,
            "prr": self.prr,
            "prr_ci_lower": self.prr_ci_lower,
            "prr_ci_upper": self.prr_ci_upper,
            "ror": self.ror,
            "ror_ci_lower": self.ror_ci_lower,
            "ror_ci_upper": self.ror_ci_upper,
            "ic": self.ic,
            "ic_ci_lower": self.ic_ci_lower,
            "ic_ci_upper": self.ic_ci_upper,
            "is_signal": self.is_signal,
            "signal_detected_date": self.signal_detected_date,
            "signal_status": self.signal_status,
            "detection_methods": self.detection_methods
        }


class EnhancedSignalDetectionEngine:
    """
    Comprehensive signal detection engine with multi-algorithm support.
    
    Implements PRR, ROR, and BCPNN with configurable thresholds and
    consensus detection across methods.
    """
    
    def __init__(self, database_client=None):
        """
        Initialize enhanced signal detection engine.
        
        Args:
            database_client: MongoDB client for accessing case data
        """
        self.db = database_client
        
        # PRR thresholds
        self.prr_threshold = 2.0  # PRR >= 2
        self.prr_chi2_threshold = 4.0  # Chi-square >= 4
        self.min_cases = 3  # Minimum 3 cases
        
        # ROR thresholds
        self.ror_ci_threshold = 1.0  # Lower bound of 95% CI > 1
        
        # BCPNN thresholds
        self.ic_threshold = 0.0  # IC lower bound > 0
        
        # Initialize BCPNN engine
        self.bcpnn_engine = BCPNNEngine(
            min_count=self.min_cases,
            ic_threshold=self.ic_threshold
        )
        
        # Consensus settings
        self.require_consensus = False  # If True, require multiple algorithms to agree
        self.consensus_threshold = 2  # Number of algorithms that must agree
        
        logger.info("Enhanced Signal Detection Engine initialized with BCPNN support")
    
    async def run_signal_detection(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        drug_filter: Optional[str] = None,
        use_bcpnn: bool = True,
        use_prr: bool = True,
        use_ror: bool = True
    ) -> List[DrugEventPair]:
        """
        Run comprehensive signal detection analysis.
        
        Args:
            start_date: Start date for analysis window
            end_date: End date for analysis window
            drug_filter: Optional drug name filter
            use_bcpnn: Enable BCPNN analysis
            use_prr: Enable PRR analysis
            use_ror: Enable ROR analysis
        
        Returns:
            List of drug-event pairs with signal metrics
        """
        logger.info("Starting enhanced signal detection analysis")
        
        # Default to last 90 days if no dates provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=90)
        
        # Fetch case data
        cases_list = await self._fetch_case_data(start_date, end_date, drug_filter)
        
        if not cases_list:
            logger.warning("No cases found for signal detection")
            return []
        
        logger.info(f"Analyzing {len(cases_list)} cases")
        
        # Run different algorithms
        all_signals = {}  # {(drug, event): DrugEventPair}
        
        # 1. BCPNN Analysis
        if use_bcpnn:
            bcpnn_results = self.bcpnn_engine.analyze_dataset(cases_list)
            self._merge_bcpnn_results(all_signals, bcpnn_results)
        
        # 2. PRR Analysis
        if use_prr:
            prr_results = self._calculate_prr_signals(cases_list)
            self._merge_prr_results(all_signals, prr_results)
        
        # 3. ROR Analysis
        if use_ror:
            ror_results = self._calculate_ror_signals(cases_list)
            self._merge_ror_results(all_signals, ror_results)
        
        # Apply consensus filtering if required
        signals = list(all_signals.values())
        
        if self.require_consensus:
            signals = [
                s for s in signals 
                if len(s.detection_methods) >= self.consensus_threshold
            ]
        
        # Sort by number of detection methods, then by IC
        signals.sort(
            key=lambda x: (len(x.detection_methods), x.ic or 0),
            reverse=True
        )
        
        logger.success(
            f"Signal detection complete | {len(signals)} signals detected | "
            f"BCPNN: {use_bcpnn}, PRR: {use_prr}, ROR: {use_ror}"
        )
        
        return signals
    
    def _merge_bcpnn_results(
        self,
        all_signals: Dict[Tuple[str, str], DrugEventPair],
        bcpnn_results: List[BCPNNResult]
    ):
        """Merge BCPNN results into signal collection"""
        for result in bcpnn_results:
            key = (result.drug.lower(), result.event.lower())
            
            if key in all_signals:
                # Update existing signal
                signal = all_signals[key]
                signal.ic = result.ic
                signal.ic_ci_lower = result.ic_lower
                signal.ic_ci_upper = result.ic_upper
                if result.is_signal:
                    signal.detection_methods.append("BCPNN")
                    signal.is_signal = True
            else:
                # Create new signal
                all_signals[key] = DrugEventPair(
                    drug_name=result.drug,
                    event_term=result.event,
                    count=result.count,
                    ic=result.ic,
                    ic_ci_lower=result.ic_lower,
                    ic_ci_upper=result.ic_upper,
                    is_signal=result.is_signal,
                    detection_methods=["BCPNN"] if result.is_signal else []
                )
    
    def _merge_prr_results(
        self,
        all_signals: Dict[Tuple[str, str], DrugEventPair],
        prr_results: List[Dict[str, Any]]
    ):
        """Merge PRR results into signal collection"""
        for result in prr_results:
            key = (result["drug"].lower(), result["event"].lower())
            
            if key in all_signals:
                signal = all_signals[key]
                signal.prr = result["prr"]
                signal.prr_ci_lower = result.get("prr_ci_lower")
                signal.prr_ci_upper = result.get("prr_ci_upper")
                if result["is_signal"]:
                    signal.detection_methods.append("PRR")
                    signal.is_signal = True
            else:
                all_signals[key] = DrugEventPair(
                    drug_name=result["drug"],
                    event_term=result["event"],
                    count=result["count"],
                    prr=result["prr"],
                    prr_ci_lower=result.get("prr_ci_lower"),
                    prr_ci_upper=result.get("prr_ci_upper"),
                    is_signal=result["is_signal"],
                    detection_methods=["PRR"] if result["is_signal"] else []
                )
    
    def _merge_ror_results(
        self,
        all_signals: Dict[Tuple[str, str], DrugEventPair],
        ror_results: List[Dict[str, Any]]
    ):
        """Merge ROR results into signal collection"""
        for result in ror_results:
            key = (result["drug"].lower(), result["event"].lower())
            
            if key in all_signals:
                signal = all_signals[key]
                signal.ror = result["ror"]
                signal.ror_ci_lower = result.get("ror_ci_lower")
                signal.ror_ci_upper = result.get("ror_ci_upper")
                if result["is_signal"]:
                    signal.detection_methods.append("ROR")
                    signal.is_signal = True
            else:
                all_signals[key] = DrugEventPair(
                    drug_name=result["drug"],
                    event_term=result["event"],
                    count=result["count"],
                    ror=result["ror"],
                    ror_ci_lower=result.get("ror_ci_lower"),
                    ror_ci_upper=result.get("ror_ci_upper"),
                    is_signal=result["is_signal"],
                    detection_methods=["ROR"] if result["is_signal"] else []
                )
    
    async def _fetch_case_data(
        self,
        start_date: datetime,
        end_date: datetime,
        drug_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch case data from database"""
        
        if self.db is None:
            logger.warning("No database client provided, returning empty list")
            return []
        
        # Query MongoDB
        query = {
            "received_date": {
                "$gte": start_date,
                "$lte": end_date
            },
            "status": {"$in": ["Validated", "Submitted", "Closed"]}
        }
        
        if drug_filter:
            query["suspect_products.product_name"] = {
                "$regex": drug_filter,
                "$options": "i"
            }
        
        # Fetch cases
        try:
            cases = await self.db.case_reports.find(query).to_list(length=None)
            return cases
        except Exception as e:
            logger.error(f"Error fetching cases: {str(e)}")
            return []
    
    def _calculate_prr_signals(
        self,
        cases: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calculate PRR for all drug-event pairs"""
        
        # Build contingency tables
        from collections import defaultdict
        
        pair_counts = defaultdict(int)
        drug_counts = defaultdict(int)
        event_counts = defaultdict(int)
        total = len(cases)
        
        for case in cases:
            drugs = set()
            for product in case.get("suspect_products", []):
                drug_name = product.get("product_name", "").strip()
                if drug_name:
                    drugs.add(drug_name.lower())
            
            events = set()
            for event in case.get("adverse_events", []):
                event_term = event.get("event_term", "").strip()
                if event_term:
                    events.add(event_term.lower())
            
            for drug in drugs:
                drug_counts[drug] += 1
                for event in events:
                    pair_counts[(drug, event)] += 1
            
            for event in events:
                event_counts[event] += 1
        
        # Calculate PRR for each pair
        results = []
        
        for (drug, event), count in pair_counts.items():
            if count < self.min_cases:
                continue
            
            # 2x2 table
            a = count
            b = drug_counts[drug] - a
            c = event_counts[event] - a
            d = total - a - b - c
            
            # Calculate PRR
            if (a + b) > 0 and (c + d) > 0:
                prr = (a / (a + b)) / (c / (c + d))
            else:
                prr = 0.0
            
            # Chi-square test
            chi2 = self._calculate_chi2(a, b, c, d)
            
            # PRR confidence interval (simplified)
            if prr > 0:
                se_log_prr = np.sqrt(1/a + 1/c - 1/(a+b) - 1/(c+d))
                prr_ci_lower = np.exp(np.log(prr) - 1.96 * se_log_prr)
                prr_ci_upper = np.exp(np.log(prr) + 1.96 * se_log_prr)
            else:
                prr_ci_lower = 0
                prr_ci_upper = 0
            
            is_signal = (
                prr >= self.prr_threshold and
                chi2 >= self.prr_chi2_threshold and
                count >= self.min_cases
            )
            
            results.append({
                "drug": drug.title(),
                "event": event.title(),
                "count": count,
                "prr": round(prr, 3),
                "prr_ci_lower": round(prr_ci_lower, 3),
                "prr_ci_upper": round(prr_ci_upper, 3),
                "chi2": round(chi2, 2),
                "is_signal": is_signal
            })
        
        return results
    
    def _calculate_ror_signals(
        self,
        cases: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calculate ROR for all drug-event pairs"""
        
        from collections import defaultdict
        
        pair_counts = defaultdict(int)
        drug_counts = defaultdict(int)
        event_counts = defaultdict(int)
        total = len(cases)
        
        for case in cases:
            drugs = set()
            for product in case.get("suspect_products", []):
                drug_name = product.get("product_name", "").strip()
                if drug_name:
                    drugs.add(drug_name.lower())
            
            events = set()
            for event in case.get("adverse_events", []):
                event_term = event.get("event_term", "").strip()
                if event_term:
                    events.add(event_term.lower())
            
            for drug in drugs:
                drug_counts[drug] += 1
                for event in events:
                    pair_counts[(drug, event)] += 1
            
            for event in events:
                event_counts[event] += 1
        
        # Calculate ROR for each pair
        results = []
        
        for (drug, event), count in pair_counts.items():
            if count < self.min_cases:
                continue
            
            # 2x2 table
            a = count
            b = drug_counts[drug] - a
            c = event_counts[event] - a
            d = total - a - b - c
            
            # Calculate ROR
            if b > 0 and c > 0:
                ror = (a * d) / (b * c)
            else:
                ror = 0.0
            
            # ROR confidence interval
            if a > 0 and b > 0 and c > 0 and d > 0 and ror > 0:
                se_log_ror = np.sqrt(1/a + 1/b + 1/c + 1/d)
                ror_ci_lower = np.exp(np.log(ror) - 1.96 * se_log_ror)
                ror_ci_upper = np.exp(np.log(ror) + 1.96 * se_log_ror)
            else:
                ror_ci_lower = 0
                ror_ci_upper = 0
            
            is_signal = ror_ci_lower > self.ror_ci_threshold
            
            results.append({
                "drug": drug.title(),
                "event": event.title(),
                "count": count,
                "ror": round(ror, 3),
                "ror_ci_lower": round(ror_ci_lower, 3),
                "ror_ci_upper": round(ror_ci_upper, 3),
                "is_signal": is_signal
            })
        
        return results
    
    def _calculate_chi2(self, a: int, b: int, c: int, d: int) -> float:
        """Calculate chi-square statistic for 2x2 table"""
        n = a + b + c + d
        if n == 0:
            return 0.0
        
        expected_a = (a + b) * (a + c) / n
        expected_b = (a + b) * (b + d) / n
        expected_c = (c + d) * (a + c) / n
        expected_d = (c + d) * (b + d) / n
        
        chi2 = 0.0
        for observed, expected in [(a, expected_a), (b, expected_b), 
                                    (c, expected_c), (d, expected_d)]:
            if expected > 0:
                chi2 += ((observed - expected) ** 2) / expected
        
        return chi2
    
    async def save_signals(self, signals: List[DrugEventPair]):
        """Save detected signals to database"""
        
        if self.db is None:
            logger.warning("No database client, cannot save signals")
            return
        
        for signal in signals:
            # Check if signal already exists
            existing = await self.db.signals.find_one({
                "drug_name": signal.drug_name,
                "event_term": signal.event_term,
                "signal_status": {"$in": ["New", "Under Review"]}
            })
            
            if not existing:
                # Insert new signal
                await self.db.signals.insert_one(signal.dict())
                logger.info(
                    f"New signal saved: {signal.drug_name} -> {signal.event_term} "
                    f"(Methods: {', '.join(signal.detection_methods)})"
                )
            else:
                # Update existing signal
                await self.db.signals.update_one(
                    {"_id": existing["_id"]},
                    {"$set": signal.dict()}
                )
                logger.info(
                    f"Signal updated: {signal.drug_name} -> {signal.event_term}"
                )


# Singleton instance
_signal_engine: Optional[EnhancedSignalDetectionEngine] = None

def get_signal_engine(database_client=None) -> EnhancedSignalDetectionEngine:
    """Get singleton signal detection engine instance"""
    global _signal_engine
    if _signal_engine is None:
        _signal_engine = EnhancedSignalDetectionEngine(database_client)
    return _signal_engine
