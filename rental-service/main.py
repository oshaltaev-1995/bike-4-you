from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import models
import schemas
from database import Base, engine, SessionLocal
from deps import get_db
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

# Создать таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bike4You RentalService", version="1.0.0")

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

@app.post("/rent", response_model=schemas.RentalOut)
def rent_item(data: schemas.RentalCreate, db: Session = Depends(get_db)):
    rental = models.Rental(
        user_id = data.user_id,
        equipment_id = data.equipment_id,
        start_time = datetime.utcnow(),
        status = "active"
    )
    db.add(rental)
    db.commit()
    db.refresh(rental)
    return rental

@app.post("/return", response_model=schemas.RentalOut)
def return_item(data: schemas.RentalReturn, db: Session = Depends(get_db)):
    rental = db.query(models.Rental).filter(models.Rental.id == data.rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")

    if rental.status != "active":
        raise HTTPException(status_code=400, detail="Rental is not active")

    now = datetime.utcnow()
    rental.end_time = now
    rental.status = "closed"
    rental.total_minutes = int((now - rental.start_time).total_seconds() / 60)

    db.commit()
    db.refresh(rental)
    return rental

@app.get("/history/{user_id}", response_model=List[schemas.RentalOut])
def rental_history(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Rental).filter(models.Rental.user_id == user_id).all()
