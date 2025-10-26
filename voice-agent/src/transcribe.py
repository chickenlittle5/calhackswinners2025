import logging
import json
from datetime import datetime
from typing import List, Dict, Any

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
        Save the transcript to a JSON file.

        Args:
            filepath: Path to save the file. If None, generates a timestamped filename.
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            room = self.metadata.get("room_name", "unknown")
            filepath = f"./transcripts/transcript_{room}_{timestamp}.json"

        data = self.get_full_data()

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Transcript saved to {filepath}")
        return filepath

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
