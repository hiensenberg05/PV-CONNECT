# BCPNN Quick Reference Card

## 🚀 Quick Start (3 Lines of Code)

```python
from bcpnn_engine import run_bcpnn_analysis
signals = run_bcpnn_analysis(your_cases, min_count=3)
print(f"Found {len(signals)} signals!")
```

## 📊 Key Metrics

| Metric | Formula | Threshold | Interpretation |
|--------|---------|-----------|----------------|
| **IC** | log₂(observed/expected) | IC_lower > 0 | Signal strength |
| **IC_lower** | IC - 1.96×SD | > 0 | 95% CI lower bound |
| **IC_upper** | IC + 1.96×SD | - | 95% CI upper bound |

## 🎯 Signal Strength

| IC Value | Signal Strength | Action |
|----------|----------------|--------|
| IC > 3.0 | Very Strong | Immediate review |
| IC 2.0-3.0 | Strong | Priority investigation |
| IC 1.0-2.0 | Moderate | Monitor closely |
| IC 0-1.0 | Weak | Continue monitoring |
| IC < 0 | No signal | Expected or less |

## 🔧 Common Usage Patterns

### Pattern 1: Standalone BCPNN

```python
from bcpnn_engine import BCPNNEngine

bcpnn = BCPNNEngine(min_count=3, ic_threshold=0.0)
results = bcpnn.analyze_dataset(cases)

for r in results:
    if r.is_signal:
        print(f"{r.drug} - {r.event}: IC={r.ic:.2f}")
```

### Pattern 2: Add to Existing PRR Signals

```python
from bcpnn_engine import add_bcpnn_to_existing_signals

# Your existing PRR signals
prr_signals = [...]

# Enhance with BCPNN
enhanced = add_bcpnn_to_existing_signals(cases, prr_signals)

# Now each signal has both PRR and IC
for s in enhanced:
    print(f"PRR: {s.get('prr_score')}, IC: {s.get('ic')}")
```

### Pattern 3: Use Enhanced Analytics Engine

```python
from analytics_engine_enhanced import AnalyticsAggregator

agg = AnalyticsAggregator(use_bcpnn=True)
summary = agg.generate_dashboard_summary(cases, algorithm="all")

print(f"PRR only: {summary['signal_breakdown']['prr_only']}")
print(f"BCPNN only: {summary['signal_breakdown']['bcpnn_only']}")
print(f"Both: {summary['signal_breakdown']['detected_by_both']}")
```

### Pattern 4: Compare Algorithms

```python
from bcpnn_engine import BCPNNIntegration

integration = BCPNNIntegration()
comparison = integration.compare_algorithms(cases)

print(f"Agreement: {comparison['agreement_rate']}%")
print(f"BCPNN only: {comparison['bcpnn_only']}")
print(f"PRR only: {comparison['prr_only']}")
```

## 🎨 Integration Options

### Option A: Replace analytics_engine.py

```python
# Just change import
from analytics_engine_enhanced import AnalyticsAggregator
# All existing code works!
```

### Option B: Side-by-Side

```python
from analytics_engine import SignalDetector  # Existing
from bcpnn_engine import BCPNNEngine  # New

prr = SignalDetector().detect_signals(cases)
bcpnn = BCPNNEngine().analyze_dataset(cases)
```

### Option C: Full Enhanced Engine

```python
from enhanced_signal_detection import get_signal_engine

engine = get_signal_engine(db_client)
signals = await engine.run_signal_detection(
    use_prr=True,
    use_ror=True,
    use_bcpnn=True
)
```

## 📋 Interpreting Results

```python
# Example BCPNN Result
{
    "drug": "Aspirin",
    "event": "Gastrointestinal Bleeding",
    "count": 25,                    # Observed cases
    "expected_count": 8.5,          # Expected under independence
    "ic": 1.55,                     # Information Component
    "ic_lower": 0.82,               # Lower 95% CI (>0 = signal!)
    "ic_upper": 2.28,               # Upper 95% CI
    "is_signal": true,              # IC_lower > 0
    "signal_strength": "Moderate",  # Based on IC value
}
```

