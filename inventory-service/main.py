from typing import List, Optional

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Query,
    Header,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt

import models
import schemas
from database import Base, engine
from deps import get_db

# ---------- JWT CONFIG ----------

SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_ME"
ALGORITHM = "HS256"


class TokenUser(BaseModel):
    user_id: int
    role: str


def get_current_user(authorization: str = Header(...)) -> TokenUser:
    """
    Reads header Authorization: Bearer <token>,
    decodes JWT and returns user_id + role.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    token = authorization.split(" ", 1)[1].strip()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user_id = payload.get("sub")
    role = payload.get("role")

    if user_id is None or role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return TokenUser(user_id=int(user_id), role=role)


def get_admin_user(current_user: TokenUser = Depends(get_current_user)) -> TokenUser:
    """
    Разрешает доступ только admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


# ---------- APP & DB SETUP ----------

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


# ---------- ENDPOINTS ----------

@app.get("/equipment", response_model=List[schemas.EquipmentOut])
def list_equipment(
    status: Optional[str] = Query(default=None),
    type_: Optional[str] = Query(default=None, alias="type"),
    db: Session = Depends(get_db),
    current_user: TokenUser = Depends(get_current_user),
):
    query = db.query(models.Equipment)

    if status is not None:
        query = query.filter(models.Equipment.status == status)

    if type_ is not None:
        query = query.filter(models.Equipment.type == type_)

    items = query.all()
    return items


@app.post("/equipment/add", response_model=schemas.EquipmentOut)
def add_equipment(
    data: schemas.EquipmentCreate,
    db: Session = Depends(get_db),
    admin: TokenUser = Depends(get_admin_user),
):
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
def update_equipment(
    update: schemas.EquipmentUpdate,
    db: Session = Depends(get_db),
    admin: TokenUser = Depends(get_admin_user),  # только admin
):
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
    db: Session = Depends(get_db),
    current_user: TokenUser = Depends(get_current_user),
):
    item = db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Equipment not found")

    return item
