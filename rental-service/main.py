from datetime import datetime
import math
import os
from typing import List

import requests
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

import models
import schemas
from database import Base, engine
from deps import get_db

# --------------------------
# CONFIG
# --------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "SUPER_SECRET_KEY_CHANGE_ME")
ALGORITHM = "HS256"

INVENTORY_URL = os.getenv(
    "INVENTORY_SERVICE_URL",
    "http://inventory-service:8000",
)

bearer = HTTPBearer()

# --------------------------
# AUTH
# --------------------------

class TokenUser:
    def __init__(self, user_id: int, role: str):
        self.user_id = user_id
        self.role = role


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> TokenUser:
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Token expired",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid token",
        )

    return TokenUser(
        user_id=int(payload["sub"]),
        role=payload["role"],
    )


def get_admin_user(
    current: TokenUser = Depends(get_current_user),
) -> TokenUser:
    if current.role != "admin":
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Admin privileges required",
        )
    return current


# --------------------------
# APP INIT
# --------------------------

app = FastAPI(
    title="Bike4You RentalService",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

Base.metadata.create_all(bind=engine)

# --------------------------
# CORS
# --------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # local frontend
        "http://localhost:4200",
        "http://127.0.0.1:4200",

        # render frontend
        "https://bike4you-frontend.onrender.com",

        # render backends
        "https://bike4you-auth.onrender.com",
        "https://bike4you-inventory.onrender.com",
        "https://bike4you-rental.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# HELPERS
# --------------------------

def get_rate(equipment_id: int, token: str) -> float:
    resp = requests.get(
        f"{INVENTORY_URL}/equipment/{equipment_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=3,
    )

    if resp.status_code != 200:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            "Inventory service unavailable",
        )

    return float(resp.json()["hourly_rate"])


def calc_price(start: datetime, end: datetime, rate: float):
    minutes = max(1, math.ceil((end - start).total_seconds() / 60))
    hours = max(1, math.ceil(minutes / 60))
    return minutes, hours * rate


# --------------------------
# ROUTES
# --------------------------

@app.post("/rentals/start", response_model=schemas.Rental)
def start_rental(
    data: schemas.RentalCreate,
    db: Session = Depends(get_db),
    current: TokenUser = Depends(get_current_user),
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
    current: TokenUser = Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Depends(bearer),
):
    token = creds.credentials

    rental = db.query(models.Rental).filter(
        models.Rental.id == rental_id
    ).first()

    if not rental:
        raise HTTPException(404, "Rental not found")

    if rental.user_id != current.user_id and current.role != "admin":
        raise HTTPException(403, "Forbidden")

    if rental.status != "active":
        raise HTTPException(400, "Rental already completed")

    end_time = datetime.utcnow()
    rate = get_rate(rental.equipment_id, token)
    minutes, total_price = calc_price(rental.start_time, end_time, rate)

    rental.end_time = end_time
    rental.total_minutes = minutes
    rental.total_price = total_price
    rental.status = "completed"

    db.commit()
    db.refresh(rental)

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
    current: TokenUser = Depends(get_current_user),
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
    admin: TokenUser = Depends(get_admin_user),
):
    return (
        db.query(models.Rental)
        .order_by(models.Rental.start_time.desc())
        .all()
    )
