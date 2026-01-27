# Node Connections - Fixed Routing

## Issue Identified
When a patient provides information manually and the system routes to `patient_intake`, subsequent messages were incorrectly routing back to `patient_doc_request` instead of continuing in `patient_intake`.

## Root Cause
1. **Entry Point Always Starts**: LangGraph always starts from the entry point (`initial_classification`)
2. **State Not Preserved**: When loading state from MongoDB, `current_node` wasn't being checked properly
3. **Routing Logic**: `route_after_user_type` didn't check for existing workflow state

## Fixes Applied

### 1. Updated `initial_classification_node` (lines 93-99)
- Now checks if we're continuing an existing workflow
- If `current_node` is set and not at start, returns state immediately
- Skips re-classification for existing cases

### 2. Updated `route_after_user_type` (lines 720-750)
- **First checks `current_node`** to continue existing workflow
- Maps `current_node` values to actual graph node names
- Only does new workflow routing if no `current_node` is set

### 3. Updated Graph Edges (lines 825-840)
- Added all possible nodes to `initial_classification` routing map
- Includes: `patient_intake`, `doctor_case_intake`, `completeness_check`, etc.

## Complete Node Flow

```
Entry: initial_classification
  ↓
  ├─→ If continuing workflow → Route to current_node
  ├─→ If new patient → patient_doc_request
  ├─→ If new doctor → doctor_registry_check
  └─→ If awaiting user type → END

patient_doc_request
  ↓
  ├─→ If image uploaded → document_extraction
  ├─→ If skip detected → patient_intake
  └─→ Otherwise → END (wait for next message)

document_extraction
  ↓
  ├─→ If error/skip → patient_intake
  └─→ Otherwise → completeness_check

patient_intake
  ↓
  └─→ completeness_check

doctor_case_intake
  ↓
  └─→ completeness_check

completeness_check
  ↓
  ├─→ If complete (≥0.7) → clinical_triage
  ├─→ If incomplete + patient → patient_intake (via END, then route back)
  ├─→ If incomplete + doctor → doctor_case_intake (via END, then route back)
  └─→ If user gives up → doctor_handoff

clinical_triage
  ↓
  └─→ confidence_scoring

confidence_scoring
  ↓
  └─→ persist_case

persist_case
  ↓
  └─→ END
```

## Key Routing Logic

### When Continuing Existing Case:
1. State loaded from MongoDB with `current_node` set
2. `initial_classification_node` detects existing workflow → returns early
3. `route_after_user_type` checks `current_node` → routes to correct node
4. Workflow continues from where it left off

### When Starting New Case:
1. No `current_node` set
2. `initial_classification_node` does full classification
3. `route_after_user_type` routes based on `sender_type`
4. Workflow starts fresh

## Testing Scenarios

### Scenario 1: Patient Skips Document
1. Patient says "I don't have it"
2. LLM detects skip → routes to `patient_intake`
3. Patient provides info → `completeness_check`
4. If incomplete → sets `current_node = "patient_intake"` → END
5. **Next message**: Routes back to `patient_intake` (not `patient_doc_request`) ✅

### Scenario 2: Patient Uploads Document
1. Patient uploads image
2. Routes to `document_extraction`
3. Extracts data → `completeness_check`
4. If incomplete → sets `current_node = "patient_intake"` → END
5. **Next message**: Routes back to `patient_intake` ✅

### Scenario 3: Patient Provides All Info
1. Patient provides complete info
2. `completeness_check` → `clinical_triage` → `confidence_scoring` → `persist_case`
3. Case closed ✅

## Status
✅ Fixed routing to preserve workflow state
✅ Fixed continuation of existing cases
✅ Fixed loop back to `patient_intake` after incomplete data
