from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from datetime import datetime

from models.budget import BudgetScenario, BudgetScenarioCreate, BudgetSession, BudgetCalculation
from database import get_database

router = APIRouter(prefix="/budget", tags=["budget"])

@router.get("/scenarios", response_model=List[BudgetScenario])
async def get_scenarios(db: AsyncIOMotorClient = Depends(get_database)):
    scenarios = await db.budget_scenarios.find().to_list(100)
    return [BudgetScenario(**scenario) for scenario in scenarios]

@router.get("/scenarios/{scenario_id}", response_model=BudgetScenario)
async def get_scenario(scenario_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    scenario = await db.budget_scenarios.find_one({"id": scenario_id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return BudgetScenario(**scenario)

@router.post("/scenarios", response_model=BudgetScenario)
async def create_scenario(scenario_data: BudgetScenarioCreate, db: AsyncIOMotorClient = Depends(get_database)):
    scenario = BudgetScenario(**scenario_data.dict())
    await db.budget_scenarios.insert_one(scenario.dict())
    return scenario

@router.post("/sessions", response_model=BudgetSession)
async def start_budget_session(
    user_id: str, 
    scenario_id: str, 
    db: AsyncIOMotorClient = Depends(get_database)
):
    # Verify scenario exists
    scenario = await db.budget_scenarios.find_one({"id": scenario_id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    session = BudgetSession(
        user_id=user_id,
        scenario_id=scenario_id
    )
    
    await db.budget_sessions.insert_one(session.dict())
    return session

@router.get("/sessions/{session_id}", response_model=BudgetSession)
async def get_budget_session(session_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    session = await db.budget_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return BudgetSession(**session)

@router.post("/sessions/{session_id}/answer")
async def submit_budget_answer(
    session_id: str,
    question_index: int,
    user_answer: int,
    db: AsyncIOMotorClient = Depends(get_database)
):
    session = await db.budget_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    scenario = await db.budget_scenarios.find_one({"id": session["scenario_id"]})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    if question_index >= len(scenario["questions"]):
        raise HTTPException(status_code=400, detail="Invalid question index")
    
    question = scenario["questions"][question_index]
    is_correct = user_answer == question["correct_answer"]
    
    # Update session
    new_score = session["score"] + (1 if is_correct else 0)
    new_answers = session["answers"] + [user_answer]
    
    update_data = {
        "score": new_score,
        "answers": new_answers
    }
    
    # Check if all questions are answered
    if len(new_answers) >= len(scenario["questions"]):
        update_data["completed"] = True
        update_data["completed_at"] = datetime.utcnow()
    
    await db.budget_sessions.update_one({"id": session_id}, {"$set": update_data})
    
    return {
        "is_correct": is_correct,
        "correct_answer": question["correct_answer"],
        "explanation": question.get("explanation", ""),
        "score": new_score,
        "completed": update_data.get("completed", False)
    }

@router.get("/sessions/{session_id}/results")
async def get_budget_results(session_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    session = await db.budget_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    scenario = await db.budget_scenarios.find_one({"id": session["scenario_id"]})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    if not session["completed"]:
        raise HTTPException(status_code=400, detail="Session not completed yet")
    
    total_questions = len(scenario["questions"])
    score = session["score"]
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    return {
        "score": score,
        "total_questions": total_questions,
        "percentage": percentage,
        "passed": percentage >= 70,
        "scenario_title": scenario["title"],
        "completed_at": session["completed_at"]
    }

@router.post("/calculations", response_model=BudgetCalculation)
async def save_budget_calculation(calculation: BudgetCalculation, db: AsyncIOMotorClient = Depends(get_database)):
    await db.budget_calculations.insert_one(calculation.dict())
    return calculation

@router.get("/calculations/{user_id}", response_model=List[BudgetCalculation])
async def get_user_calculations(user_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    calculations = await db.budget_calculations.find({"user_id": user_id}).to_list(100)
    return [BudgetCalculation(**calc) for calc in calculations]