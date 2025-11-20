from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine
from deps import get_db

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bike4You InventoryService",
    version="1.0.0",
)

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


@app.get("/equipment", response_model=List[schemas.EquipmentOut])
def list_equipment(db: Session = Depends(get_db)):
    items = db.query(models.Equipment).all()
    return items


@app.post("/equipment/add", response_model=schemas.EquipmentOut)
def add_equipment(data: schemas.EquipmentCreate, db: Session = Depends(get_db)):
    item = models.Equipment(
        type=data.type,
        status=data.status,
        location=data.location,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.post("/equipment/update", response_model=schemas.EquipmentOut)
def update_equipment(update: schemas.EquipmentUpdate, db: Session = Depends(get_db)):
    item = db.query(models.Equipment).filter(models.Equipment.id == update.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Equipment not found")

    if update.status is not None:
        item.status = update.status
    if update.location is not None:
        item.location = update.location

    db.commit()
    db.refresh(item)
    return item
