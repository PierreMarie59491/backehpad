from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from models.user import User
from utils.auth import get_password_hash, verify_password, create_access_token
from database import get_database
from bson import ObjectId
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
ALGORITHM = "HS256"

# ---------- Pydantic models ----------

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# ---------- Register route ----------

@router.post("/register")
async def register(user: UserRegister):
    db = await get_database()
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    hashed_pw = get_password_hash(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_pw
    )

    await db.users.insert_one(new_user.dict())
    return {"message": "Utilisateur créé avec succès"}

# ---------- Login route ----------

@router.post("/login")
async def login(user: UserLogin):
    db = await get_database()
    stored = await db.users.find_one({"email": user.email})

    if not stored:
        print("❌ Utilisateur non trouvé pour:", user.email)
    elif not verify_password(user.password, stored["hashed_password"]):
        print("❌ Mot de passe incorrect pour:", user.email)
    else:
        print("✅ Connexion réussie pour:", user.email)

    if not stored or not verify_password(user.password, stored["hashed_password"]):
        raise HTTPException(status_code=400, detail="Identifiants invalides")

    token = create_access_token({"sub": str(stored["_id"])})
    print("🔐 Token généré:", token)
    return {"access_token": token, "token_type": "bearer"}

# ---------- Protected route ----------

@router.get("/me")
async def get_me(access_token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token invalide")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

    db = await get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    user["id"] = str(user["_id"])
    del user["_id"]
    del user["hashed_password"]
    return user
