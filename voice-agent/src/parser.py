import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from anthropic import Anthropic

logger = logging.getLogger("parser")


class TranscriptParser:
    """Parse conversation transcripts using Claude AI to extract structured patient data."""

    def __init__(self, api_key: str = None):
        """
        Initialize the parser with Anthropic API key.

        Args:
            api_key: Anthropic API key. If None, reads from environment.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"  # Latest available Claude 3.5 Sonnet model

    def parse_transcript(self, transcript_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse a transcript file and extract patient data.

        Args:
            transcript_path: Path to the transcript JSON file

        Returns:
            Dictionary with extracted patient data, or None if parsing fails
        """
        try:
            # Load transcript
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_data = json.load(f)

            logger.info(f"Loaded transcript from {transcript_path}")

            # Extract messages
            messages = transcript_data.get("transcript", [])
            if not messages:
                logger.warning(f"No messages found in transcript {transcript_path}")
                return None

            # Convert to conversation format
            conversation_text = self._format_conversation(messages)

            # Extract data using Claude
            extracted_data = self._extract_patient_data(conversation_text)

            # Add metadata
            extracted_data["transcript_path"] = str(transcript_path)
            extracted_data["room_name"] = transcript_data.get("metadata", {}).get("room_name", "unknown")
            extracted_data["extraction_timestamp"] = datetime.now().isoformat()

            # Validate
            validated_data = self._validate_extracted_data(extracted_data)

            logger.info(f"Successfully parsed transcript: {transcript_path}")
            return validated_data

        except Exception as e:
            logger.error(f"Error parsing transcript {transcript_path}: {e}", exc_info=True)
            return None

    def _format_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """
        Format transcript messages into a readable conversation.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Formatted conversation string
        """
        lines = []
        for msg in messages:
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            lines.append(f"[{timestamp}] {role}: {content}")

        return "\n".join(lines)

    def _extract_patient_data(self, conversation_text: str) -> Dict[str, Any]:
        """
        Use Claude tool-use to force a structured JSON object and normalize speech-style inputs.
        """
        system = (
            "You extract patient data from a noisy voice transcript.\n"
            "Rules:\n"
            "- Convert spoken numbers to digits (e.g., 'six six nine two five five three nine eight four' -> '6692553984').\n"
            "- Convert emails like 'smith family at gmail dot com' -> 'smithfamily@gmail.com' (remove spaces in local part).\n"
            "- Normalize phone numbers to E.164-like digits only (no spaces or words); if you can derive a US number, format as +1XXXXXXXXXX; otherwise raw digits.\n"
            "- Interpret month/day/year spoken as words (e.g., 'July' + 'twenty first' + 'two thousand five' -> '2005-07-21').\n"
            "- If a field is clearly wrong (DOB in the future, age >120, etc.), set it to null.\n"
            "- Only infer from what’s said in the conversation; do not invent.\n"
            "- Return the result by calling the `patient_record` tool exactly once."
        )

        tool_schema = {
            "name": "patient_record",
            "description": "Structured patient record extracted from conversation",
            "input_schema": {
                "type": "object",
                "properties": {
                    "first_name": {"type": ["string", "null"]},
                    "last_name": {"type": ["string", "null"]},
                    "date_of_birth": {
                        "type": ["string", "null"],
                        "description": "YYYY-MM-DD"
                    },
                    "gender": {"type": ["string", "null"]},
                    "age": {"type": ["integer", "null"]},
                    "contact_email": {"type": ["string", "null"]},
                    "phone_number": {"type": ["string", "null"]},
                    "location": {"type": ["string", "null"]},
                    "diagnosed_conditions": {"type": "array", "items": {"type": "string"}},
                    "current_medications": {"type": "array", "items": {"type": "string"}},
                    "condition_summary": {"type": ["string", "null"]}
                },
                "required": [
                    "first_name","last_name","date_of_birth","gender","age",
                    "contact_email","phone_number","location",
                    "diagnosed_conditions","current_medications","condition_summary"
                ],
                "additionalProperties": False
            }
        }

        try:
            resp = self.client.messages.create(
                model=self.model,             # e.g., "claude-3-5-sonnet-20241022" or "claude-3-5-sonnet-latest"
                max_tokens=800,
                temperature=0,
                system=system,
                messages=[{"role": "user", "content": conversation_text}],
                tools=[tool_schema],
            )

            # Prefer tool_use result
            for block in resp.content:
                if getattr(block, "type", None) == "tool_use" and getattr(block, "name", "") == "patient_record":
                    # Claude already returns a parsed dict for tool inputs in the SDK
                    extracted = dict(block.input)
                    return extracted

            # Fallback: text block (rare with tools, but just in case)
            for block in resp.content:
                if getattr(block, "type", None) == "text":
                    txt = block.text.strip()
                    # strip code fences if present
                    if txt.startswith("```"):
                        txt = txt.split("```", 2)[1]
                        if txt.startswith("json"):
                            txt = txt[4:].strip()
                    return json.loads(txt)

            logger.warning("Claude response had no tool_use or text content; returning empty structure.")
            return self._get_empty_patient_data()

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error from Claude: {e}", exc_info=True)
            return self._get_empty_patient_data()
        except Exception as e:
            logger.error(f"Claude tool call failed: {e}", exc_info=True)
            return self._get_empty_patient_data()


    def _validate_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean extracted patient data.

        Args:
            data: Raw extracted data

        Returns:
            Validated and cleaned data
        """
        validated = data.copy()

        # Ensure required fields exist
        required_fields = [
            "first_name", "last_name", "date_of_birth", "gender", "age",
            "contact_email", "phone_number", "location",
            "diagnosed_conditions", "current_medications", "condition_summary"
        ]

        for field in required_fields:
            if field not in validated:
                if field in ["diagnosed_conditions", "current_medications"]:
                    validated[field] = []
                else:
                    validated[field] = None

        # Validate email format (basic)
        if validated.get("contact_email"):
            email = validated["contact_email"]
            if "@" not in email or "." not in email.split("@")[-1]:
                logger.warning(f"Invalid email format: {email}")
                validated["email_valid"] = False
            else:
                validated["email_valid"] = True

        # Validate age if present
        if validated.get("age"):
            try:
                age = int(validated["age"])
                if age < 0 or age > 120:
                    logger.warning(f"Age out of reasonable range: {age}")
                    validated["age"] = None
            except (ValueError, TypeError):
                logger.warning(f"Invalid age value: {validated['age']}")
                validated["age"] = None

        # Validate date of birth format (basic)
        if validated.get("date_of_birth"):
            dob = validated["date_of_birth"]
            try:
                datetime.strptime(dob, "%Y-%m-%d")
                validated["dob_valid"] = True
            except ValueError:
                logger.warning(f"Invalid date_of_birth format: {dob}")
                validated["dob_valid"] = False

        # Ensure arrays are lists
        for field in ["diagnosed_conditions", "current_medications"]:
            if not isinstance(validated.get(field), list):
                validated[field] = []

        # Add confidence flag (simple heuristic)
        filled_fields = sum(1 for v in validated.values() if v not in [None, [], ""])
        validated["extraction_confidence"] = "high" if filled_fields >= 8 else "medium" if filled_fields >= 5 else "low"

        return validated

    def _get_empty_patient_data(self) -> Dict[str, Any]:
        """
        Return empty patient data structure.

        Returns:
            Dictionary with all fields set to None or empty
        """
        return {
            "first_name": None,
            "last_name": None,
            "date_of_birth": None,
            "gender": None,
            "age": None,
            "contact_email": None,
            "phone_number": None,
            "location": None,
            "diagnosed_conditions": [],
            "current_medications": [],
            "condition_summary": None,
            "extraction_confidence": "low"
        }

    def parse_multiple_transcripts(self, transcript_dir: str = "transcripts") -> List[Dict[str, Any]]:
        """
        Parse all transcripts in a directory.

        Args:
            transcript_dir: Directory containing transcript JSON files

        Returns:
            List of extracted patient data dictionaries
        """
        results = []
        transcript_path = Path(transcript_dir)

        if not transcript_path.exists():
            logger.warning(f"Transcript directory not found: {transcript_dir}")
            return results

        for transcript_file in transcript_path.glob("*.json"):
            logger.info(f"Processing {transcript_file.name}...")
            data = self.parse_transcript(str(transcript_file))
            if data:
                results.append(data)

        logger.info(f"Processed {len(results)} transcripts")
        return results


# Helper function for easy usage
def parse_transcript_file(transcript_path: str, api_key: str = None) -> Optional[Dict[str, Any]]:
    """
    Convenience function to parse a single transcript file.

    Args:
        transcript_path: Path to transcript JSON file
        api_key: Anthropic API key (optional, reads from env if not provided)

    Returns:
        Extracted patient data or None if parsing fails
    """
    parser = TranscriptParser(api_key=api_key)
    return parser.parse_transcript(transcript_path)
