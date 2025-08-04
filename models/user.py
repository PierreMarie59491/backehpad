from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    hashed_password: str  # 🔐 nouveau champ
    avatar: str = "avatar1"
    level: int = 1
    xp: int = 0
    badges: List[str] = []
    completed_themes: List[str] = []
    created_activities: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(BaseModel):
    name: str
    email: str
    password: str  # 🔐 champ nécessaire pour l'inscription

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    level: Optional[int] = None
    xp: Optional[int] = None
    badges: Optional[List[str]] = None
    completed_themes: Optional[List[str]] = None
    created_activities: Optional[List[str]] = None

class UserProgress(BaseModel):
    user_id: str
    theme: str
    score: int
    total_questions: int
    completed: bool
    xp_earned: int
    badges_earned: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)