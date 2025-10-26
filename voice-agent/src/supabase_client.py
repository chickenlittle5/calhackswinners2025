import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from supabase import create_client, Client

logger = logging.getLogger("supabase_client")


class SupabasePatientDB:
    """Handle all Supabase database operations for patient data."""

    def __init__(self, url: str = None, service_key: str = None):
        """
        Initialize Supabase client.

        Args:
            url: Supabase project URL. If None, reads from environment.
            service_key: Supabase service key. If None, reads from environment.
        """
        self.url = url or os.getenv("SUPABASE_URL")
        self.service_key = service_key or os.getenv("SUPABASE_SERVICE_KEY")

        if not self.url:
            raise ValueError("SUPABASE_URL not found in environment variables")
        if not self.service_key:
            raise ValueError("SUPABASE_SERVICE_KEY not found in environment variables")

        # Initialize Supabase client
        self.client: Client = create_client(self.url, self.service_key)
        self.table_name = "patients"

        logger.info("Supabase client initialized successfully")

    def insert_patient(self, patient_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Insert a new patient record into the database.

        Args:
            patient_data: Dictionary containing patient information

        Returns:
            Inserted record with generated ID, or None if insert fails
        """
        try:
            # Prepare data for insertion
            insert_data = self._prepare_patient_data(patient_data)

            # Insert into Supabase
            result = self.client.table(self.table_name).insert(insert_data).execute()

            if result.data:
                patient_id = result.data[0].get("patient_id")
                logger.info(f"Successfully inserted patient with ID: {patient_id}")
                return result.data[0]
            else:
                logger.error(f"Insert returned no data: {result}")
                return None

        except Exception as e:
            logger.error(f"Error inserting patient: {e}", exc_info=True)
            return None

    def update_patient(self, patient_id: str, patient_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing patient record.

        Args:
            patient_id: UUID of the patient to update
            patient_data: Dictionary containing updated patient information

        Returns:
            Updated record, or None if update fails
        """
        try:
            # Prepare data for update
            update_data = self._prepare_patient_data(patient_data)
            update_data["updated_at"] = datetime.now().isoformat()

            # Update in Supabase
            result = self.client.table(self.table_name).update(update_data).eq("patient_id", patient_id).execute()

            if result.data:
                logger.info(f"Successfully updated patient with ID: {patient_id}")
                return result.data[0]
            else:
                logger.error(f"Update returned no data for ID: {patient_id}")
                return None

        except Exception as e:
            logger.error(f"Error updating patient {patient_id}: {e}", exc_info=True)
            return None

    def get_patient_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find a patient by email address.

        Args:
            email: Patient's email address

        Returns:
            Patient record if found, None otherwise
        """
        try:
            result = self.client.table(self.table_name).select("*").eq("contact_email", email).execute()

            if result.data and len(result.data) > 0:
                logger.info(f"Found patient with email: {email}")
                return result.data[0]
            else:
                logger.info(f"No patient found with email: {email}")
                return None

        except Exception as e:
            logger.error(f"Error querying patient by email {email}: {e}", exc_info=True)
            return None

    def get_patient_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Find a patient by phone number.

        Args:
            phone_number: Patient's phone number

        Returns:
            Patient record if found, None otherwise
        """
        try:
            result = self.client.table(self.table_name).select("*").eq("phone_number", phone_number).execute()

            if result.data and len(result.data) > 0:
                logger.info(f"Found patient with phone: {phone_number}")
                return result.data[0]
            else:
                logger.info(f"No patient found with phone: {phone_number}")
                return None

        except Exception as e:
            logger.error(f"Error querying patient by phone {phone_number}: {e}", exc_info=True)
            return None

    def get_patient_by_id(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a patient record by ID.

        Args:
            patient_id: UUID of the patient

        Returns:
            Patient record if found, None otherwise
        """
        try:
            result = self.client.table(self.table_name).select("*").eq("patient_id", patient_id).execute()

            if result.data and len(result.data) > 0:
                logger.info(f"Found patient with ID: {patient_id}")
                return result.data[0]
            else:
                logger.info(f"No patient found with ID: {patient_id}")
                return None

        except Exception as e:
            logger.error(f"Error querying patient by ID {patient_id}: {e}", exc_info=True)
            return None

    def upsert_patient(self, patient_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Insert patient or update if phone number already exists.

        Args:
            patient_data: Dictionary containing patient information

        Returns:
            Inserted or updated patient record, or None if operation fails
        """
        phone_number = patient_data.get("phone_number")

        if not phone_number:
            logger.warning("No phone number provided, cannot check for existing patient. Inserting new record.")
            return self.insert_patient(patient_data)

        # Check if patient exists by phone number
        existing_patient = self.get_patient_by_phone(phone_number)

        if existing_patient:
            # Update existing record
            patient_id = existing_patient.get("patient_id")
            logger.info(f"Patient with phone {phone_number} already exists. Updating record {patient_id}.")
            return self.update_patient(patient_id, patient_data)
        else:
            # Insert new record
            logger.info(f"No existing patient with phone {phone_number}. Inserting new record.")
            return self.insert_patient(patient_data)

    def get_all_patients(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all patient records (with limit).

        Args:
            limit: Maximum number of records to return

        Returns:
            List of patient records
        """
        try:
            result = self.client.table(self.table_name).select("*").limit(limit).execute()

            if result.data:
                logger.info(f"Retrieved {len(result.data)} patient records")
                return result.data
            else:
                logger.info("No patient records found")
                return []

        except Exception as e:
            logger.error(f"Error retrieving all patients: {e}", exc_info=True)
            return []

    def delete_patient(self, patient_id: str) -> bool:
        """
        Delete a patient record.

        Args:
            patient_id: UUID of the patient to delete

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            result = self.client.table(self.table_name).delete().eq("patient_id", patient_id).execute()

            if result.data:
                logger.info(f"Successfully deleted patient with ID: {patient_id}")
                return True
            else:
                logger.warning(f"Delete returned no data for ID: {patient_id}")
                return False

        except Exception as e:
            logger.error(f"Error deleting patient {patient_id}: {e}", exc_info=True)
            return False

    def update_eligible_trials(self, patient_id: str, nct_ids: List[str]) -> Optional[Dict[str, Any]]:
        """
        Update the current_eligible_trials field for a patient.

        Args:
            patient_id: UUID of the patient to update
            nct_ids: List of NCT IDs (clinical trial identifiers)

        Returns:
            Updated patient record, or None if update fails
        """
        try:
            update_data = {
                "current_eligible_trials": nct_ids,
                "updated_at": datetime.now().isoformat()
            }

            result = self.client.table(self.table_name).update(update_data).eq("patient_id", patient_id).execute()

            if result.data:
                logger.info(f"Updated eligible trials for patient {patient_id}: {len(nct_ids)} trials")
                return result.data[0]
            else:
                logger.error(f"Failed to update eligible trials for patient {patient_id}")
                return None

        except Exception as e:
            logger.error(f"Error updating eligible trials for patient {patient_id}: {e}", exc_info=True)
            return None

    def update_future_trials(
        self,
        patient_id: str,
        predicted_conditions: List[str],
        nct_ids: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Update the future trials data for a patient (predicted conditions and matching trials).

        Args:
            patient_id: UUID of the patient to update
            predicted_conditions: List of predicted future conditions
            nct_ids: List of NCT IDs for future trials

        Returns:
            Updated patient record, or None if update fails
        """
        try:
            update_data = {
                "future_eligible_trials": nct_ids,
                "updated_at": datetime.now().isoformat()
            }

            result = self.client.table(self.table_name).update(update_data).eq("patient_id", patient_id).execute()

            if result.data:
                logger.info(f"Updated future trials for patient {patient_id}: {len(predicted_conditions)} conditions, {len(nct_ids)} trials")
                return result.data[0]
            else:
                logger.error(f"Failed to update future trials for patient {patient_id}")
                return None

        except Exception as e:
            logger.error(f"Error updating future trials for patient {patient_id}: {e}", exc_info=True)
            return None

    def _prepare_patient_data(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare patient data for database insertion/update.

        Args:
            patient_data: Raw patient data from parser

        Returns:
            Cleaned data ready for database (only fields that exist in schema)
        """
        # Map parser fields to database columns (matching exact Supabase schema)
        # Excluding patient_id (auto-generated primary key)
        db_data = {
            "contact_email": patient_data.get("contact_email"),
            "phone_number": patient_data.get("phone_number"),
            "first_name": patient_data.get("first_name"),
            "last_name": patient_data.get("last_name"),
            "date_of_birth": patient_data.get("date_of_birth"),
            "age": patient_data.get("age"),
            "gender": patient_data.get("gender"),
            "location": patient_data.get("location"),
            "condition_summary": patient_data.get("condition_summary"),
            "diagnosed_conditions": patient_data.get("diagnosed_conditions", []),
            "current_medications": patient_data.get("current_medications", []),
        }

        # Remove None values (let database handle defaults)
        db_data = {k: v for k, v in db_data.items() if v is not None}

        return db_data


# Helper function for easy usage
def save_patient_to_db(patient_data: Dict[str, Any], url: str = None, service_key: str = None) -> Optional[Dict[str, Any]]:
    """
    Convenience function to save patient data to Supabase.

    Args:
        patient_data: Dictionary containing patient information
        url: Supabase URL (optional, reads from env if not provided)
        service_key: Supabase service key (optional, reads from env if not provided)

    Returns:
        Saved patient record or None if save fails
    """
    db = SupabasePatientDB(url=url, service_key=service_key)
    return db.upsert_patient(patient_data)
