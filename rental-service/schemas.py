from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RentalCreate(BaseModel):
    user_id: int
    equipment_id: int

class RentalReturn(BaseModel):
    rental_id: int

class RentalOut(BaseModel):
    id: int
    user_id: int
    equipment_id: int
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    total_minutes: Optional[int]

    class Config:
        orm_mode = True
