"""Main FastAPI application for clinical trial matching."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from .clinicaltrials_client import ClinicalTrialsClient, format_trial_for_db
from .matching_engine import MatchingEngine
from .database import Database
from .config import settings


app = FastAPI(
    title="TrialSync Matching API",
    description="API for matching patients with clinical trials",
    version="1.0.0"
)

# CORS middleware to allow requests from Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
ct_client = ClinicalTrialsClient()
db = Database()
matcher = MatchingEngine()


# Request/Response models
class MatchRequest(BaseModel):
    """Request model for matching operations."""
    patient_id: Optional[str] = None
    trial_id: Optional[str] = None
    min_score: int = 50


class SyncTrialsRequest(BaseModel):
    """Request model for syncing trials from ClinicalTrials.gov."""
    condition: Optional[str] = None
    phase: Optional[List[str]] = None
    max_results: int = 100


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "TrialSync Matching API",
        "version": "1.0.0",
        "endpoints": {
            "match_patient": "/match/patient/{patient_id}",
            "match_trial": "/match/trial/{trial_id}",
            "match_all": "/match/all",
            "sync_trials": "/trials/sync",
            "search_trials": "/trials/search"
        }
    }


@app.post("/match/patient/{patient_id}")
async def match_patient(patient_id: str, min_score: int = 50):
    """
    Match a specific patient with all available trials.
    
    Updates the patient's current_eligible_trials and future_eligible_trials in the database.
    """
    # Get patient data
    patient = await db.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get all trials
    trials = await db.get_all_trials()
    if not trials:
        raise HTTPException(status_code=404, detail="No trials found in database")
    
    # Perform matching
    match_results = matcher.match_patient_to_trials(patient, trials, min_score)
    
    # Update database
    success = await db.update_patient_eligibility(
        patient_id,
        match_results["current_eligible_trials"],
        match_results["future_eligible_trials"]
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update patient eligibility")
    
    return {
        "patient_id": patient_id,
        "patient_name": f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip(),
        "current_eligible_count": len(match_results["current_eligible_trials"]),
        "future_eligible_count": len(match_results["future_eligible_trials"]),
        "current_eligible_trials": match_results["current_eligible_trials"],
        "future_eligible_trials": match_results["future_eligible_trials"]
    }


@app.post("/match/trial/{trial_id}")
async def match_trial(trial_id: str, min_score: int = 50):
    """
    Match a specific trial with all available patients.
    
    Updates the trial's eligible_patients and future_eligible_patients in the database.
    """
    # Get trial data
    trial = await db.get_trial(trial_id)
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    # Get all patients
    patients = await db.get_all_patients()
    if not patients:
        raise HTTPException(status_code=404, detail="No patients found in database")
    
    # Perform matching
    match_results = matcher.match_trial_to_patients(trial, patients, min_score)
    
    # Update database
    success = await db.update_trial_eligibility(
        trial_id,
        match_results["eligible_patients"],
        match_results["future_eligible_patients"]
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update trial eligibility")
    
    return {
        "trial_id": trial_id,
        "trial_title": trial.get("title"),
        "eligible_count": len(match_results["eligible_patients"]),
        "future_eligible_count": len(match_results["future_eligible_patients"]),
        "eligible_patients": match_results["eligible_patients"],
        "future_eligible_patients": match_results["future_eligible_patients"]
    }


@app.post("/match/all")
async def match_all(min_score: int = 50):
    """
    Match all patients with all trials.
    
    This can be computationally expensive with large datasets.
    """
    # Get all patients and trials
    patients = await db.get_all_patients()
    trials = await db.get_all_trials()
    
    if not patients:
        raise HTTPException(status_code=404, detail="No patients found in database")
    if not trials:
        raise HTTPException(status_code=404, detail="No trials found in database")
    
    results = {
        "patients_processed": 0,
        "trials_processed": 0,
        "total_matches": 0
    }
    
    # Match each patient
    for patient in patients:
        match_results = matcher.match_patient_to_trials(patient, trials, min_score)
        
        await db.update_patient_eligibility(
            patient["patient_id"],
            match_results["current_eligible_trials"],
            match_results["future_eligible_trials"]
        )
        
        results["patients_processed"] += 1
        results["total_matches"] += len(match_results["current_eligible_trials"])
    
    # Match each trial
    for trial in trials:
        match_results = matcher.match_trial_to_patients(trial, patients, min_score)
        
        await db.update_trial_eligibility(
            trial["trial_id"],
            match_results["eligible_patients"],
            match_results["future_eligible_patients"]
        )
        
        results["trials_processed"] += 1
    
    return results


@app.post("/trials/sync")
async def sync_trials(request: SyncTrialsRequest):
    """
    Sync trials from ClinicalTrials.gov and add them to the database.
    
    Args:
        condition: Optional condition to filter by
        phase: Optional list of phases to filter by
        max_results: Maximum number of trials to sync
    """
    # Search for trials
    search_results = await ct_client.search_trials(
        condition=request.condition,
        phase=request.phase,
        status=["RECRUITING", "NOT_YET_RECRUITING"],
        page_size=min(request.max_results, 100)
    )
    
    if not search_results.get("studies"):
        return {
            "message": "No trials found matching criteria",
            "synced_count": 0
        }
    
    synced_count = 0
    errors = []
    
    for study in search_results["studies"]:
        try:
            # Format trial data for database
            trial_data = format_trial_for_db(study)
            
            # Remove nct_id if present (not in our schema)
            nct_id = trial_data.pop("nct_id", None)
            
            # Add NCT ID to title if available
            if nct_id:
                trial_data["title"] = f"{trial_data['title']} ({nct_id})"
            
            # Upsert trial
            success = await db.upsert_trial(trial_data)
            
            if success:
                synced_count += 1
        except Exception as e:
            errors.append(str(e))
    
    return {
        "message": f"Synced {synced_count} trials from ClinicalTrials.gov",
        "synced_count": synced_count,
        "total_found": len(search_results["studies"]),
        "errors": errors if errors else None
    }


@app.get("/trials/search")
async def search_trials(
    condition: Optional[str] = None,
    phase: Optional[str] = None,
    page_size: int = 20
):
    """
    Search ClinicalTrials.gov without syncing to database.
    
    Returns trial information for preview.
    """
    phase_list = [phase] if phase else None
    
    search_results = await ct_client.search_trials(
        condition=condition,
        phase=phase_list,
        status=["RECRUITING"],
        page_size=page_size
    )
    
    studies = search_results.get("studies", [])
    formatted_studies = []
    
    for study in studies:
        try:
            formatted = format_trial_for_db(study)
            formatted_studies.append(formatted)
        except Exception as e:
            print(f"Error formatting study: {e}")
    
    return {
        "total_count": search_results.get("totalCount", 0),
        "results": formatted_studies
    }


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await ct_client.close()