## 🔍 BCPNN vs PRR Comparison

```
Same Pair Analysis:

PRR:
  Observed: 25 cases
  PRR: 2.94 (CI: 1.89 - 4.58)
  Signal: YES (PRR > 2.0)

BCPNN:
  Observed: 25 cases
  Expected: 8.5 cases
  IC: 1.55 (CI: 0.82 - 2.28)
  Signal: YES (IC_lower > 0)
  
Interpretation:
  Both methods agree → Strong signal
  Aspirin-GI Bleeding reported 2.94x more than expected
```

## ⚙️ Configuration

```python
BCPNNEngine(
    min_count=3,         # Minimum reports required
    ic_threshold=0.0,    # IC_lower threshold for signal
    credibility_level=0.95  # 95% credibility interval
)

# Adjust prior parameters (advanced)
bcpnn.alpha_prior = 0.5  # Drug-event prior
bcpnn.beta_prior = 0.5   # Drug margin prior
bcpnn.gamma_prior = 0.5  # Event margin prior
```

## 🧪 Testing

```bash
# Run all tests
pytest test_bcpnn.py -v

# Run specific test
pytest test_bcpnn.py::TestBCPNNEngine::test_signal_detection -v

# With coverage
pytest test_bcpnn.py --cov=bcpnn_engine --cov-report=html
```

## 🐛 Common Issues

### Issue: No signals detected

**Check:**
- Minimum count threshold (default: 3)
- IC threshold (default: 0.0)
- Data format (correct field names)

```python
# Debug mode
bcpnn = BCPNNEngine(min_count=1, ic_threshold=-1.0)
results = bcpnn.analyze_dataset(cases)
print(f"Total pairs analyzed: {len(results)}")
```

### Issue: Different results from literature

BCPNN has parameters that can vary:
- Prior parameters (α, β, γ)
- Credibility level (95% vs 99%)
- Minimum count threshold

**Our defaults match WHO UMC VigiBase methodology**

### Issue: Performance on large datasets

BCPNN is O(n×m) where n=drugs, m=events

**Optimization tips:**
- Filter cases by date range
- Pre-filter by case count threshold
- Use specific drug/event subsets for targeted analysis

## 📚 Further Reading

- **Integration Guide**: `BCPNN_INTEGRATION_GUIDE.md`
- **Source Code**: `bcpnn_engine.py`
- **Tests**: `test_bcpnn.py`
- **Enhanced Engine**: `enhanced_signal_detection.py`

## 💡 Pro Tips

1. **Use both algorithms**: PRR + BCPNN provides robust detection
2. **Trust consensus**: Signals detected by both are high priority
3. **BCPNN for rare events**: Better than PRR for low counts
4. **Check credibility intervals**: Wide intervals = high uncertainty
5. **Monitor IC trends**: Watch for IC changes over time

## ⚡ One-Liners

```python
# Quick signal count
len([r for r in bcpnn.analyze_dataset(cases) if r.is_signal])

# Top 5 signals by IC
sorted(results, key=lambda r: r.ic, reverse=True)[:5]

# Filter strong signals only
[r for r in results if r.is_signal and r.ic >= 2.0]

# Get all Aspirin signals
[r for r in results if 'aspirin' in r.drug.lower()]

# Count by detection method
sum(1 for s in signals if 'BCPNN' in s.get('detection_methods', []))
```

## 📞 Support Checklist

Before asking for help, verify:
- ✅ BCPNN module imported successfully
- ✅ Case data in correct format
- ✅ Minimum count threshold reasonable
- ✅ Tests pass (`pytest test_bcpnn.py`)
- ✅ Checked integration guide

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Compatible With**: PV-CONNECT, VigiGrade System
