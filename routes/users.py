from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
from datetime import datetime

from models.user import User, UserCreate, UserUpdate, UserProgress
from database import get_database

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User)
async def create_user(user_data: UserCreate, db: AsyncIOMotorClient = Depends(get_database)):
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    user = User(**user_data.dict())
    await db.users.insert_one(user.dict())
    return user

@router.get("/", response_model=List[User])
async def list_users(db: AsyncIOMotorClient = Depends(get_database)):
    users_cursor = db.users.find()
    users = await users_cursor.to_list(100)
    return [User(**user) for user in users]

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@router.get("/email/{email}", response_model=User)
async def get_user_by_email(email: str, db: AsyncIOMotorClient = Depends(get_database)):
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user_data: UserUpdate, db: AsyncIOMotorClient = Depends(get_database)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {k: v for k, v in user_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.users.update_one({"id": user_id}, {"$set": update_data})
    updated_user = await db.users.find_one({"id": user_id})
    return User(**updated_user)

@router.post("/{user_id}/xp")
async def add_xp(user_id: str, xp_points: int, db: AsyncIOMotorClient = Depends(get_database)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_xp = user.get("xp", 0) + xp_points
    new_level = (new_xp // 100) + 1
    
    await db.users.update_one(
        {"id": user_id}, 
        {"$set": {"xp": new_xp, "level": new_level, "updated_at": datetime.utcnow()}}
    )
    updated_user = await db.users.find_one({"id": user_id})
    return User(**updated_user)

@router.post("/{user_id}/badges")
async def add_badge(user_id: str, badge_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if badge_id not in user.get("badges", []):
        await db.users.update_one(
            {"id": user_id}, 
            {"$push": {"badges": badge_id}, "$set": {"updated_at": datetime.utcnow()}}
        )
    updated_user = await db.users.find_one({"id": user_id})
    return User(**updated_user)

@router.post("/{user_id}/complete-theme")
async def complete_theme(user_id: str, theme: str, db: AsyncIOMotorClient = Depends(get_database)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if theme not in user.get("completed_themes", []):
        await db.users.update_one(
            {"id": user_id}, 
            {"$push": {"completed_themes": theme}, "$set": {"updated_at": datetime.utcnow()}}
        )
    updated_user = await db.users.find_one({"id": user_id})
    return User(**updated_user)

@router.post("/{user_id}/progress", response_model=UserProgress)
async def save_progress(user_id: str, progress: UserProgress, db: AsyncIOMotorClient = Depends(get_database)):
    progress.user_id = user_id
    await db.user_progress.insert_one(progress.dict())
    return progress

@router.get("/{user_id}/progress", response_model=List[UserProgress])
async def get_user_progress(user_id: str, db: AsyncIOMotorClient = Depends(get_database)):
    progress_list = await db.user_progress.find({"user_id": user_id}).to_list(100)
    return [UserProgress(**progress) for progress in progress_list]
