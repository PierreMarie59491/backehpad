from fastapi import FastAPI, APIRouter, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import logging
import os
import uuid
import asyncio

asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# Import routes
from routes.users import router as users_router
from routes.quiz import router as quiz_router
from routes.activities import router as activities_router
from routes.budget import router as budget_router
from routes.config import router as config_router
from database import get_database, init_database
from routes.auth import router as auth_router


# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    logger.info("✅ Database initialized")
    yield
    db = await get_database()
    db.client.close()
    logger.info("🛑 Database connection closed")

# Create FastAPI app with lifespan
app = FastAPI(title="EHPAD Academy API", version="1.0.0", lifespan=lifespan)

# Middleware (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["http://localhost:3000","https://frontehpad.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Ajout du WebSocket endpoint ici ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message received: {data}")

# Router with /api prefix
api_router = APIRouter(prefix="/api")

# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Status endpoints
@api_router.get("/")
async def root():
    return {"message": "EHPAD Academy API is running"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    db = await get_database()
    status_obj = StatusCheck(**input.dict())
    await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    db = await get_database()
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**item) for item in status_checks]

# Register feature routes
api_router.include_router(users_router)
api_router.include_router(quiz_router)
api_router.include_router(activities_router)
api_router.include_router(budget_router)
api_router.include_router(config_router)
api_router.include_router(auth_router, prefix="/auth")


# Register router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
