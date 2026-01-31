"""
Comprehensive Test Suite for BCPNN Implementation

Tests cover:
- Basic BCPNN calculations
- Signal detection logic
- Integration with existing code
- Edge cases and error handling
"""

import pytest
import numpy as np
from datetime import datetime
from bcpnn_engine import (
    BCPNNEngine,
    BCPNNResult,
    BCPNNIntegration,
    run_bcpnn_analysis,
    add_bcpnn_to_existing_signals
)


class TestBCPNNEngine:
    """Test suite for core BCPNN engine"""
    
    @pytest.fixture
    def bcpnn_engine(self):
        """Fixture providing a BCPNN engine instance"""
        return BCPNNEngine(min_count=3, ic_threshold=0.0)
    
    @pytest.fixture
    def sample_cases(self):
        """Fixture providing sample cases for testing"""
        return [
            {
                "suspect_products": [{"product_name": "Aspirin"}],
                "adverse_events": [{"event_term": "Headache"}]
            },
            {
                "suspect_products": [{"product_name": "Aspirin"}],
                "adverse_events": [{"event_term": "Headache"}]
            },
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
    
    def test_engine_initialization(self):
        """Test BCPNN engine initializes correctly"""
        engine = BCPNNEngine(min_count=5, ic_threshold=0.5)
        
        assert engine.min_count == 5
        assert engine.ic_threshold == 0.5
        assert engine.credibility_level == 0.95
    
    def test_basic_analysis(self, bcpnn_engine, sample_cases):
        """Test basic BCPNN analysis on sample data"""
        results = bcpnn_engine.analyze_dataset(sample_cases)
        
        assert len(results) > 0
        assert all(isinstance(r, BCPNNResult) for r in results)
    
    def test_drug_event_identification(self, bcpnn_engine, sample_cases):
        """Test correct identification of drug-event pairs"""
        results = bcpnn_engine.analyze_dataset(sample_cases)
        
        # Should find Aspirin-Headache pair
        aspirin_headache = next(
            (r for r in results 
             if r.drug.lower() == "aspirin" and r.event.lower() == "headache"),
            None
        )
        
        assert aspirin_headache is not None
        assert aspirin_headache.count == 3
    
    def test_signal_detection(self, bcpnn_engine):
        """Test signal detection logic"""
        # Create cases where DrugX + EventY is overrepresented
        cases = []
        
        # 15 cases with DrugX and EventY (strong association)
        for _ in range(15):
            cases.append({
                "suspect_products": [{"product_name": "DrugX"}],
                "adverse_events": [{"event_term": "EventY"}]
            })
        
        # 5 cases with DrugX and other events
        for i in range(5):
            cases.append({
                "suspect_products": [{"product_name": "DrugX"}],
                "adverse_events": [{"event_term": f"OtherEvent{i}"}]
            })
        
        # 5 cases with other drugs and EventY
        for i in range(5):
            cases.append({
                "suspect_products": [{"product_name": f"OtherDrug{i}"}],
                "adverse_events": [{"event_term": "EventY"}]
            })
        
        # 20 background cases (other drugs + other events)
        for i in range(20):
            cases.append({
                "suspect_products": [{"product_name": f"Drug{i}"}],
                "adverse_events": [{"event_term": f"Event{i}"}]
            })
        
        results = bcpnn_engine.analyze_dataset(cases)
        
        # Find DrugX-EventY pair
        target = next(
            (r for r in results 
             if r.drug.lower() == "drugx" and r.event.lower() == "eventy"),
            None
        )
        
        assert target is not None
        assert target.is_signal, "Should detect signal for overrepresented pair"
        assert target.ic > 0, "IC should be positive for signal"
        assert target.count == 15
    
    def test_no_signal_for_expected(self, bcpnn_engine):
        """Test that no signal is detected when counts are as expected"""
        # Create balanced dataset where everything is proportional
        cases = []
        
        # Equal distribution
        for drug in ["DrugA", "DrugB"]:
            for event in ["Event1", "Event2"]:
                for _ in range(5):
                    cases.append({
                        "suspect_products": [{"product_name": drug}],
                        "adverse_events": [{"event_term": event}]
                    })
        
        results = bcpnn_engine.analyze_dataset(cases)
        
        # All IC values should be close to 0
        for result in results:
            assert abs(result.ic) < 0.5, f"IC should be near 0 for balanced data: {result.ic}"
    
    def test_ic_credibility_intervals(self, bcpnn_engine, sample_cases):
        """Test that credibility intervals are properly calculated"""
        results = bcpnn_engine.analyze_dataset(sample_cases)
        
        for result in results:
            # Lower bound should be less than IC
            assert result.ic_lower <= result.ic, \
                f"IC lower ({result.ic_lower}) > IC ({result.ic})"
            
            # IC should be less than upper bound
            assert result.ic <= result.ic_upper, \
                f"IC ({result.ic}) > IC upper ({result.ic_upper})"
            
            # Interval should have positive width
            assert result.ic_upper > result.ic_lower, \
                "Credibility interval has zero width"
    
    def test_minimum_count_threshold(self):
        """Test that pairs below minimum count are excluded"""
        engine = BCPNNEngine(min_count=5)
        
        cases = [
            {
                "suspect_products": [{"product_name": "RareDrug"}],
                "adverse_events": [{"event_term": "RareEvent"}]
            }
        ] * 3  # Only 3 cases, below threshold of 5
        
        results = engine.analyze_dataset(cases)
        
        # Should not return results for pair with count < 5
        rare_pair = next(
            (r for r in results 
             if r.drug.lower() == "raredrug"),
            None
        )
        
        assert rare_pair is None, "Should exclude pairs below minimum count"
    
    def test_empty_dataset(self, bcpnn_engine):
        """Test handling of empty dataset"""
        results = bcpnn_engine.analyze_dataset([])
        
        assert len(results) == 0
    
    def test_case_normalization(self, bcpnn_engine):
        """Test that drug/event names are normalized (case-insensitive)"""
        cases = [
            {
                "suspect_products": [{"product_name": "ASPIRIN"}],
                "adverse_events": [{"event_term": "headache"}]
            },
            {
                "suspect_products": [{"product_name": "aspirin"}],
                "adverse_events": [{"event_term": "HEADACHE"}]
            },
            {
                "suspect_products": [{"product_name": "Aspirin"}],
                "adverse_events": [{"event_term": "Headache"}]
            }
        ]
        
        results = bcpnn_engine.analyze_dataset(cases)
        
        # Should combine all three into one pair
        aspirin_results = [r for r in results if r.drug.lower() == "aspirin"]
        
        assert len(aspirin_results) == 1
        assert aspirin_results[0].count == 3
    
    def test_multiple_drugs_per_case(self, bcpnn_engine):
        """Test handling of cases with multiple drugs"""
        cases = [
            {
                "suspect_products": [
                    {"product_name": "DrugA"},
                    {"product_name": "DrugB"}
                ],
                "adverse_events": [{"event_term": "Event1"}]
            }
        ] * 5
        
        results = bcpnn_engine.analyze_dataset(cases)
        
        # Should create pairs for both drugs
        druga_results = [r for r in results if r.drug.lower() == "druga"]
        drugb_results = [r for r in results if r.drug.lower() == "drugb"]
        
        assert len(druga_results) > 0
        assert len(drugb_results) > 0
    
    def test_multiple_events_per_case(self, bcpnn_engine):
        """Test handling of cases with multiple events"""
        cases = [
            {
                "suspect_products": [{"product_name": "Drug1"}],
                "adverse_events": [
                    {"event_term": "EventA"},
                    {"event_term": "EventB"}
                ]
            }
        ] * 5
        
        results = bcpnn_engine.analyze_dataset(cases)
        
        # Should create pairs for both events
        eventa_results = [r for r in results if r.event.lower() == "eventa"]
        eventb_results = [r for r in results if r.event.lower() == "eventb"]
        
        assert len(eventa_results) > 0
        assert len(eventb_results) > 0
    
    def test_single_pair_analysis(self, bcpnn_engine, sample_cases):
        """Test analysis of specific drug-event pair"""
        result = bcpnn_engine.calculate_single_pair(
            drug="Aspirin",
            event="Headache",
            cases=sample_cases
        )
        
        assert result is not None
        assert result.drug.lower() == "aspirin"
        assert result.event.lower() == "headache"
        assert result.count == 3
    
    def test_single_pair_not_found(self, bcpnn_engine, sample_cases):
        """Test single pair analysis when pair doesn't exist"""
        result = bcpnn_engine.calculate_single_pair(
            drug="Nonexistent",
            event="FakeEvent",
            cases=sample_cases
        )
        
        assert result is None


class TestBCPNNIntegration:
    """Test suite for BCPNN integration layer"""
    
    @pytest.fixture
    def integration(self):
        """Fixture providing BCPNN integration instance"""
        return BCPNNIntegration()
    
    @pytest.fixture
    def sample_cases(self):
        """Sample cases for integration testing"""
        return [
            {
                "suspect_products": [{"product_name": "DrugA"}],
                "adverse_events": [{"event_term": "Event1"}]
            }
        ] * 10 + [
            {
                "suspect_products": [{"product_name": "DrugB"}],
                "adverse_events": [{"event_term": "Event2"}]
            }
        ] * 5
    
    def test_enhance_with_bcpnn(self, integration, sample_cases):
        """Test enhancing existing signals with BCPNN metrics"""
        # Existing PRR signals
        prr_signals = [
            {
                "drug": "DrugA",
                "reaction": "Event1",
                "prr_score": 2.5,
                "case_count": 10
            }
        ]
        
        enhanced = integration.enhance_signal_detection(sample_cases, prr_signals)
        
        assert len(enhanced) > 0
        assert "ic" in enhanced[0]
        assert "ic_lower" in enhanced[0]
        assert "ic_upper" in enhanced[0]
    
    def test_bcpnn_only_signals(self, integration, sample_cases):
        """Test generating signals using only BCPNN"""
        signals = integration.enhance_signal_detection(sample_cases, None)
        
        assert len(signals) > 0
        assert all("ic" in s for s in signals)


class TestConvenienceFunctions:
    """Test suite for convenience functions"""
    
    def test_run_bcpnn_analysis(self):
        """Test convenience function for running BCPNN"""
        cases = [
            {
                "suspect_products": [{"product_name": "TestDrug"}],
                "adverse_events": [{"event_term": "TestEvent"}]
            }
        ] * 5
        
        signals = run_bcpnn_analysis(cases, min_count=3)
        
        assert isinstance(signals, list)
        assert all(isinstance(s, dict) for s in signals)
    
    def test_add_bcpnn_to_existing(self):
        """Test adding BCPNN to existing signals"""
        cases = [
            {
                "suspect_products": [{"product_name": "Drug"}],
                "adverse_events": [{"event_term": "Event"}]
            }
        ] * 10
        
        existing = [
            {
                "drug": "Drug",
                "reaction": "Event",
                "prr_score": 2.0
            }
        ]
        
        enhanced = add_bcpnn_to_existing_signals(cases, existing)
        
        assert len(enhanced) > 0
        assert "ic" in enhanced[0] or "prr_score" in enhanced[0]


class TestBCPNNResult:
    """Test suite for BCPNNResult dataclass"""
    
    def test_result_creation(self):
        """Test BCPNNResult can be created"""
        result = BCPNNResult(
            drug="Aspirin",
            event="Headache",
            count=10,
            expected_count=3.5,
            ic=1.5,
            ic_lower=0.5,
            ic_upper=2.5,
            is_signal=True,
            total_reports=100,
            drug_margin=30,
            event_margin=25
        )
        
        assert result.drug == "Aspirin"
        assert result.count == 10
        assert result.is_signal is True
    
    def test_result_to_dict(self):
        """Test conversion to dictionary"""
        result = BCPNNResult(
            drug="Drug",
            event="Event",
            count=5,
            expected_count=2.0,
            ic=1.0,
            ic_lower=0.2,
            ic_upper=1.8,
            is_signal=True,
            total_reports=50,
            drug_margin=10,
            event_margin=15
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["drug"] == "Drug"
        assert result_dict["ic"] == 1.0
        assert "signal_strength" in result_dict
    
    def test_signal_strength_classification(self):
        """Test signal strength classification"""
        # Very strong signal
        strong = BCPNNResult(
            drug="D", event="E", count=10, expected_count=1,
            ic=3.5, ic_lower=2.5, ic_upper=4.5, is_signal=True,
            total_reports=100, drug_margin=20, event_margin=15
        )
        assert strong._classify_signal_strength() == "Very Strong"
        
        # Weak signal
        weak = BCPNNResult(
            drug="D", event="E", count=5, expected_count=3,
            ic=0.5, ic_lower=0.1, ic_upper=0.9, is_signal=True,
            total_reports=100, drug_margin=20, event_margin=15
        )
        assert weak._classify_signal_strength() == "Weak"
        
        # No signal
        none_sig = BCPNNResult(
            drug="D", event="E", count=3, expected_count=3,
            ic=0.0, ic_lower=-0.5, ic_upper=0.5, is_signal=False,
            total_reports=100, drug_margin=20, event_margin=15
        )
        assert none_sig._classify_signal_strength() == "No Signal"


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_zero_cases(self):
        """Test with zero cases"""
        engine = BCPNNEngine()
        results = engine.analyze_dataset([])
        
        assert len(results) == 0
    
    def test_missing_fields(self):
        """Test cases with missing fields"""
        engine = BCPNNEngine(min_count=1)
        
        cases = [
            {},  # Completely empty
            {"suspect_products": []},  # Empty products
            {"adverse_events": []},  # Empty events
            {"suspect_products": [{}]},  # Empty product dict
            {"adverse_events": [{}]}  # Empty event dict
        ]
        
        # Should not crash
        results = engine.analyze_dataset(cases)
        
        # Should return empty results
        assert len(results) == 0
    
    def test_very_large_dataset(self):
        """Test performance with larger dataset"""
        engine = BCPNNEngine()
        
        # Create 1000 cases
        cases = []
        for i in range(100):
            for j in range(10):
                cases.append({
                    "suspect_products": [{"product_name": f"Drug{i%10}"}],
                    "adverse_events": [{"event_term": f"Event{j%5}"}]
                })
        
        # Should complete without error
        results = engine.analyze_dataset(cases)
        
        assert len(results) > 0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
