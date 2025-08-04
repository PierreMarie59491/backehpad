from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from datetime import datetime

from models.activity import ActivitySheet, ActivitySheetCreate, ActivitySheetUpdate, ActivityFilter
from database import get_database

router = APIRouter(prefix="/activities", tags=["activities"])

@router.get("/", response_model=List[ActivitySheet])
async def get_activities(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    author_id: Optional[str] = None,
    search: Optional[str] = None,
    is_public: Optional[bool] = True,
    skip: int = 0,
    limit: int = 100,
    db: AsyncIOMotorClient = Depends(get_database)
):
    filter_query = {}
    
    if category:
        filter_query["category"] = category
    if difficulty:
        filter_query["difficulty"] = difficulty
    if author_id:
        filter_query["author_id"] = author_id
    if is_public is not None:
        filter_query["is_public"] = is_public
    if search:
        filter_query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"category": {"$regex": search, "$options": "i"}}
        ]
    
    activities = await db.activities.find(filter_query).skip(skip).limit(limit).to_list(limit)
    return [ActivitySheet(**activity) for activity in activities]

@router.get("/{activity_id}", response_model=ActivitySheet)
async def get_activity(activity_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    activity = await db.activities.find_one({"id": activity_id})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return ActivitySheet(**activity)

@router.post("/", response_model=ActivitySheet)
async def create_activity(activity_data: ActivitySheetCreate, db: AsyncIOMotorClient = Depends(get_database)):
    activity = ActivitySheet(**activity_data.dict())
    await db.activities.insert_one(activity.dict())
    
    # Add to user's created activities if author_id is provided
    if activity.author_id:
        await db.users.update_one(
            {"id": activity.author_id},
            {"$push": {"created_activities": activity.id}}
        )
    
    return activity

@router.put("/{activity_id}", response_model=ActivitySheet)
async def update_activity(
    activity_id: str, 
    activity_data: ActivitySheetUpdate, 
    db: AsyncIOMotorClient = Depends(get_database)
):
    activity = await db.activities.find_one({"id": activity_id})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    update_data = {k: v for k, v in activity_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.activities.update_one({"id": activity_id}, {"$set": update_data})
    
    updated_activity = await db.activities.find_one({"id": activity_id})
    return ActivitySheet(**updated_activity)

@router.delete("/{activity_id}")
async def delete_activity(activity_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    activity = await db.activities.find_one({"id": activity_id})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    await db.activities.delete_one({"id": activity_id})
    
    # Remove from user's created activities
    if activity.get("author_id"):
        await db.users.update_one(
            {"id": activity["author_id"]},
            {"$pull": {"created_activities": activity_id}}
        )
    
    return {"message": "Activity deleted successfully"}

@router.get("/categories/list")
async def get_categories(db: AsyncIOMotorClient = Depends(get_database)):
    categories = await db.activities.distinct("category")
    return {"categories": categories}

@router.get("/user/{user_id}", response_model=List[ActivitySheet])
async def get_user_activities(user_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    activities = await db.activities.find({"author_id": user_id}).to_list(100)
    return [ActivitySheet(**activity) for activity in activities]