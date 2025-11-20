from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EquipmentCreate(BaseModel):
    type: str
    status: str
    location: str


class EquipmentUpdate(BaseModel):
    id: int
    status: Optional[str] = None
    location: Optional[str] = None


class EquipmentOut(BaseModel):
    id: int
    type: str
    status: str
    location: str
    created_at: datetime

    class Config:
        orm_mode = True
