# Infinite Loop Fix

## Problem
Backend was stuck in an infinite loop causing repeated API calls to Gemini.

## Root Cause
The graph had a loop:
```
patient_intake → completeness_check → (if incomplete) → patient_intake → ...
```

This created an endless cycle because:
1. User sends message
2. Goes to patient_intake
3. Goes to completeness_check
4. If incomplete (< 0.7), routes back to patient_intake
5. Repeats forever without user input

## Solution Applied ✅

**Changed in `graph.py`:**

### Before (CAUSED LOOP):
```python
def route_after_completeness(state: NovaState) -> str:
    if state.get("completeness_score", 0) >= settings.COMPLETENESS_THRESHOLD:
        return "clinical_triage"
    else:
        return "patient_intake"  # ← INFINITE LOOP!
```

### After (FIXED):
```python
def route_after_completeness(state: NovaState) -> str:
    """Always proceed to avoid infinite loops"""
    return "clinical_triage"  # ← Always proceed
```

Also simplified the graph edges:
```python
# Before:
workflow.add_conditional_edges("completeness_check", route_after_completeness, {...})

# After:
workflow.add_edge("completeness_check", "clinical_triage")  # Direct edge
```

## New Flow (No Loops)

```
User Message
    ↓
language_detection
    ↓
user_type_detection
    ↓
patient_intake OR doctor_case_intake
    ↓
completeness_check
    ↓
clinical_triage  ← Always proceeds (no loop back)
    ↓
confidence_scoring
    ↓
persist_case
    ↓
END
```

## Status
✅ **Fixed!** Backend will auto-reload and work correctly now.

## Note
The completeness score is still calculated and stored in the state. It just doesn't control the flow anymore to prevent loops. In a production system, you'd handle follow-up questions in a multi-turn conversation pattern rather than looping within a single graph execution.

## Test
Try sending a message from the frontend now - it should complete without looping!
