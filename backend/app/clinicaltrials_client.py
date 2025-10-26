"""Client for interacting with ClinicalTrials.gov API v2."""
import httpx
from typing import List, Dict, Any, Optional
from .config import settings


class ClinicalTrialsClient:
    """Client for fetching data from ClinicalTrials.gov API."""
    
    def __init__(self):
        self.base_url = settings.clinicaltrials_api_base
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_trials(
        self,
        condition: Optional[str] = None,
        phase: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        page_size: int = 100,
        page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for clinical trials using the ClinicalTrials.gov API v2.
        
        Args:
            condition: Disease or condition name
            phase: List of trial phases (e.g., ["PHASE1", "PHASE2", "PHASE3", "PHASE4"])
            status: List of recruitment statuses (e.g., ["RECRUITING", "ACTIVE_NOT_RECRUITING"])
            page_size: Number of results per page (max 1000)
            page_token: Token for pagination
        
        Returns:
            Dictionary containing trial data and pagination info
        """
        params = {
            "format": "json",
            "pageSize": page_size
        }
        
        # Build query
        query_parts = []
        
        if condition:
            query_parts.append(f"AREA[ConditionSearch]{condition}")
        
        if status:
            status_query = " OR ".join([f"AREA[OverallStatus]{s}" for s in status])
            query_parts.append(f"({status_query})")
        
        if phase:
            phase_query = " OR ".join([f"AREA[Phase]{p}" for p in phase])
            query_parts.append(f"({phase_query})")
        
        if query_parts:
            params["query.cond"] = " AND ".join(query_parts)
        
        if page_token:
            params["pageToken"] = page_token
        
        # Fields to retrieve
        params["fields"] = (
            "NCTId,BriefTitle,Condition,Phase,OverallStatus,"
            "StartDate,CompletionDate,EnrollmentCount,LocationCity,"
            "LocationState,LocationCountry,MinimumAge,MaximumAge,"
            "Gender,EligibilityCriteria,LeadSponsorName"
        )
        
        try:
            response = await self.client.get(
                f"{self.base_url}/studies",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Error fetching trials: {e}")
            return {"studies": [], "totalCount": 0}
    
    async def get_trial_details(self, nct_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific trial.
        
        Args:
            nct_id: NCT ID of the trial
        
        Returns:
            Dictionary containing trial details or None if not found
        """
        params = {
            "format": "json",
            "fields": (
                "NCTId,BriefTitle,DetailedDescription,Condition,Phase,"
                "OverallStatus,StartDate,CompletionDate,EnrollmentCount,"
                "LocationCity,LocationState,LocationCountry,MinimumAge,"
                "MaximumAge,Gender,EligibilityCriteria,LeadSponsorName,"
                "HealthyVolunteers,StdAge"
            )
        }
        
        try:
            response = await self.client.get(
                f"{self.base_url}/studies/{nct_id}",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            if "studies" in data and len(data["studies"]) > 0:
                return data["studies"][0]
            return None
        except httpx.HTTPError as e:
            print(f"Error fetching trial {nct_id}: {e}")
            return None
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


def parse_age(age_str: Optional[str]) -> Optional[int]:
    """
    Parse age string from ClinicalTrials.gov format.
    
    Examples: "18 Years", "65 Years", "6 Months", "N/A"
    
    Returns:
        Age in years or None
    """
    if not age_str or age_str == "N/A":
        return None
    
    age_str = age_str.strip().upper()
    
    try:
        if "YEAR" in age_str:
            return int(age_str.split()[0])
        elif "MONTH" in age_str:
            months = int(age_str.split()[0])
            return months // 12
        elif "DAY" in age_str or "WEEK" in age_str:
            return 0
    except (ValueError, IndexError):
        return None
    
    return None


def format_trial_for_db(trial_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format trial data from ClinicalTrials.gov API for database storage.
    
    Args:
        trial_data: Raw trial data from API
    
    Returns:
        Formatted dictionary ready for database insertion
    """
    protocol = trial_data.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    eligibility = protocol.get("eligibilityModule", {})
    contacts = protocol.get("contactsLocationsModule", {})
    sponsor = protocol.get("sponsorCollaboratorsModule", {})
    
    # Extract locations
    locations = contacts.get("locations", [])
    location_str = None
    if locations:
        first_loc = locations[0]
        city = first_loc.get("city", "")
        state = first_loc.get("state", "")
        country = first_loc.get("country", "")
        location_parts = [p for p in [city, state, country] if p]
        location_str = ", ".join(location_parts)
    
    # Extract phase
    phases = design.get("phases", [])
    phase = phases[0] if phases else None
    if phase:
        phase = phase.replace("PHASE", "").strip()
    
    # Extract dates
    start_date = status.get("startDateStruct", {}).get("date")
    completion_date = status.get("completionDateStruct", {}).get("date")
    
    return {
        "nct_id": identification.get("nctId"),
        "title": identification.get("briefTitle"),
        "phase": phase,
        "condition": ", ".join(protocol.get("conditionsModule", {}).get("conditions", [])),
        "status": status.get("overallStatus"),
        "location": location_str,
        "start_date": start_date,
        "end_date": completion_date,
        "sponsor": sponsor.get("leadSponsor", {}).get("name"),
        "min_age": parse_age(eligibility.get("minimumAge")),
        "max_age": parse_age(eligibility.get("maximumAge")),
        "gender": eligibility.get("sex", "ALL"),
        "eligibility_criteria": eligibility.get("eligibilityCriteria"),
    }

