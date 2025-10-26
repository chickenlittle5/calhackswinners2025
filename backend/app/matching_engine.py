"""Matching engine for determining patient eligibility for clinical trials."""
from typing import Dict, Any, List, Optional
from datetime import datetime
import re


class MatchingEngine:
    """Engine for matching patients with clinical trials based on eligibility criteria."""
    
    @staticmethod
    def calculate_match_score(patient: Dict[str, Any], trial: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate how well a patient matches a trial's eligibility criteria.
        
        Args:
            patient: Patient data including demographics and medical history
            trial: Trial data including eligibility criteria
        
        Returns:
            Dictionary with match score and eligibility status
        """
        score = 100
        reasons = []
        is_eligible = True
        
        # Age check
        patient_age = patient.get("age")
        min_age = trial.get("min_age")
        max_age = trial.get("max_age")
        
        if patient_age:
            if min_age and patient_age < min_age:
                is_eligible = False
                reasons.append(f"Age {patient_age} is below minimum age {min_age}")
                score -= 30
            elif max_age and patient_age > max_age:
                is_eligible = False
                reasons.append(f"Age {patient_age} exceeds maximum age {max_age}")
                score -= 30
        
        # Gender check
        trial_gender = trial.get("gender", "ALL")
        patient_gender = patient.get("gender", "").upper()
        
        if trial_gender and trial_gender != "ALL":
            if patient_gender and patient_gender != trial_gender:
                is_eligible = False
                reasons.append(f"Gender mismatch: trial requires {trial_gender}")
                score -= 40
        
        # Condition matching (basic keyword matching)
        patient_conditions = []
        
        # Extract from condition_summary
        if patient.get("condition_summary"):
            patient_conditions.append(patient["condition_summary"].lower())
        
        # Extract from diagnosed_conditions (JSONB array)
        if patient.get("diagnosed_conditions"):
            if isinstance(patient["diagnosed_conditions"], list):
                patient_conditions.extend([c.lower() for c in patient["diagnosed_conditions"]])
        
        trial_conditions = []
        if trial.get("condition"):
            trial_conditions = [c.strip().lower() for c in trial["condition"].split(",")]
        
        # Check for condition matches
        condition_match = False
        if patient_conditions and trial_conditions:
            for patient_cond in patient_conditions:
                for trial_cond in trial_conditions:
                    # Simple substring matching
                    if trial_cond in patient_cond or patient_cond in trial_cond:
                        condition_match = True
                        break
                    
                    # Check for common condition keywords
                    if MatchingEngine._has_condition_overlap(patient_cond, trial_cond):
                        condition_match = True
                        break
                
                if condition_match:
                    break
        
        if not condition_match and trial_conditions:
            score -= 20
            reasons.append("Condition does not match trial criteria")
        
        # Location check (basic - just checking if location exists)
        patient_location = patient.get("location", "").lower()
        trial_location = trial.get("location", "").lower()
        
        if patient_location and trial_location:
            # Simple check if same state/country
            if not any(loc in trial_location for loc in patient_location.split(",")):
                score -= 10
                reasons.append("Location may not be optimal")
        
        # Trial status check
        trial_status = trial.get("status", "").upper()
        if trial_status not in ["RECRUITING", "NOT_YET_RECRUITING", "AVAILABLE"]:
            is_eligible = False
            reasons.append(f"Trial status is {trial_status}")
            score -= 50
        
        # Ensure score doesn't go below 0
        score = max(0, score)
        
        return {
            "score": score,
            "is_eligible": is_eligible,
            "reasons": reasons,
            "trial_id": trial.get("trial_id") or trial.get("nct_id"),
            "trial_title": trial.get("title"),
            "match_type": "current" if is_eligible else "future"
        }
    
    @staticmethod
    def _has_condition_overlap(cond1: str, cond2: str) -> bool:
        """
        Check if two condition strings have overlapping keywords.
        
        Args:
            cond1: First condition string
            cond2: Second condition string
        
        Returns:
            True if conditions have common keywords
        """
        # Common medical condition keywords
        keywords1 = set(re.findall(r'\b\w{4,}\b', cond1.lower()))
        keywords2 = set(re.findall(r'\b\w{4,}\b', cond2.lower()))
        
        # Remove common stopwords
        stopwords = {
            'disease', 'syndrome', 'disorder', 'condition', 'chronic',
            'acute', 'with', 'without', 'type', 'stage'
        }
        
        keywords1 -= stopwords
        keywords2 -= stopwords
        
        # Check for overlap
        return len(keywords1 & keywords2) > 0
    
    @staticmethod
    def match_patient_to_trials(
        patient: Dict[str, Any],
        trials: List[Dict[str, Any]],
        min_score: int = 50
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Match a patient against multiple trials.
        
        Args:
            patient: Patient data
            trials: List of trial data
            min_score: Minimum score to consider a match
        
        Returns:
            Dictionary with 'current_eligible' and 'future_eligible' lists
        """
        current_eligible = []
        future_eligible = []
        
        for trial in trials:
            match_result = MatchingEngine.calculate_match_score(patient, trial)
            
            if match_result["score"] >= min_score:
                match_info = {
                    "trial_id": match_result["trial_id"],
                    "title": match_result["trial_title"],
                    "score": match_result["score"],
                    "match_date": datetime.now().isoformat()
                }
                
                if match_result["is_eligible"]:
                    current_eligible.append(match_info)
                else:
                    match_info["reasons"] = match_result["reasons"]
                    future_eligible.append(match_info)
        
        # Sort by score (highest first)
        current_eligible.sort(key=lambda x: x["score"], reverse=True)
        future_eligible.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "current_eligible_trials": current_eligible,
            "future_eligible_trials": future_eligible
        }
    
    @staticmethod
    def match_trial_to_patients(
        trial: Dict[str, Any],
        patients: List[Dict[str, Any]],
        min_score: int = 50
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Match a trial against multiple patients.
        
        Args:
            trial: Trial data
            patients: List of patient data
            min_score: Minimum score to consider a match
        
        Returns:
            Dictionary with 'eligible_patients' and 'future_eligible_patients' lists
        """
        eligible_patients = []
        future_eligible_patients = []
        
        for patient in patients:
            match_result = MatchingEngine.calculate_match_score(patient, trial)
            
            if match_result["score"] >= min_score:
                match_info = {
                    "patient_id": patient.get("patient_id"),
                    "name": f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip(),
                    "score": match_result["score"],
                    "match_date": datetime.now().isoformat()
                }
                
                if match_result["is_eligible"]:
                    eligible_patients.append(match_info)
                else:
                    match_info["reasons"] = match_result["reasons"]
                    future_eligible_patients.append(match_info)
        
        # Sort by score (highest first)
        eligible_patients.sort(key=lambda x: x["score"], reverse=True)
        future_eligible_patients.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "eligible_patients": eligible_patients,
            "future_eligible_patients": future_eligible_patients
        }

