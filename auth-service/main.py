from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import models
import schemas
from database import Base, engine
from deps import get_db
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bike4You AuthService", version="1.0.0")

origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

KAMK_DOMAIN = "@kamk.fi"


@app.post("/auth/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    if not user_in.email.endswith(KAMK_DOMAIN):
        raise HTTPException(status_code=400, detail="Email must end with @kamk.fi")

    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = models.User(name=user_in.name, email=user_in.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=schemas.UserOut)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    email = data.email

    if not email.endswith(KAMK_DOMAIN):
        raise HTTPException(status_code=400, detail="Email must end with @kamk.fi")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not registered")

    return user
