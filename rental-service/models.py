from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
from database import Base


class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    equipment_id = Column(Integer, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="active")  # active / completed / cancelled и т.п.
    total_minutes = Column(Integer, nullable=True)
    total_price = Column(Float, nullable=True)  # общая стоимость аренды в евро
    penalty_eur = Column(Float, default=0.0)    # на будущее, штрафы и т.п.
