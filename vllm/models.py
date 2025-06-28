from pydantic import BaseModel
from typing import List

class Info(BaseModel):
    """
    Model to represent character or place information.
    """
    name: str
    description: str

class TranslatedResults(BaseModel):
    """
    Model to represent the translated results.
    """
    summary: str
    title: str
    content: str
    character_bible: List[Info]
    notes_for_next_chapter: str

