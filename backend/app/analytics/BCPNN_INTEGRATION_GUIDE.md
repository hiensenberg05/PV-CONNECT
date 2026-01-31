# BCPNN Integration Guide for PV-CONNECT

Complete guide for integrating Bayesian Confidence Propagation Neural Network (BCPNN) signal detection into your existing pharmacovigilance system.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [What is BCPNN?](#what-is-bcpnn)
3. [Files Provided](#files-provided)
4. [Integration Steps](#integration-steps)
5. [Usage Examples](#usage-examples)
6. [API Endpoints](#api-endpoints)
7. [Comparison with PRR](#comparison-with-prr)
8. [Testing](#testing)

---

## 🚀 Quick Start

### Option 1: Drop-in Replacement for analytics_engine.py

```python
# Replace your existing analytics_engine.py with:
from analytics_engine_enhanced import (
    AnalyticsAggregator,
    EnhancedSignalDetector,
    VigiGradeScorer
)

# Your existing code continues to work!
aggregator = AnalyticsAggregator(use_bcpnn=True)
summary = aggregator.generate_dashboard_summary(cases)
```

### Option 2: Add BCPNN to Existing Code

```python
# Keep your existing code, just add BCPNN
from bcpnn_engine import run_bcpnn_analysis

# Your existing PRR code...
prr_signals = signal_detector.detect_signals(cases)

# Add BCPNN analysis
bcpnn_signals = run_bcpnn_analysis(cases, min_count=3)

# Combine results
all_signals = prr_signals + bcpnn_signals
```

---

## 📖 What is BCPNN?

### Overview

BCPNN (Bayesian Confidence Propagation Neural Network) is a sophisticated signal detection algorithm developed by the **WHO Uppsala Monitoring Centre** (UMC) for the VigiBase database.

### Key Advantages

✅ **Bayesian Approach**: Uses prior probabilities for more stable estimates  
✅ **Better for Small Counts**: Handles rare events better than PRR  
✅ **Credibility Intervals**: Provides uncertainty quantification  
✅ **WHO Standard**: Same method used by VigiBase (world's largest AE database)

### The Information Component (IC)

The core metric is the **Information Component (IC)**:

```
IC = log₂(P(drug, event) / (P(drug) × P(event)))
```

- **IC > 0**: Drug-event pair reported more than expected
- **IC < 0**: Reported less than expected
- **Signal**: When IC_lower (lower bound of 95% CI) > 0

### Comparison with PRR

| Metric | PRR | BCPNN (IC) |
|--------|-----|-----------|
| **Formula** | (a/(a+b)) / (c/(c+d)) | log₂(observed/expected) |
| **Best For** | Frequent events | All events, especially rare |
| **Handles Small Counts** | Poor | Excellent (Bayesian shrinkage) |
| **Uncertainty** | Requires separate CI | Built-in credibility interval |
| **Threshold** | PRR ≥ 2 | IC_lower > 0 |
| **Used By** | FDA, EMA | WHO, UMC |

---

## 📦 Files Provided

### 1. `bcpnn_engine.py` (Core Implementation)

**Main Components:**
- `BCPNNEngine`: Core BCPNN calculation engine
- `BCPNNResult`: Data class for results
- `BCPNNIntegration`: Helper for integrating with existing code

**Key Features:**
- Full BCPNN algorithm implementation
- Bayesian shrinkage with informative priors
- Credibility interval calculation
- Single-pair and batch analysis

### 2. `enhanced_signal_detection.py` (Full Integration)

**Main Components:**
- `EnhancedSignalDetectionEngine`: Multi-algorithm detection
- Combines PRR, ROR, and BCPNN
- Consensus detection across methods
- Async database operations

**Use When:**
- You want all three algorithms (PRR, ROR, BCPNN)
- Need database integration
- Want consensus-based detection

### 3. `analytics_engine_enhanced.py` (Drop-in Replacement)

**Main Components:**
- `AnalyticsAggregator`: Enhanced with BCPNN
- `EnhancedSignalDetector`: PRR + BCPNN
- `VigiGradeScorer`: Unchanged from original

**Use When:**
- Easiest migration path
- Maintains backward compatibility
- Want to switch algorithms via parameter

---

## 🔧 Integration Steps

### Step 1: Add Files to Your Project

```bash
# Copy the BCPNN files to your project
cp bcpnn_engine.py /path/to/your/project/app/analytics/
cp analytics_engine_enhanced.py /path/to/your/project/app/analytics/

# Or use enhanced signal detection (full-featured)
cp enhanced_signal_detection.py /path/to/your/project/app/analytics/
```

### Step 2: Install Dependencies

```bash
pip install numpy loguru
```

### Step 3: Choose Your Integration Method

#### Method A: Replace analytics_engine.py (Easiest)

```python
# In your existing code, just update the import:
# OLD:
# from app.analytics.analytics_engine import AnalyticsAggregator

# NEW:
from app.analytics.analytics_engine_enhanced import AnalyticsAggregator

# Everything else stays the same!
aggregator = AnalyticsAggregator(use_bcpnn=True)
```

#### Method B: Use Side-by-Side (Most Flexible)

```python
# Keep your existing analytics_engine.py
# Import BCPNN separately
from app.analytics.bcpnn_engine import run_bcpnn_analysis
from app.analytics.analytics_engine import SignalDetector

# Use both
prr_signals = SignalDetector().detect_signals(cases)
bcpnn_signals = run_bcpnn_analysis(cases)

# Merge results
all_signals = merge_signals(prr_signals, bcpnn_signals)
```

#### Method C: Full Enhanced Engine (Most Features)

```python
from app.analytics.enhanced_signal_detection import get_signal_engine

# Initialize with database
engine = get_signal_engine(database_client=mongodb_client)

# Run multi-algorithm detection
signals = await engine.run_signal_detection(
    start_date=start,
    end_date=end,
    use_bcpnn=True,
    use_prr=True,
    use_ror=True
)

# Signals now have metrics from all methods!
for signal in signals:
    print(f"{signal.drug_name} -> {signal.event_term}")
    print(f"  PRR: {signal.prr}, IC: {signal.ic}")
    print(f"  Detected by: {signal.detection_methods}")
```

---

## 💻 Usage Examples

### Example 1: Basic BCPNN Analysis

```python
from bcpnn_engine import BCPNNEngine

# Initialize engine
bcpnn = BCPNNEngine(min_count=3, ic_threshold=0.0)

# Your cases from MongoDB
cases = [
    {
        "suspect_products": [{"product_name": "Aspirin"}],
        "adverse_events": [{"event_term": "Headache"}]
    },
    # ... more cases
]

# Run analysis
results = bcpnn.analyze_dataset(cases)

# Print signals
for result in results:
    if result.is_signal:
        print(f"{result.drug} - {result.event}")
        print(f"  Count: {result.count}")
        print(f"  IC: {result.ic:.3f} [{result.ic_lower:.3f}, {result.ic_upper:.3f}]")
        print(f"  Signal Strength: {result._classify_signal_strength()}")
```

### Example 2: Compare PRR and BCPNN

```python
from bcpnn_engine import BCPNNIntegration

integration = BCPNNIntegration()

# Compare algorithms
comparison = integration.compare_algorithms(cases)

print(f"Total cases: {comparison['total_cases']}")
print(f"PRR signals: {comparison['prr_signals']}")
print(f"BCPNN signals: {comparison['bcpnn_signals']}")
print(f"Detected by both: {comparison['both_methods']}")
print(f"Agreement rate: {comparison['agreement_rate']}%")
```

### Example 3: Enhanced Dashboard

```python
from analytics_engine_enhanced import AnalyticsAggregator

aggregator = AnalyticsAggregator(use_bcpnn=True)

# Generate summary with BCPNN
summary = aggregator.generate_dashboard_summary(
    all_cases=cases,
    signal_algorithm="all"  # Use both PRR and BCPNN
)

print(f"Signals detected: {summary['signals_detected']}")
print(f"Signal breakdown:")
print(f"  PRR only: {summary['signal_breakdown']['prr_only']}")
print(f"  BCPNN only: {summary['signal_breakdown']['bcpnn_only']}")
print(f"  Both methods: {summary['signal_breakdown']['detected_by_both']}")

# Display top signals
for signal in summary['signals'][:5]:
    print(f"\n{signal['drug']} -> {signal['reaction']}")
    print(f"  Cases: {signal['case_count']}")
    if 'prr_score' in signal:
        print(f"  PRR: {signal['prr_score']:.2f}")
    if 'ic' in signal:
        print(f"  IC: {signal['ic']:.3f} [{signal['ic_lower']:.3f}, {signal['ic_upper']:.3f}]")
    print(f"  Detected by: {', '.join(signal.get('detection_methods', []))}")
```

### Example 4: Single Drug-Event Pair Analysis

```python
from bcpnn_engine import BCPNNEngine

bcpnn = BCPNNEngine()

# Analyze specific pair
result = bcpnn.calculate_single_pair(
    drug="Aspirin",
    event="Gastrointestinal Bleeding",
    cases=all_cases
)

if result:
    print(f"Analysis for Aspirin - GI Bleeding:")
    print(f"  Observed: {result.count} cases")
    print(f"  Expected: {result.expected_count:.1f} cases")
    print(f"  IC: {result.ic:.3f}")
    print(f"  95% CI: [{result.ic_lower:.3f}, {result.ic_upper:.3f}]")
    print(f"  Signal: {'YES' if result.is_signal else 'NO'}")
```

---

## 🌐 API Endpoints

If you're using the enhanced signal detection with FastAPI, you can add these endpoints:

### Add BCPNN Endpoint

```python
# In your FastAPI router
from fastapi import APIRouter
from bcpnn_engine import run_bcpnn_analysis

router = APIRouter()

@router.post("/api/v1/signals/bcpnn")
async def detect_bcpnn_signals(
    min_count: int = 3,
    ic_threshold: float = 0.0,
    db = Depends(get_database)
):
    """Run BCPNN signal detection"""
    
    # Fetch cases
    cases = await db.cases.find({}).to_list(length=None)
    
    # Run BCPNN
    signals = run_bcpnn_analysis(
        cases,
        min_count=min_count,
        ic_threshold=ic_threshold
    )
    
    return {
        "total_cases": len(cases),
        "signals_detected": len(signals),
        "signals": signals
    }

@router.get("/api/v1/signals/compare")
async def compare_algorithms(db = Depends(get_database)):
    """Compare PRR and BCPNN results"""
    
    from bcpnn_engine import BCPNNIntegration
    
    cases = await db.cases.find({}).to_list(length=None)
    
    integration = BCPNNIntegration()
    comparison = integration.compare_algorithms(cases)
    
    return comparison
```

---

## 📊 Comparison with PRR

### When to Use BCPNN vs PRR

**Use BCPNN when:**
- ✅ You have rare events (few reports)
- ✅ You want WHO-standard methodology
- ✅ You need better handling of uncertainty
- ✅ Comparing to international databases (VigiBase)

**Use PRR when:**
- ✅ You have many reports per pair
- ✅ Regulatory requirement (FDA FAERS)
- ✅ Simpler interpretation needed
- ✅ Computational efficiency critical

**Use Both when:**
- ✅ You want robust detection (consensus)
- ✅ Comparing different methodologies
- ✅ Research or validation studies

### Example Output Comparison

```python
# Same drug-event pair analyzed with both methods

PRR Analysis:
  Aspirin - Headache
  Cases: 5
  PRR: 3.2 (95% CI: 1.1 - 9.4)
  Signal: YES (PRR > 2)

BCPNN Analysis:
  Aspirin - Headache
  Cases: 5
  IC: 1.68 (95% CI: 0.23 - 3.13)
  Signal: YES (IC_lower > 0)
  Expected: 1.8 cases
  Observed/Expected ratio: 2.8x
```

---

## 🧪 Testing

### Unit Tests for BCPNN

```python
import pytest
from bcpnn_engine import BCPNNEngine, BCPNNResult

def test_bcpnn_basic():
    """Test basic BCPNN calculation"""
    bcpnn = BCPNNEngine(min_count=1)
    
    cases = [
        {
            "suspect_products": [{"product_name": "DrugA"}],
            "adverse_events": [{"event_term": "EventX"}]
        },
        {
            "suspect_products": [{"product_name": "DrugA"}],
            "adverse_events": [{"event_term": "EventX"}]
        },
        {
            "suspect_products": [{"product_name": "DrugA"}],
            "adverse_events": [{"event_term": "EventX"}]
        }
    ]
    
    results = bcpnn.analyze_dataset(cases)
    
    assert len(results) > 0
    assert results[0].drug.lower() == "druga"
    assert results[0].event.lower() == "eventx"
    assert results[0].count == 3

def test_signal_detection():
    """Test signal detection logic"""
    bcpnn = BCPNNEngine(min_count=3)
    
    # Create cases where DrugX + EventY is overrepresented
    cases = []
    
    # 10 cases with DrugX and EventY (overrepresented)
    for _ in range(10):
        cases.append({
            "suspect_products": [{"product_name": "DrugX"}],
            "adverse_events": [{"event_term": "EventY"}]
        })
    
    # 5 cases with DrugX and other events
    for i in range(5):
        cases.append({
            "suspect_products": [{"product_name": "DrugX"}],
            "adverse_events": [{"event_term": f"Event{i}"}]
        })
    
    # 5 cases with other drugs and EventY
    for i in range(5):
        cases.append({
            "suspect_products": [{"product_name": f"Drug{i}"}],
            "adverse_events": [{"event_term": "EventY"}]
        })
    
    results = bcpnn.analyze_dataset(cases)
    
    # Find the DrugX-EventY pair
    target = next(
        (r for r in results if r.drug.lower() == "drugx" and r.event.lower() == "eventy"),
        None
    )
    
    assert target is not None
    assert target.is_signal  # Should be a signal due to overrepresentation
    assert target.ic > 0  # IC should be positive

def test_credibility_interval():
    """Test that credibility intervals are calculated"""
    bcpnn = BCPNNEngine()
    
    cases = [
        {
            "suspect_products": [{"product_name": "TestDrug"}],
            "adverse_events": [{"event_term": "TestEvent"}]
        }
    ] * 5
    
    results = bcpnn.analyze_dataset(cases)
    
    if results:
        result = results[0]
        assert result.ic_lower <= result.ic
        assert result.ic <= result.ic_upper
        assert result.ic_upper > result.ic_lower
```

### Integration Tests

```python
import pytest
from analytics_engine_enhanced import AnalyticsAggregator

@pytest.mark.asyncio
async def test_dashboard_with_bcpnn():
    """Test dashboard generation with BCPNN enabled"""
    
    # Sample cases
    cases = [
        {
            "suspect_products": [{"product_name": "Aspirin"}],
            "adverse_events": [{"event_term": "Headache"}],
            "patient": {"age": 45, "sex": "M"},
            "narrative": "Patient experienced headache",
            "causality_assessment": "Possible"
        }
    ] * 10
    
    aggregator = AnalyticsAggregator(use_bcpnn=True)
    summary = aggregator.generate_dashboard_summary(cases, signal_algorithm="all")
    
    assert summary["total_cases"] == 10
    assert summary["bcpnn_enabled"] is True
    assert "signal_breakdown" in summary
    assert len(summary["signals"]) > 0
```

---

## 🔍 Troubleshooting

### Issue: "BCPNN not available"

**Cause**: bcpnn_engine.py not found or import error

**Solution**:
```python
# Check if BCPNN is available
try:
    from bcpnn_engine import BCPNNEngine
    print("BCPNN available ✓")
except ImportError as e:
    print(f"BCPNN not available: {e}")
```

### Issue: Different results from PRR and BCPNN

**This is expected!** They use different methodologies:
- PRR: Simple ratio, can be unstable for rare events
- BCPNN: Bayesian approach with shrinkage, more conservative

**Both detecting a signal = Strong evidence**  
**Only one detecting = Warrants investigation**

### Issue: IC values seem different from literature

BCPNN IC can be calibrated differently. Our implementation uses:
- Prior parameters: α=0.5, β=0.5, γ=0.5
- These can be adjusted in `BCPNNEngine.__init__()`

---

## 📚 References

1. Bate, A. et al. (1998) "A Bayesian neural network method for adverse drug reaction signal generation"
2. Norén, G.N. et al. (2006) "Shrinkage observed-to-expected ratios for robust and transparent large-scale pattern discovery"
3. WHO UMC VigiBase methodology documentation

---

## 🎯 Next Steps

1. ✅ Add bcpnn_engine.py to your project
2. ✅ Choose integration method (A, B, or C)
3. ✅ Update imports in your code
4. ✅ Test with sample data
5. ✅ Compare PRR and BCPNN results
6. ✅ Update dashboard to show both methods
7. ✅ Deploy and monitor

---

## 💬 Support

For issues or questions:
- Review the code comments in `bcpnn_engine.py`
- Check the examples in this guide
- Compare with WHO UMC methodology papers
- Test with known drug-event pairs

**Happy Signal Detecting! 🎉**
