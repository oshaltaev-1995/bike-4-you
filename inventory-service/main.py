from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine
from deps import get_db

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bike4You InventoryService", version="1.0.0")

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
def list_equipment(
    status: Optional[str] = Query(default=None),
    type_: Optional[str] = Query(default=None, alias="type"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Equipment)

    if status is not None:
        query = query.filter(models.Equipment.status == status)

    if type_ is not None:
        query = query.filter(models.Equipment.type == type_)

    items = query.all()
    return items


@app.post("/equipment/add", response_model=schemas.EquipmentOut)
def add_equipment(data: schemas.EquipmentCreate, db: Session = Depends(get_db)):
    item = models.Equipment(
        type=data.type,
        status=data.status,
        location=data.location,
        image_url=data.image_url,
        hourly_rate=data.hourly_rate,
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
    if update.image_url is not None:
        item.image_url = update.image_url
    if update.hourly_rate is not None:
        item.hourly_rate = update.hourly_rate

    db.commit()
    db.refresh(item)
    return item


@app.get("/equipment/{equipment_id}", response_model=schemas.EquipmentOut)
def get_equipment_by_id(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    item = db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Equipment not found")

    return item
