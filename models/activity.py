from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class ActivitySheet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    category: str
    duration: str
    participants: str
    material: List[str]
    objectives: List[str]
    description: str
    difficulty: str
    author: str
    author_id: Optional[str] = None
    is_public: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ActivitySheetCreate(BaseModel):
    title: str
    category: str
    duration: str
    participants: str
    material: List[str]
    objectives: List[str]
    description: str
    difficulty: str
    author: str
    author_id: Optional[str] = None
    is_public: bool = True

class ActivitySheetUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    duration: Optional[str] = None
    participants: Optional[str] = None
    material: Optional[List[str]] = None
    objectives: Optional[List[str]] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    is_public: Optional[bool] = None

class ActivityFilter(BaseModel):
    category: Optional[str] = None
    difficulty: Optional[str] = None
    author_id: Optional[str] = None
    search: Optional[str] = None
    is_public: Optional[bool] = None