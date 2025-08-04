from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List

from models.config import GameConfig, Avatar, Badge
from database import get_database

router = APIRouter(prefix="/config", tags=["config"])

@router.get("/game", response_model=GameConfig)
async def get_game_config(db: AsyncIOMotorClient = Depends(get_database)):
    config = await db.game_config.find_one({"type": "main"})
    if not config:
        # Return default config if not found
        default_config = {
            "type": "main",
            "avatars": [
                {"id": "avatar1", "name": "Animateur Débutant", "image": "👨‍🏫", "unlocked": True, "required_level": 1},
                {"id": "avatar2", "name": "Animatrice Experte", "image": "👩‍🏫", "unlocked": False, "required_level": 5},
                {"id": "avatar3", "name": "Coordinateur", "image": "👨‍💼", "unlocked": False, "required_level": 10},
                {"id": "avatar4", "name": "Directrice", "image": "👩‍💼", "unlocked": False, "required_level": 15}
            ],
            "badges": [
                {"id": "first_quiz", "name": "Premier Quiz", "description": "Complété votre premier quiz", "icon": "🎯", "condition": "Complete first quiz"},
                {"id": "legislation_master", "name": "Maître de la Législation", "description": "Excellé en législation", "icon": "⚖️", "condition": "Score 80%+ in legislation"},
                {"id": "animation_expert", "name": "Expert Animation", "description": "Maîtrise des techniques d'animation", "icon": "🎭", "condition": "Score 80%+ in animation"},
                {"id": "budget_wizard", "name": "Magicien du Budget", "description": "Parfait en gestion budgétaire", "icon": "💰", "condition": "Score 80%+ in budget"},
                {"id": "creator", "name": "Créateur", "description": "Créé votre première fiche d'activité", "icon": "✨", "condition": "Create first activity"}
            ],
            "themes": [
                {"id": "legislation", "name": "Législation", "description": "Règles et lois régissant les EHPAD", "icon": "⚖️", "color": "bg-blue-500", "order": 0},
                {"id": "animation_types", "name": "Types d'Animation", "description": "Différentes formes d'animation en EHPAD", "icon": "🎭", "color": "bg-green-500", "order": 1},
                {"id": "project_management", "name": "Gestion de Projet", "description": "Planification et organisation d'activités", "icon": "📋", "color": "bg-purple-500", "order": 2},
                {"id": "budget_management", "name": "Gestion de Budget", "description": "Maîtrise des aspects financiers", "icon": "💰", "color": "bg-orange-500", "order": 3}
            ],
            "xp_per_correct_answer": 20,
            "xp_per_activity_creation": 50,
            "xp_per_budget_simulation": 30,
            "xp_per_level": 100
        }
        await db.game_config.insert_one(default_config)
        config = default_config
    
    return GameConfig(**config)

@router.get("/avatars", response_model=List[Avatar])
async def get_avatars(db: AsyncIOMotorClient = Depends(get_database)):
    config = await get_game_config(db)
    return config.avatars

@router.get("/badges", response_model=List[Badge])
async def get_badges(db: AsyncIOMotorClient = Depends(get_database)):
    config = await get_game_config(db)
    return config.badges

@router.get("/themes")
async def get_themes(db: AsyncIOMotorClient = Depends(get_database)):
    config = await get_game_config(db)
    return config.themes