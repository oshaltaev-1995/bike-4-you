from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# ==========================
# USER MODEL FOR JWT
# ==========================

class TokenUserBase(BaseModel):
    user_id: int
    role: str


# ==========================
# BASE MODELS
# ==========================

class RentalBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    equipment_id: int


# ==========================
# CREATE MODEL
# ==========================

class RentalCreate(BaseModel):
    equipment_id: int


# ==========================
# DB MODEL
# ==========================

class RentalInDBBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    equipment_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    total_minutes: Optional[int] = None
    total_price: Optional[float] = None
    penalty_eur: float


# ==========================
# RESPONSE MODEL
# ==========================

class Rental(RentalInDBBase):
    pass


# ==========================
# LIST MODEL
# ==========================

class RentalList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[Rental]
