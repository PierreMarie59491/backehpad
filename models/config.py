from pydantic import BaseModel
from typing import List

class Avatar(BaseModel):
    id: str
    name: str
    image: str
    unlocked: bool = False
    required_level: int = 1

class Badge(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    condition: str  # description of how to unlock

class GameConfig(BaseModel):
    avatars: List[Avatar]
    badges: List[Badge]
    themes: List[dict]
    xp_per_correct_answer: int = 20
    xp_per_activity_creation: int = 50
    xp_per_budget_simulation: int = 30
    xp_per_level: int = 100