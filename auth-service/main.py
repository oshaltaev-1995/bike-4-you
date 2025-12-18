from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import os

import models
import schemas
from database import Base, engine
from deps import get_db

# =========================
# APP INIT
# =========================

app = FastAPI(
    title="Bike4You AuthService",
    version="2.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

Base.metadata.create_all(bind=engine)

# =========================
# CONFIG
# =========================

SECRET_KEY = os.getenv("SECRET_KEY", "SUPER_SECRET_KEY_CHANGE_ME")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
KAMK_DOMAIN = "@kamk.fi"

# =========================
# CORS (🔥 FIXED 🔥)
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # local dev
        "http://localhost:4200",
        "http://127.0.0.1:4200",

        # ✅ ACTUAL Render frontend domain
        "https://bike-4-you-1.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# HELPERS
# =========================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(user_id: int, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# =========================
# ENDPOINTS
# =========================

@app.post("/auth/register", response_model=schemas.Token)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):

    if not user_in.email.endswith(KAMK_DOMAIN):
        raise HTTPException(400, "Email must end with @kamk.fi")

    existing = db.query(models.User).filter(
        models.User.email == user_in.email
    ).first()
    if existing:
        raise HTTPException(400, "User already exists")

    user = models.User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role="user",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.role)

    return schemas.Token(
        access_token=token,
        token_type="bearer",
        user=user,
    )


@app.post("/auth/login", response_model=schemas.Token)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.email == data.email
    ).first()
    if not user:
        raise HTTPException(404, "User not found")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(400, "Incorrect password")

    token = create_access_token(user.id, user.role)

    return schemas.Token(
        access_token=token,
        token_type="bearer",
        user=user,
    )


@app.get("/auth/me", response_model=schemas.UserOut)
def get_me(token: str, db: Session = Depends(get_db)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid token")

    user = db.query(models.User).filter(
        models.User.id == int(payload["sub"])
    ).first()

    if not user:
        raise HTTPException(404, "User not found")

    return user
