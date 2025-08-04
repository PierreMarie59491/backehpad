from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class QuizQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    theme: str
    difficulty: str = "medium"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class QuizQuestionCreate(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    theme: str
    difficulty: str = "medium"

class QuizTheme(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    color: str
    questions_count: int = 0
    order: int = 0

class QuizSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    theme: str
    questions: List[str]  # question IDs
    current_question: int = 0
    score: int = 0
    answers: List[int] = []
    completed: bool = False
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class QuizAnswer(BaseModel):
    session_id: str
    question_id: str
    user_answer: int
    is_correct: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)