import logging
import requests
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger("clinical_trials_matcher")


class ClinicalTrialsMatcher:
    """Match patients to clinical trials using ClinicalTrials.gov API."""

    def __init__(self):
        """Initialize the ClinicalTrials.gov API client."""
        self.base_url = "https://clinicaltrials.gov/api/v2/studies"
        self.rate_limit_delay = 1.2  # seconds between requests (50/min = 1.2s)

        logger.info("ClinicalTrials matcher initialized")

    def find_matching_trials(
    self,
    conditions: List[str],
    age: Optional[Union[int, float]] = None,
    gender: Optional[str] = None
) -> List[str]:
        """
        Find clinical trials matching patient's medical conditions, with optional age and gender filters.

        Args:
            conditions: List of diagnosed medical conditions
            age: Patient age in years (numeric). If provided, filters to trials whose
                eligibility includes this age (MinimumAge ≤ age ≤ MaximumAge).
            gender: Patient gender. Accepted values (case/abbrev tolerant):
                    'female'/'f', 'male'/'m'. Everything else (e.g., 'all', None) applies no sex filter.

        Returns:
            List of NCT IDs for matching trials
        """
        if not conditions:
            logger.warning("No conditions provided for trial matching")
            return []

        combined_query = " OR ".join(conditions)
        logger.info(f"Searching trials for conditions: {combined_query} "
                    f"(age={age!r}, gender={gender!r})")

        # Build advanced filter (Essie / Search Areas)
        advanced_parts: List[str] = []

        # Normalize gender -> AREA[Sex]{Male|Female}
        if isinstance(gender, str):
            g = gender.strip().lower()
            if g in ("female", "f", "woman", "women"):
                advanced_parts.append("AREA[Sex]Female")
            elif g in ("male", "m", "man", "men"):
                advanced_parts.append("AREA[Sex]Male")
            # else: 'all', 'other', 'unknown' -> no sex filter

        # Age filter: MinimumAge ≤ age AND MaximumAge ≥ age
        if age is not None:
            try:
                age_yrs = int(float(age))
                if age_yrs >= 0:
                    advanced_parts.append(f"AREA[MinimumAge]RANGE[0 Years,{age_yrs} Years]")
                    advanced_parts.append(f"AREA[MaximumAge]RANGE[{age_yrs} Years,MAX]")
            except (TypeError, ValueError):
                logger.warning(f"Invalid age provided: {age!r}; skipping age filter")

        params = {
            "query.cond": combined_query,
            "filter.overallStatus": "RECRUITING",
            "pageSize": 100,
            "format": "json",
            "fields": "NCTId",
        }

        if advanced_parts:
            params["filter.advanced"] = " AND ".join(advanced_parts)

        try:
            logger.info(f"API Request: {self.base_url} with params={params}")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            studies = data.get("studies", [])
            nct_ids: List[str] = []

            for study in studies:
                protocol_section = study.get("protocolSection", {})
                identification_module = protocol_section.get("identificationModule", {})
                nct_id = identification_module.get("nctId")
                if nct_id:
                    nct_ids.append(nct_id)

            # Deduplicate just in case
            unique_ids = list(dict.fromkeys(nct_ids))
            logger.info(f"Total unique trials found: {len(unique_ids)}")
            return unique_ids

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}", exc_info=True)
            return []
        except (ValueError, KeyError) as e:
            logger.error(f"Failed to parse API response: {e}", exc_info=True)
            return []


    def _search_by_conditions(self, conditions_query: str) -> List[str]:
        """
        Search ClinicalTrials.gov API for trials by conditions and extract NCT IDs.

        Args:
            conditions_query: Combined conditions query (e.g., "Cancer OR Diabetes")

        Returns:
            List of NCT ID strings
        """
        params = {
            "query.cond": conditions_query,
            "filter.overallStatus": "RECRUITING",  # Only recruiting trials
            "pageSize": 100,
            "format": "json",
            "fields": "NCTId"  # Only request NCT ID field
        }

        try:
            logger.info(f"API Request: {self.base_url} with conditions='{conditions_query}'")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Extract NCT IDs from studies
            studies = data.get("studies", [])
            nct_ids = []

            for study in studies:
                # Navigate the nested structure to get NCT ID
                protocol_section = study.get("protocolSection", {})
                identification_module = protocol_section.get("identificationModule", {})
                nct_id = identification_module.get("nctId")

                if nct_id:
                    nct_ids.append(nct_id)

            logger.info(f"API returned {len(nct_ids)} NCT IDs for '{conditions_query}'")
            return nct_ids

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for conditions '{conditions_query}': {e}")
            return []
        except (ValueError, KeyError) as e:
            logger.error(f"Failed to parse API response: {e}")
            return []


# Helper function for easy usage
def match_patient_to_trials(patient_data: Dict[str, Any]) -> List[str]:
    """
    Convenience function to match a patient to clinical trials.

    Args:
        patient_data: Dictionary with patient information.
                      Expected keys:
                        - diagnosed_conditions: List[str]
                        - age: int/float (years)
                        - gender: str ('male'/'female'/'all'/etc.)

    Returns:
        List of matching NCT IDs
    """
    conditions = patient_data.get("diagnosed_conditions", [])
    if not conditions:
        logger.warning("Patient has no diagnosed conditions, cannot match trials")
        return []

    age = patient_data.get("age")
    gender = patient_data.get("gender")

    matcher = ClinicalTrialsMatcher()
    nct_ids = matcher.find_matching_trials(conditions, age=age, gender=gender)
    return nct_ids
