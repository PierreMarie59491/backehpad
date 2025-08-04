from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from datetime import datetime
import random

from models.quiz import QuizQuestion, QuizQuestionCreate, QuizTheme, QuizSession, QuizAnswer
from database import get_database

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.get("/themes", response_model=List[QuizTheme])
async def get_themes(db: AsyncIOMotorClient = Depends(get_database)):
    themes = await db.quiz_themes.find().sort("order", 1).to_list(100)
    return [QuizTheme(**theme) for theme in themes]

@router.get("/themes/{theme_id}/questions", response_model=List[QuizQuestion])
async def get_theme_questions(theme_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    questions = await db.quiz_questions.find({"theme": theme_id}).to_list(100)
    return [QuizQuestion(**question) for question in questions]

@router.post("/questions", response_model=QuizQuestion)
async def create_question(question_data: QuizQuestionCreate, db: AsyncIOMotorClient = Depends(get_database)):
    question = QuizQuestion(**question_data.dict())
    await db.quiz_questions.insert_one(question.dict())
    
    # Update theme questions count
    await db.quiz_themes.update_one(
        {"id": question.theme},
        {"$inc": {"questions_count": 1}}
    )
    
    return question

@router.post("/sessions", response_model=QuizSession)
async def start_quiz_session(user_id: str, theme: str, db: AsyncIOMotorClient = Depends(get_database)):
    # Get all questions for the theme
    questions = await db.quiz_questions.find({"theme": theme}).to_list(100)
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this theme")
    
    # Randomize questions
    random.shuffle(questions)
    question_ids = [q["id"] for q in questions]
    
    session = QuizSession(
        user_id=user_id,
        theme=theme,
        questions=question_ids
    )
    
    await db.quiz_sessions.insert_one(session.dict())
    return session

@router.get("/sessions/{session_id}", response_model=QuizSession)
async def get_quiz_session(session_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    session = await db.quiz_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return QuizSession(**session)

@router.post("/sessions/{session_id}/answer")
async def submit_answer(
    session_id: str, 
    question_id: str, 
    user_answer: int, 
    db: AsyncIOMotorClient = Depends(get_database)
):
    session = await db.quiz_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    question = await db.quiz_questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    is_correct = user_answer == question["correct_answer"]
    
    # Save answer
    answer = QuizAnswer(
        session_id=session_id,
        question_id=question_id,
        user_answer=user_answer,
        is_correct=is_correct
    )
    await db.quiz_answers.insert_one(answer.dict())
    
    # Update session
    new_score = session["score"] + (1 if is_correct else 0)
    new_current_question = session["current_question"] + 1
    
    update_data = {
        "score": new_score,
        "current_question": new_current_question,
        "$push": {"answers": user_answer}
    }
    
    # Check if quiz is completed
    if new_current_question >= len(session["questions"]):
        update_data["completed"] = True
        update_data["completed_at"] = datetime.utcnow()
    
    await db.quiz_sessions.update_one({"id": session_id}, {"$set": update_data})
    
    return {
        "is_correct": is_correct,
        "correct_answer": question["correct_answer"],
        "explanation": question["explanation"],
        "score": new_score,
        "completed": update_data.get("completed", False)
    }

@router.get("/sessions/{session_id}/results")
async def get_quiz_results(session_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    session = await db.quiz_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session["completed"]:
        raise HTTPException(status_code=400, detail="Quiz not completed yet")
    
    total_questions = len(session["questions"])
    score = session["score"]
    percentage = (score / total_questions) * 100
    
    return {
        "score": score,
        "total_questions": total_questions,
        "percentage": percentage,
        "passed": percentage >= 70,
        "theme": session["theme"],
        "completed_at": session["completed_at"]
    }