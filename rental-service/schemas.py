from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

# ==========================
# BASE MODELS
# ==========================

class RentalBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    equipment_id: int


# ==========================
# CREATE MODEL (REQUEST)
# ==========================

class RentalCreate(BaseModel):
    """
    Для старта аренды пользователь не передаёт user_id.
    Он берётся из JWT.
    """
    equipment_id: int


# ==========================
# RETURN MODEL
# ==========================

class RentalReturn(BaseModel):
    pass


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
