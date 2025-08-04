from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def get_database():
    return db

# Initialize collections and indexes
async def init_database():
    # Create indexes for better performance
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    await db.quiz_questions.create_index("theme")
    await db.quiz_sessions.create_index("user_id")
    await db.activities.create_index("author_id")
    await db.activities.create_index("category")
    await db.budget_sessions.create_index("user_id")
    await db.budget_calculations.create_index("user_id")
    
    # Initialize quiz themes if they don't exist
    themes_count = await db.quiz_themes.count_documents({})
    if themes_count == 0:
        themes = [
            {"id": "legislation", "name": "Législation", "description": "Règles et lois régissant les EHPAD", "icon": "⚖️", "color": "bg-blue-500", "order": 0, "questions_count": 0},
            {"id": "animation_types", "name": "Types d'Animation", "description": "Différentes formes d'animation en EHPAD", "icon": "🎭", "color": "bg-green-500", "order": 1, "questions_count": 0},
            {"id": "project_management", "name": "Gestion de Projet", "description": "Planification et organisation d'activités", "icon": "📋", "color": "bg-purple-500", "order": 2, "questions_count": 0},
            {"id": "budget_management", "name": "Gestion de Budget", "description": "Maîtrise des aspects financiers", "icon": "💰", "color": "bg-orange-500", "order": 3, "questions_count": 0}
        ]
        await db.quiz_themes.insert_many(themes)
    
    # Initialize sample quiz questions
    questions_count = await db.quiz_questions.count_documents({})
    if questions_count == 0:
        sample_questions = [
            {
                "id": "leg_1",
                "question": "Quel est le ratio minimum d'encadrement en EHPAD ?",
                "options": ["1 soignant pour 10 résidents", "1 soignant pour 8 résidents", "1 soignant pour 6 résidents", "1 soignant pour 12 résidents"],
                "correct_answer": 1,
                "explanation": "Le ratio minimum est de 1 soignant pour 8 résidents selon la réglementation.",
                "theme": "legislation",
                "difficulty": "medium"
            },
            {
                "id": "leg_2",
                "question": "Quelle autorisation est nécessaire pour ouvrir un EHPAD ?",
                "options": ["Autorisation préfectorale", "Autorisation du conseil départemental", "Autorisation de l'ARS", "Autorisation municipale"],
                "correct_answer": 2,
                "explanation": "L'Agence Régionale de Santé (ARS) délivre l'autorisation d'ouverture.",
                "theme": "legislation",
                "difficulty": "medium"
            },
            {
                "id": "anim_1",
                "question": "Quelle activité est recommandée pour stimuler la mémoire ?",
                "options": ["Jeux de cartes", "Réminiscence", "Gymnastique douce", "Musique"],
                "correct_answer": 1,
                "explanation": "Les activités de réminiscence stimulent efficacement la mémoire autobiographique.",
                "theme": "animation_types",
                "difficulty": "easy"
            },
            {
                "id": "proj_1",
                "question": "Première étape d'un projet d'animation ?",
                "options": ["Définir les objectifs", "Choisir l'activité", "Préparer le matériel", "Évaluer les résidents"],
                "correct_answer": 3,
                "explanation": "L'évaluation des résidents est essentielle pour adapter l'activité.",
                "theme": "project_management",
                "difficulty": "medium"
            },
            {
                "id": "bud_1",
                "question": "Quel pourcentage du budget total est généralement alloué aux animations ?",
                "options": ["2-5%", "8-12%", "15-20%", "25-30%"],
                "correct_answer": 0,
                "explanation": "Le budget animation représente généralement 2 à 5% du budget total.",
                "theme": "budget_management",
                "difficulty": "hard"
            }
        ]
        await db.quiz_questions.insert_many(sample_questions)
        
        # Update theme question counts
        for theme in ["legislation", "animation_types", "project_management", "budget_management"]:
            count = len([q for q in sample_questions if q["theme"] == theme])
            await db.quiz_themes.update_one({"id": theme}, {"$set": {"questions_count": count}})
    
    # Initialize sample activities
    activities_count = await db.activities.count_documents({})
    if activities_count == 0:
        sample_activities = [
            {
                "id": "act_1",
                "title": "Atelier Cuisine Thérapeutique",
                "category": "Cognitive",
                "duration": "60 min",
                "participants": "6-8 personnes",
                "material": ["Ingrédients simples", "Ustensiles adaptés", "Tabliers"],
                "objectives": ["Stimuler la mémoire", "Favoriser la socialisation", "Maintenir l'autonomie"],
                "description": "Atelier de préparation de recettes simples favorisant les échanges et la stimulation cognitive.",
                "difficulty": "Facile",
                "author": "Équipe pédagogique",
                "author_id": None,
                "is_public": True
            },
            {
                "id": "act_2",
                "title": "Jardinage Adapté",
                "category": "Physique",
                "duration": "45 min",
                "participants": "4-6 personnes",
                "material": ["Graines", "Petits outils", "Jardinières"],
                "objectives": ["Stimulation sensorielle", "Activité physique douce", "Contact avec la nature"],
                "description": "Activité de plantation et d'entretien de plantes adaptée aux capacités des résidents.",
                "difficulty": "Moyenne",
                "author": "Équipe pédagogique",
                "author_id": None,
                "is_public": True
            }
        ]
        await db.activities.insert_many(sample_activities)
    
    # Initialize sample budget scenario
    scenarios_count = await db.budget_scenarios.count_documents({})
    if scenarios_count == 0:
        sample_scenario = {
            "id": "scen_1",
            "title": "Budget Annuel Animation",
            "description": "Vous devez gérer un budget annuel de 5000€ pour les animations d'un EHPAD de 50 résidents.",
            "budget": 5000,
            "expenses": [
                {"category": "Matériel artistique", "amount": 1200},
                {"category": "Intervenants extérieurs", "amount": 2000},
                {"category": "Sorties", "amount": 800},
                {"category": "Fêtes et événements", "amount": 1000}
            ],
            "questions": [
                {
                    "question": "Quel est le budget par résident pour l'année ?",
                    "options": ["80€", "100€", "120€", "150€"],
                    "correct_answer": 1,
                    "explanation": "5000€ / 50 résidents = 100€ par résident"
                }
            ],
            "difficulty": "medium"
        }
        await db.budget_scenarios.insert_one(sample_scenario)
    
    print("Database initialized successfully!")