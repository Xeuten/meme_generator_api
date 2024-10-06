from dataclasses import dataclass
from typing import Optional


@dataclass
class MemeDTO:
    template_id: int
    created_by_id: int
    top_text: Optional[str] = None
    bottom_text: Optional[str] = None


@dataclass
class RateMemeDTO:
    meme_id: int
    user_id: int
    score: int
