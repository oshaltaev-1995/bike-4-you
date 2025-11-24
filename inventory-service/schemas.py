from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class EquipmentBase(BaseModel):
    type: str
    status: str
    location: str
    image_url: Optional[str] = None
    hourly_rate: float  # ← Добавили


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    id: int
    status: Optional[str] = None
    location: Optional[str] = None
    image_url: Optional[str] = None
    hourly_rate: Optional[float] = None  # ← Разрешаем обновлять тариф


class EquipmentOut(EquipmentBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
