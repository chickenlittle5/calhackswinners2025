import logging
import os
import requests
from typing import List, Dict, Any, Optional, Union
from anthropic import Anthropic

logger = logging.getLogger("future_trials_matcher")


class FutureTrialsMatcher:
    """
    Use Claude AI to predict potential disease progressions and find relevant clinical trials
    for future conditions that patients may develop.
    """

    def __init__(self, anthropic_api_key: str = None):
        """
        Initialize the future trials matcher with Claude API.

        Args:
            anthropic_api_key: Anthropic API key. If None, reads from environment.
        """
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"
        self.trials_api_url = "https://clinicaltrials.gov/api/v2/studies"

        logger.info("Future trials matcher initialized")

    def predict_future_conditions(self, patient_data: Dict[str, Any]) -> List[str]:
        """
        Use Claude to predict potential future disease progressions based on patient's
        current diagnoses, medications, and condition summary.

        Args:
            patient_data: Dictionary containing patient information with keys:
                - diagnosed_conditions: List[str]
                - current_medications: List[str]
                - condition_summary: str
                - age: int
                - gender: str

        Returns:
            List of predicted future conditions/progressions
        """
        try:
            # Extract patient information
            current_conditions = patient_data.get("diagnosed_conditions", [])
            medications = patient_data.get("current_medications", [])
            condition_summary = patient_data.get("condition_summary", "")
            age = patient_data.get("age")
            gender = patient_data.get("gender")

            # Build the prompt for Claude
            prompt = f"""You are a medical expert analyzing patient data to predict potential disease progressions and complications.

PATIENT INFORMATION:
- Age: {age}
- Gender: {gender}
- Current Diagnosed Conditions: {', '.join(current_conditions) if current_conditions else 'None listed'}
- Current Medications: {', '.join(medications) if medications else 'None listed'}
- Condition Summary: {condition_summary if condition_summary else 'None provided'}

TASK:
Based on this patient's current health status, predict 3-7 potential future disease progressions, complications, or related conditions they may develop. Consider:
1. Natural disease progression patterns
2. Common comorbidities and complications
3. Medication side effects or related conditions
4. Age and gender-specific risk factors

REQUIREMENTS:
- Return ONLY medical condition names that could be used to search clinical trials
- Be specific (e.g., "Type 2 Diabetes Nephropathy" not just "Kidney Disease")
- Focus on conditions with active clinical trial research
- DO NOT include the current diagnosed conditions
- Return between 3-7 conditions

CRITICAL: Return ONLY a valid JSON array of strings. No markdown, no code blocks, no explanations. Just the raw JSON array.

Example: ["Diabetic Retinopathy", "Cardiovascular Disease", "Chronic Kidney Disease"]

Your response must start with [ and end with ]."""

            logger.info("Requesting future condition predictions from Claude...")

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract the response text
            response_text = response.content[0].text.strip()
            logger.info(f"Claude raw response: {response_text}")

            if not response_text:
                logger.error("Claude returned empty response")
                return []

            # Parse the JSON array - handle markdown code blocks if present
            import json
            import re

            # Remove markdown code blocks if present
            # Pattern: ```json\n[...]\n``` or ```\n[...]\n```
            json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # Try to find JSON array directly
                json_match = re.search(r'(\[.*?\])', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(1)
                else:
                    json_text = response_text

            try:
                predicted_conditions = json.loads(json_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from Claude response. Error: {e}")
                logger.error(f"Attempted to parse: {json_text[:200]}")
                return []

            if not isinstance(predicted_conditions, list):
                logger.error(f"Expected list, got {type(predicted_conditions)}")
                return []

            logger.info(f"✅ Predicted {len(predicted_conditions)} future conditions: {predicted_conditions}")
            return predicted_conditions

        except Exception as e:
            logger.error(f"Error predicting future conditions: {e}", exc_info=True)
            return []

    def search_trials_for_conditions(
        self,
        conditions: List[str],
        age: Optional[Union[int, float]] = None,
        gender: Optional[str] = None
    ) -> List[str]:
        """
        Search ClinicalTrials.gov for trials matching the predicted future conditions,
        with optional age and gender filters.

        Args:
            conditions: List of predicted future conditions
            age: Patient age in years (numeric). If provided, filters to trials whose
                eligibility includes this age (MinimumAge ≤ age ≤ MaximumAge).
            gender: Patient gender. Accepted values (case/abbrev tolerant):
                    'female'/'f', 'male'/'m'. Everything else (e.g., 'all', None) applies no sex filter.

        Returns:
            List of NCT IDs for matching trials
        """
        if not conditions:
            logger.warning("No conditions provided for trial search")
            return []

        # Combine conditions with OR logic
        combined_query = " OR ".join(conditions)
        logger.info(f"Searching future trials for: {combined_query} "
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
            logger.info(f"API Request: {self.trials_api_url} with params={params}")
            response = requests.get(self.trials_api_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Extract NCT IDs
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
            logger.info(f"Found {len(unique_ids)} future trials")
            return unique_ids

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}", exc_info=True)
            return []
        except (ValueError, KeyError) as e:
            logger.error(f"Failed to parse API response: {e}", exc_info=True)
            return []

    def find_future_trials(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete workflow: predict future conditions and find matching trials.

        Args:
            patient_data: Dictionary containing patient information

        Returns:
            Dictionary with predicted conditions and matching NCT IDs:
            {
                "predicted_conditions": List[str],
                "trial_nct_ids": List[str],
                "trial_count": int
            }
        """
        logger.info("Starting future trials matching workflow...")

        # Extract age and gender (optional for filtering)
        age = patient_data.get("age")
        gender = patient_data.get("gender")

        # Step 1: Predict future conditions using Claude
        predicted_conditions = self.predict_future_conditions(patient_data)

        if not predicted_conditions:
            logger.warning("No future conditions predicted")
            return {
                "predicted_conditions": [],
                "trial_nct_ids": [],
                "trial_count": 0
            }

        # Step 2: Search for trials matching predicted conditions
        trial_nct_ids = self.search_trials_for_conditions(
            conditions=predicted_conditions,
            age=age,
            gender=gender
        )

        result = {
            "predicted_conditions": predicted_conditions,
            "trial_nct_ids": trial_nct_ids,
            "trial_count": len(trial_nct_ids)
        }

        logger.info(f"✅ Future trials workflow complete: {len(predicted_conditions)} conditions, {len(trial_nct_ids)} trials")
        return result


# Helper function for easy usage
def match_patient_to_future_trials(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to predict future conditions and find matching trials.

    Args:
        patient_data: Dictionary with patient information

    Returns:
        Dictionary with predicted conditions and trial NCT IDs
    """
    matcher = FutureTrialsMatcher()
    return matcher.find_future_trials(patient_data)
