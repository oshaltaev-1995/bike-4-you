from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import jwt
from passlib.context import CryptContext

import models
import schemas
from database import Base, engine
from deps import get_db

# ---------- CONFIG ----------

SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_ME"   # поменяй при деплое
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

KAMK_DOMAIN = "@kamk.fi"

origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200"
]

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bike4You AuthService", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- UTILS ----------

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# ---------- ENDPOINTS ----------

@app.post("/auth/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    if not user_in.email.endswith(KAMK_DOMAIN):
        raise HTTPException(status_code=400, detail="Email must end with @kamk.fi")

    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = models.User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),   # 🔥 HASH PASSWORD
        role="user",
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=schemas.Token)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    if not data.email.endswith(KAMK_DOMAIN):
        raise HTTPException(status_code=400, detail="Email must end with @kamk.fi")

    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not registered")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })

    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@app.get("/auth/me", response_model=schemas.UserOut)
def get_me(token: str, db: Session = Depends(get_db)):
    """
    Фронтенд будет отправлять токен, мы его декодируем.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.post("/auth/make-admin/{user_id}", response_model=schemas.UserOut)
def make_admin(user_id: int, db: Session = Depends(get_db)):
    """
    Можно вызывать через Swagger, чтобы назначить администратора.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = "admin"
    db.commit()
    db.refresh(user)
    return user
