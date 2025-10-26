import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger("transcribe")

class TranscriptManager:
    """Manages conversation transcripts from LiveKit agent sessions."""

    def __init__(self):
        self.transcript: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}

    def add_message(self, role: str, content: str, timestamp: datetime = None):
        """
        Add a message to the transcript.

        Args:
            role: Either 'user' or 'assistant'
            content: The message content
            timestamp: When the message was sent (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp.isoformat()
        }
        self.transcript.append(message)
        logger.info(f"Added {role} message to transcript")

    def set_metadata(self, room_name: str = None, **kwargs):
        """
        Set metadata about the conversation.

        Args:
            room_name: The LiveKit room name
            **kwargs: Additional metadata fields
        """
        if room_name:
            self.metadata["room_name"] = room_name
        self.metadata["session_start"] = datetime.now().isoformat()
        self.metadata.update(kwargs)

    def get_transcript(self) -> List[Dict[str, Any]]:
        """Get the current transcript as a list of messages."""
        return self.transcript.copy()

    def get_full_data(self) -> Dict[str, Any]:
        """Get the complete transcript data including metadata."""
        return {
            "metadata": self.metadata,
            "transcript": self.transcript,
            "message_count": len(self.transcript),
            "exported_at": datetime.now().isoformat()
        }

    def save_to_file(self, filepath: str = None):
        """
        Save the transcript to a JSON file in the transcripts folder.

        Args:
            filepath: Path to save the file. If None, generates a timestamped filename in transcripts/.
        """
        # Create transcripts directory if it doesn't exist
        transcripts_dir = Path("transcripts")
        transcripts_dir.mkdir(exist_ok=True)

        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            room = self.metadata.get("room_name", "unknown")
            filename = f"transcript_{room}_{timestamp}.json"
            filepath = transcripts_dir / filename
        else:
            # If custom filepath provided, still put it in transcripts folder
            filepath = transcripts_dir / Path(filepath).name

        data = self.get_full_data()

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Transcript saved to {filepath}")
        return str(filepath)

    def load_from_session_history(self, session_history):
        """
        Load transcript from LiveKit session.history object.

        Args:
            session_history: The session.history object from LiveKit
        """
        try:
            # Convert session history to dict if it has that method
            if hasattr(session_history, 'to_dict'):
                history_data = session_history.to_dict()
            else:
                history_data = session_history

            # Clear existing transcript
            self.transcript = []

            # Process history data
            if isinstance(history_data, list):
                for item in history_data:
                    if isinstance(item, dict) and 'role' in item and 'content' in item:
                        self.add_message(
                            role=item['role'],
                            content=item['content'],
                            timestamp=datetime.now()
                        )

            logger.info(f"Loaded {len(self.transcript)} messages from session history")
        except Exception as e:
            logger.error(f"Error loading session history: {e}")

    def clear(self):
        """Clear all transcript data."""
        self.transcript = []
        self.metadata = {}
        logger.info("Transcript cleared")

    def get_text_only(self) -> str:
        """
        Get the transcript as plain text (useful for display or analysis).

        Returns:
            A formatted string with the conversation
        """
        lines = []
        for msg in self.transcript:
            role = msg['role'].upper()
            content = msg['content']
            timestamp = msg.get('timestamp', '')
            lines.append(f"[{timestamp}] {role}: {content}")

        return "\n".join(lines)

    def extract_user_responses(self) -> List[str]:
        """Extract only user messages from the transcript."""
        return [msg['content'] for msg in self.transcript if msg['role'] == 'user']

    def extract_agent_responses(self) -> List[str]:
        """Extract only agent/assistant messages from the transcript."""
        return [msg['content'] for msg in self.transcript if msg['role'] == 'assistant']

    def parse_and_save_to_db(self, transcript_filepath: str) -> Optional[Dict[str, Any]]:
        """
        Parse the transcript using Claude and save extracted data to Supabase.

        Args:
            transcript_filepath: Path to the saved transcript JSON file

        Returns:
            Dictionary with parsing and saving results, or None if failed
        """
        try:
            # Import parser and supabase client (lazy import to avoid circular dependencies)
            from parser import TranscriptParser
            from supabase_client import SupabasePatientDB

            logger.info(f"Starting parse and save for: {transcript_filepath}")

            # Step 1: Parse transcript with Claude
            parser = TranscriptParser()
            patient_data = parser.parse_transcript(transcript_filepath)

            if not patient_data:
                logger.error("Failed to parse transcript")
                return {"success": False, "error": "Parsing failed", "patient_id": None}

            logger.info(f"Successfully parsed transcript. Confidence: {patient_data.get('extraction_confidence', 'unknown')}")

            # Step 2: Save to Supabase
            db = SupabasePatientDB()
            saved_record = db.upsert_patient(patient_data)

            if not saved_record:
                logger.error("Failed to save to Supabase")
                # Save extracted data to backup file
                self._save_backup(patient_data, transcript_filepath)
                return {"success": False, "error": "Database save failed", "patient_data": patient_data}

            patient_id = saved_record.get("patient_id")
            logger.info(f"Successfully saved patient data to Supabase with ID: {patient_id}")

            # Step 3: Match patient to clinical trials
            try:
                from clinical_trials_matcher import match_patient_to_trials

                logger.info("Starting clinical trial matching...")
                nct_ids = match_patient_to_trials(patient_data)

                if nct_ids:
                    # Update patient record with eligible trials
                    updated_record = db.update_eligible_trials(patient_id, nct_ids)
                    if updated_record:
                        logger.info(f"✅ Matched {len(nct_ids)} clinical trials for patient {patient_id}")
                    else:
                        logger.warning(f"Trial matching found {len(nct_ids)} trials but failed to update database")
                else:
                    logger.info(f"No matching clinical trials found for patient {patient_id}")

            except Exception as e:
                logger.error(f"Error during clinical trial matching: {e}", exc_info=True)
                # Don't fail the whole operation if trial matching fails
                logger.warning("Continuing despite trial matching error")

            return {
                "success": True,
                "patient_id": patient_id,
                "patient_data": patient_data,
                "database_record": saved_record,
                "matched_trials": nct_ids if 'nct_ids' in locals() else []
            }

        except Exception as e:
            logger.error(f"Error in parse_and_save_to_db: {e}", exc_info=True)
            return {"success": False, "error": str(e), "patient_id": None}

    def _save_backup(self, patient_data: Dict[str, Any], transcript_path: str):
        """
        Save extracted patient data as backup JSON if database save fails.

        Args:
            patient_data: Extracted patient information
            transcript_path: Original transcript path
        """
        try:
            backup_dir = Path("transcripts/parsed_backups")
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            room = self.metadata.get("room_name", "unknown")
            backup_file = backup_dir / f"parsed_{room}_{timestamp}.json"

            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(patient_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved backup to {backup_file}")

        except Exception as e:
            logger.error(f"Failed to save backup: {e}")


# Global transcript manager instance
transcript_manager = TranscriptManager()


def get_transcript_manager() -> TranscriptManager:
    """Get the global transcript manager instance."""
    return transcript_manager


async def save_transcript_on_shutdown(session, room_name: str):
    """
    Callback function to save transcript when the session ends.

    Args:
        session: The LiveKit AgentSession object
        room_name: The name of the room
    """
    try:
        transcript_manager.set_metadata(room_name=room_name)
        transcript_manager.load_from_session_history(session.history)
        filepath = transcript_manager.save_to_file()
        logger.info(f"Session ended. Transcript saved to {filepath}")
    except Exception as e:
        logger.error(f"Error saving transcript on shutdown: {e}")
