from vllm.models import TranslatedResults
from json_repair import loads
import json

def force_validate_TranslationResults(text: str) -> tuple[TranslatedResults, bool]:
    """
    Forces a string to be the correct schema, and fills any properties that are missing.

    Args:
        text: The input string, potentially a malformed JSON.
        schema: The Pydantic schema to validate against.

    Returns:
        A Pydantic model instance with the validated and completed data.
        A boolean indicating whether the validation was successful.
    """
    try:
        # Attempt to repair and parse the JSON string
        repaired_json = loads(text)
        # Validate the repaired JSON against the schema
        validated_data = TranslatedResults.model_validate_json(json.dumps(repaired_json))
        
        return validated_data, True
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Failed to parse and validate JSON: {e}")
        # Return an empty model of the specified schema
        return TranslatedResults(
            translated_title='!!ERROR ERROR!!',
            summary='',
            character_bible=[],
            notes_for_next_chapter='',
            translated_content=''
        ), False
