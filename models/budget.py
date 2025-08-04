from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class BudgetExpense(BaseModel):
    category: str
    amount: float

class BudgetQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str] = None

class BudgetScenario(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    budget: float
    expenses: List[BudgetExpense]
    questions: List[BudgetQuestion]
    difficulty: str = "medium"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BudgetScenarioCreate(BaseModel):
    title: str
    description: str
    budget: float
    expenses: List[BudgetExpense]
    questions: List[BudgetQuestion]
    difficulty: str = "medium"

class BudgetSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    scenario_id: str
    answers: List[int] = []
    score: int = 0
    completed: bool = False
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class BudgetCalculation(BaseModel):
    user_id: str
    total_budget: float
    categories: List[BudgetExpense]
    total_spent: float
    remaining: float
    is_over_budget: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)