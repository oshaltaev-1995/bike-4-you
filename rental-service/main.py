from datetime import datetime
import math
import os
from typing import List

import requests
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

import models
import schemas
from database import Base, engine
from deps import get_db

# ============================
# CONFIG
# ============================

SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_ME"
ALGORITHM = "HS256"

bearer = HTTPBearer()  # Swagger-compatible bearer auth
INVENTORY_URL = os.getenv("INVENTORY_URL", "http://inventory-service:8000")

# ============================
# AUTH
# ============================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid token")

    return schemas.TokenUserBase(
        user_id=int(payload["sub"]),
        role=payload["role"]
    )


def get_admin_user(current=Depends(get_current_user)):
    if current.role != "admin":
        raise HTTPException(403, "Admin only")
    return current


# ============================
# APP INIT
# ============================

app = FastAPI(
    title="Bike4You RentalService",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "https://bike4you.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================
# HELPERS
# ============================

def get_rate(equipment_id: int, token: str) -> float:
    resp = requests.get(
        f"{INVENTORY_URL}/equipment/{equipment_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=3,
    )

    if resp.status_code != 200:
        raise HTTPException(502, "Inventory service error")

    return float(resp.json()["hourly_rate"])


def calc_price(start: datetime, end: datetime, rate: float):
    minutes = math.ceil((end - start).total_seconds() / 60)
    hours = max(1, math.ceil(minutes / 60))
    return minutes, hours * rate


# ============================
# ROUTES
# ============================

@app.post("/rentals/start", response_model=schemas.Rental)
def start_rental(
    data: schemas.RentalCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(bearer),
):
    token = creds.credentials

    rental = models.Rental(
        user_id=current.user_id,
        equipment_id=data.equipment_id,
        start_time=datetime.utcnow(),
        status="active",
    )

    db.add(rental)
    db.commit()
    db.refresh(rental)

    # update inventory
    try:
        requests.post(
            f"{INVENTORY_URL}/equipment/update",
            json={"id": data.equipment_id, "status": "rented"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=3,
        )
    except Exception:
        pass

    return rental


@app.post("/rentals/return/{rental_id}", response_model=schemas.Rental)
def return_rental(
    rental_id: int,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(bearer),
):
    token = creds.credentials

    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(404, "Rental not found")

    if rental.user_id != current.user_id and current.role != "admin":
        raise HTTPException(403, "Forbidden")

    if rental.status != "active":
        raise HTTPException(400, "Already completed")

    end = datetime.utcnow()

    rate = get_rate(rental.equipment_id, token)
    minutes, total_price = calc_price(rental.start_time, end, rate)

    rental.end_time = end
    rental.total_minutes = minutes
    rental.total_price = total_price
    rental.status = "completed"

    db.commit()
    db.refresh(rental)

    # update inventory back
    try:
        requests.post(
            f"{INVENTORY_URL}/equipment/update",
            json={"id": rental.equipment_id, "status": "available"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=3,
        )
    except Exception:
        pass

    return rental


@app.get("/rentals/my", response_model=List[schemas.Rental])
def my_rentals(
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    return (
        db.query(models.Rental)
        .filter(models.Rental.user_id == current.user_id)
        .order_by(models.Rental.start_time.desc())
        .all()
    )


@app.get("/rentals/all", response_model=List[schemas.Rental])
def all_rentals(
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    return db.query(models.Rental).order_by(models.Rental.start_time.desc()).all()
