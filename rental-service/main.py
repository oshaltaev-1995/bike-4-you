from datetime import datetime
import math
import os
from typing import List, Optional

import requests
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine
from deps import get_db

# --- Создание таблиц ---
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bike4You RentalService", version="1.0.0")

# --- CORS ---
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INVENTORY_SERVICE_URL = os.getenv(
    "INVENTORY_SERVICE_URL",
    "http://inventory-service:8000"  # в докере; локально через порт: http://localhost:8002
)

# --- helpers ---

def get_equipment_hourly_rate(equipment_id: int) -> float:
    url = f"{INVENTORY_SERVICE_URL}/equipment/{equipment_id}"
    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch equipment from inventory-service: {e}"
        )

    data = resp.json()
    hourly_rate = data.get("hourly_rate")
    if hourly_rate is None:
        raise HTTPException(
            status_code=500,
            detail="hourly_rate missing in inventory response"
        )

    return float(hourly_rate)


def calculate_rental_price(start_time: datetime, end_time: datetime, hourly_rate: float):
    if end_time < start_time:
        raise ValueError("end_time cannot be earlier")

    delta = end_time - start_time
    minutes = max(1, math.ceil(delta.total_seconds() / 60))
    hours = max(1, math.ceil(minutes / 60))
    return minutes, hours * hourly_rate


# --- endpoints ---

@app.post("/rentals/start", response_model=schemas.Rental, tags=["rentals"])
def start_rental(rental_in: schemas.RentalCreate, db: Session = Depends(get_db)):
    rental = models.Rental(
        user_id=rental_in.user_id,
        equipment_id=rental_in.equipment_id,
        start_time=datetime.utcnow(),
        status="active",
    )
    db.add(rental)
    db.commit()
    db.refresh(rental)

    # Обновляем статус оборудования
    try:
        requests.post(
            f"{INVENTORY_SERVICE_URL}/equipment/update",
            json={"id": rental_in.equipment_id, "status": "rented"},
            timeout=3
        )
    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Failed to update equipment in inventory-service"
        )

    return rental


@app.post("/rentals/return/{rental_id}", response_model=schemas.Rental, tags=["rentals"])
def return_rental(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")

    if rental.status != "active":
        raise HTTPException(status_code=400, detail="Rental is not active")

    end_time = datetime.utcnow()
    hourly_rate = get_equipment_hourly_rate(rental.equipment_id)

    minutes, total_price = calculate_rental_price(
        rental.start_time, end_time, hourly_rate
    )

    rental.end_time = end_time
    rental.total_minutes = minutes
    rental.total_price = total_price
    rental.status = "completed"

    db.commit()
    db.refresh(rental)

    # Сбрасываем статус оборудования
    try:
        requests.post(
            f"{INVENTORY_SERVICE_URL}/equipment/update",
            json={"id": rental.equipment_id, "status": "available"},
            timeout=3
        )
    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Failed to update equipment status in inventory-service"
        )

    return rental


@app.get("/rentals/active", response_model=List[schemas.Rental], tags=["rentals"])
def get_active_rentals(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
):
    query = db.query(models.Rental).filter(models.Rental.status == "active")
    if user_id is not None:
        query = query.filter(models.Rental.user_id == user_id)

    rentals = query.order_by(models.Rental.start_time.desc()).all()
    return rentals


@app.get("/rentals/history", response_model=List[schemas.Rental], tags=["rentals"])
def get_rental_history(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
):
    query = db.query(models.Rental).filter(models.Rental.status != "active")
    if user_id is not None:
        query = query.filter(models.Rental.user_id == user_id)

    rentals = query.order_by(models.Rental.start_time.desc()).all()
    return rentals


@app.get("/rentals/{rental_id}", response_model=schemas.Rental, tags=["rentals"])
def get_rental_by_id(
    rental_id: int,
    db: Session = Depends(get_db),
):
    rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return rental


@app.get("/health", tags=["health"])
def health():
  return {"status": "ok", "service": "rental-service"}
