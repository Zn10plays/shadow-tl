from pydantic import BaseModel
from typing import List

class Info(BaseModel):
    """
    Model to represent character or place information.
    """
    translated_name: str
    orignal_name: str
    classification: str
    description: str


class TranslatedResults(BaseModel):
    """
    Model to represent the translated results.
    """
    translated_title: str
    summary: str
    character_bible: List[Info]
    notes_for_next_chapter: str
    translated_content: str

