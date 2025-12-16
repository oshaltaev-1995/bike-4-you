from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
import jwt
import os

import models
import schemas
from database import Base, engine
from deps import get_db

# --------------------------
# CONFIG
# --------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "SUPER_SECRET_KEY_CHANGE_ME")
ALGORITHM = "HS256"

bearer = HTTPBearer()

# --------------------------
# AUTH MODELS
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
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    return TokenUser(
        user_id=int(payload["sub"]),
        role=payload["role"],
    )


def get_admin_user(current: TokenUser = Depends(get_current_user)) -> TokenUser:
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
    title="Bike4You InventoryService",
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

        # render backends (swagger + inter-service)
        "https://bike4you-auth.onrender.com",
        "https://bike4you-inventory.onrender.com",
        "https://bike4you-rental.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# ROUTES
# --------------------------

@app.get("/equipment", response_model=List[schemas.EquipmentOut])
def list_equipment(
    status: Optional[str] = Query(default=None),
    type_: Optional[str] = Query(default=None, alias="type"),
    db: Session = Depends(get_db),
    user: TokenUser = Depends(get_current_user),
):
    query = db.query(models.Equipment)

    if status is not None:
        query = query.filter(models.Equipment.status == status)

    if type_ is not None:
        query = query.filter(models.Equipment.type == type_)

    return query.all()


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
    admin: TokenUser = Depends(get_admin_user),
):
    item = db.query(models.Equipment).filter(
        models.Equipment.id == update.id
    ).first()

    if not item:
        raise HTTPException(404, "Equipment not found")

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
def get_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    user: TokenUser = Depends(get_current_user),
):
    item = db.query(models.Equipment).filter(
        models.Equipment.id == equipment_id
    ).first()

    if not item:
        raise HTTPException(404, "Equipment not found")

    return item


@app.get("/health")
def health():
    return {"status": "ok", "service": "inventory-service"}


# --------------------------
# CUSTOM OPENAPI (Swagger Bearer)
# --------------------------

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Bike4You InventoryService",
        version="1.0.0",
        routes=app.routes,
    )

    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
