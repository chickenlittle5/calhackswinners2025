# Future Trials Matching Feature

## Overview
The Future Trials Matcher uses Claude AI to predict potential disease progressions and complications based on a patient's current health status, then searches ClinicalTrials.gov for relevant trials for those predicted future conditions.

## How It Works

### Step 1: AI-Powered Prediction
Claude analyzes:
- Current diagnosed conditions
- Current medications
- Condition summary
- Age and gender

Then predicts 3-7 potential future conditions considering:
- Natural disease progression patterns
- Common comorbidities and complications
- Medication side effects
- Age/gender-specific risk factors

### Step 2: Trial Matching
Searches ClinicalTrials.gov using the predicted conditions with OR logic (same as current trials matcher).

### Step 3: Database Storage
Stores two new fields in Supabase:
- `predicted_future_conditions` (array of strings) - The conditions Claude predicted
- `future_eligible_trials` (array of strings) - NCT IDs of matching future trials

## Example Workflow

**Input Patient Data:**
```json
{
  "age": 55,
  "gender": "Male",
  "diagnosed_conditions": ["Type 2 Diabetes"],
  "current_medications": ["Metformin", "Lisinopril"],
  "condition_summary": "Recently diagnosed with Type 2 Diabetes, well controlled on Metformin"
}
```

**Claude Prediction:**
```json
[
  "Diabetic Retinopathy",
  "Diabetic Nephropathy",
  "Cardiovascular Disease",
  "Peripheral Neuropathy",
  "Chronic Kidney Disease"
]
```

**API Query:**
```
"Diabetic Retinopathy OR Diabetic Nephropathy OR Cardiovascular Disease OR Peripheral Neuropathy OR Chronic Kidney Disease"
```

**Result:**
- 80+ NCT IDs for future trials stored in `future_eligible_trials`
- Predicted conditions stored in `predicted_future_conditions`

## Integration

The future trials matching is automatically integrated into the voice agent workflow:

1. Voice call ends → Transcript saved
2. Claude parses transcript → Extracts patient data
3. Data saved to Supabase
4. **Current trials matched** → `current_eligible_trials` updated
5. **Future trials matched** → `predicted_future_conditions` and `future_eligible_trials` updated

## Files Created/Modified

### New Files:
- `voice-agent/src/future_trials_matcher.py` - Main implementation

### Modified Files:
- `voice-agent/src/supabase_client.py` - Added `update_future_trials()` method
- `voice-agent/src/transcribe.py` - Integrated Step 4 (future trial matching)

## Database Schema Requirements

Add these fields to your Supabase `patients` table:
- `predicted_future_conditions` - Type: `text[]` or `jsonb`
- `future_eligible_trials` - Type: `text[]` or `jsonb`

## Usage

### Standalone Usage:
```python
from future_trials_matcher import match_patient_to_future_trials

patient_data = {
    "age": 55,
    "gender": "Male",
    "diagnosed_conditions": ["Type 2 Diabetes"],
    "current_medications": ["Metformin"],
    "condition_summary": "Well controlled diabetes"
}

result = match_patient_to_future_trials(patient_data)
# Returns: {
#   "predicted_conditions": ["Diabetic Retinopathy", ...],
#   "trial_nct_ids": ["NCT12345678", ...],
#   "trial_count": 85
# }
```

### Automatic Integration:
No additional code needed - it runs automatically after every voice call in the existing workflow.

## Value Proposition

**For Patients:**
- Proactive trial discovery
- Early intervention opportunities
- Awareness of potential health risks

**For Hackathon Demo:**
- Showcases AI-powered predictive healthcare
- Demonstrates integration of multiple APIs (Anthropic + ClinicalTrials.gov)
- Addresses Regeneron's focus on clinical trial innovation

**For Regeneron Judges:**
- Innovative use of AI for patient recruitment
- Addresses trial enrollment challenges
- Shows forward-thinking approach to patient care
