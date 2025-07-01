from pydantic import BaseModel
from typing import List

class Info(BaseModel):
    """
    Model to represent character or place information.
    """
    name_translated: str
    orignal_name: str
    description: str

class TranslatedResults(BaseModel):
    """
    Model to represent the translated results.
    """
    title: str
    summary: str
    character_bible: List[Info]
    notes_for_next_chapter: str
    content: str

