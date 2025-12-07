from datetime import datetime
import math
import os
from typing import List

import requests
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt

import models
import schemas
from database import Base, engine
from deps import get_db

# ---------- DB ----------
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bike4You RentalService", version="1.0.0")

# ---------- CORS ----------
origins = [
    "http://localhost:4200",
    "https://bike4you.onrender.com",
    "https://*.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- JWT ----------
SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_ME"
ALGORITHM = "HS256"


class TokenUser(BaseModel):
    user_id: int
    role: str


def get_current_user(authorization: str = Header(...)) -> TokenUser:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization header")

    token = authorization.split(" ", 1)[1].strip()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid token")

    user_id = payload.get("sub")
    role = payload.get("role")
    if user_id is None or role is None:
        raise HTTPException(401, "Invalid token payload")

    return TokenUser(user_id=int(user_id), role=role)


def get_admin_user(current_user: TokenUser = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin privileges required")
    return current_user


# ---------- Inventory service ----------
INVENTORY_SERVICE_URL = os.getenv(
    "INVENTORY_SERVICE_URL", 
    "http://inventory-service:8000"
)


# ---------- Helper functions ----------
def get_equipment_hourly_rate(equipment_id: int, authorization: str) -> float:
    url = f"{INVENTORY_SERVICE_URL}/equipment/{equipment_id}"
    resp = requests.get(url, headers={"Authorization": authorization}, timeout=3)

    if resp.status_code != 200:
        raise HTTPException(502, "Failed to fetch equipment from inventory-service")

    data = resp.json()
    return float(data["hourly_rate"])


def calculate_rental_price(start_time: datetime, end_time: datetime, hourly_rate: float):
    delta = end_time - start_time
    minutes = max(1, math.ceil(delta.total_seconds() / 60))
    hours = max(1, math.ceil(minutes / 60))
    return minutes, hours * hourly_rate


# ---------- API ENDPOINTS ----------

@app.post("/rentals/start", response_model=schemas.Rental, tags=["rentals"])
def start_rental(
    rental_in: schemas.RentalCreate,
    db: Session = Depends(get_db),
    current: TokenUser = Depends(get_current_user),
    authorization: str = Header(...),
):
    rental = models.Rental(
        user_id=current.user_id,
        equipment_id=rental_in.equipment_id,
        start_time=datetime.utcnow(),
        status="active",
    )
    db.add(rental)
    db.commit()
    db.refresh(rental)

    # Update equipment → rented
    requests.post(
        f"{INVENTORY_SERVICE_URL}/equipment/update",
        json={"id": rental_in.equipment_id, "status": "rented"},
        headers={"Authorization": authorization},
        timeout=3,
    )

    return rental


@app.post("/rentals/return/{rental_id}", response_model=schemas.Rental, tags=["rentals"])
def return_rental(
    rental_id: int,
    db: Session = Depends(get_db),
    current: TokenUser = Depends(get_current_user),
    authorization: str = Header(...),
):
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(404, "Rental not found")

    if rental.user_id != current.user_id and current.role != "admin":
        raise HTTPException(403, "Not your rental")

    if rental.status != "active":
        raise HTTPException(400, "Rental already completed")

    end_time = datetime.utcnow()
    hourly_rate = get_equipment_hourly_rate(rental.equipment_id, authorization)

    minutes, total_price = calculate_rental_price(
        rental.start_time, end_time, hourly_rate
    )

    rental.end_time = end_time
    rental.total_minutes = minutes
    rental.total_price = total_price
    rental.status = "completed"

    db.commit()
    db.refresh(rental)

    # Update equipment → available
    requests.post(
        f"{INVENTORY_SERVICE_URL}/equipment/update",
        json={"id": rental.equipment_id, "status": "available"},
        headers={"Authorization": authorization},
        timeout=3,
    )

    return rental


@app.get("/rentals/my", response_model=List[schemas.Rental], tags=["rentals"])
def get_my_rentals(
    db: Session = Depends(get_db),
    current: TokenUser = Depends(get_current_user),
):
    return (
        db.query(models.Rental)
        .filter(models.Rental.user_id == current.user_id)
        .order_by(models.Rental.start_time.desc())
        .all()
    )


@app.get("/rentals/all", response_model=List[schemas.Rental], tags=["rentals"])
def get_all_rentals(
    db: Session = Depends(get_db),
    admin: TokenUser = Depends(get_admin_user),
):
    return db.query(models.Rental).order_by(models.Rental.start_time.desc()).all()


@app.get("/rentals/{rental_id}", response_model=schemas.Rental, tags=["rentals"])
def get_rental(
    rental_id: int,
    db: Session = Depends(get_db),
    current: TokenUser = Depends(get_current_user),
):
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()

    if not rental:
        raise HTTPException(404, "Rental not found")

    if rental.user_id != current.user_id and current.role != "admin":
        raise HTTPException(403, "Not your rental")

    return rental


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "rental-service"}
