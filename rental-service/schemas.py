from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class RentalBase(BaseModel):
    user_id: int
    equipment_id: int


class RentalCreate(RentalBase):
    """
    Данные для старта аренды.
    Пока достаточно user_id и equipment_id.
    """
    pass


class RentalReturn(BaseModel):
    """
    Можно будет расширить (например, передавать комментарии/повреждения и т.п.).
    Сейчас не используется.
    """
    pass


class RentalInDBBase(BaseModel):
    id: int
    user_id: int
    equipment_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    total_minutes: Optional[int] = None
    total_price: Optional[float] = None
    penalty_eur: float

    class Config:
        orm_mode = True


class Rental(RentalInDBBase):
    """
    Модель для ответа API.
    """
    pass


class RentalList(BaseModel):
    """
    Обёртка под список, если захочется добавлять метаданные (пагинация и т.п.).
    Пока можно не использовать.
    """
    items: List[Rental]
