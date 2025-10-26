"""Database operations for Supabase."""
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from .config import settings


class Database:
    """Database client for Supabase operations."""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    async def get_all_patients(self) -> List[Dict[str, Any]]:
        """Fetch all patients from the database."""
        response = self.client.table("patients").select("*").execute()
        return response.data if response.data else []
    
    async def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific patient by ID."""
        response = self.client.table("patients").select("*").eq("patient_id", patient_id).execute()
        return response.data[0] if response.data else None
    
    async def get_all_trials(self) -> List[Dict[str, Any]]:
        """Fetch all trials from the database."""
        response = self.client.table("trials").select("*").execute()
        return response.data if response.data else []
    
    async def get_trial(self, trial_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific trial by ID."""
        response = self.client.table("trials").select("*").eq("trial_id", trial_id).execute()
        return response.data[0] if response.data else None
    
    async def update_patient_eligibility(
        self,
        patient_id: str,
        current_eligible_trials: List[Dict[str, Any]],
        future_eligible_trials: List[Dict[str, Any]]
    ) -> bool:
        """
        Update patient's eligible trials in the database.
        
        Args:
            patient_id: Patient UUID
            current_eligible_trials: List of currently eligible trials
            future_eligible_trials: List of potentially eligible trials
        
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.client.table("patients").update({
                "current_eligible_trials": current_eligible_trials,
                "future_eligible_trials": future_eligible_trials,
                "updated_at": "NOW()"
            }).eq("patient_id", patient_id).execute()
            
            return len(response.data) > 0
        except Exception as e:
            print(f"Error updating patient eligibility: {e}")
            return False
    
    async def update_trial_eligibility(
        self,
        trial_id: str,
        eligible_patients: List[Dict[str, Any]],
        future_eligible_patients: List[Dict[str, Any]]
    ) -> bool:
        """
        Update trial's eligible patients in the database.
        
        Args:
            trial_id: Trial UUID
            eligible_patients: List of eligible patients
            future_eligible_patients: List of potentially eligible patients
        
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.client.table("trials").update({
                "eligible_patients": eligible_patients,
                "future_eligible_patients": future_eligible_patients,
                "updated_at": "NOW()"
            }).eq("trial_id", trial_id).execute()
            
            return len(response.data) > 0
        except Exception as e:
            print(f"Error updating trial eligibility: {e}")
            return False
    
    async def insert_trial_from_clinicaltrials(
        self,
        trial_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Insert a trial from ClinicalTrials.gov into the database.
        
        Args:
            trial_data: Formatted trial data
        
        Returns:
            Trial ID if successful, None otherwise
        """
        try:
            response = self.client.table("trials").insert(trial_data).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0].get("trial_id")
            return None
        except Exception as e:
            print(f"Error inserting trial: {e}")
            return None
    
    async def upsert_trial(self, trial_data: Dict[str, Any]) -> bool:
        """
        Upsert a trial (update if exists, insert if not).
        
        Args:
            trial_data: Trial data to upsert
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to find existing trial by title (since NCT ID might not be stored)
            existing = self.client.table("trials").select("trial_id").eq("title", trial_data.get("title")).execute()
            
            if existing.data and len(existing.data) > 0:
                # Update existing
                trial_id = existing.data[0]["trial_id"]
                response = self.client.table("trials").update(trial_data).eq("trial_id", trial_id).execute()
            else:
                # Insert new
                response = self.client.table("trials").insert(trial_data).execute()
            
            return len(response.data) > 0
        except Exception as e:
            print(f"Error upserting trial: {e}")
            return False

