from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
from database import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)      # bike, scooter, ski
    status = Column(String, nullable=False)    # available, rented
    location = Column(String, nullable=False)  # campus, dorm
    image_url = Column(String, nullable=True)
    hourly_rate = Column(Float, nullable=False, default=4.0)  # ← Новое поле
    created_at = Column(DateTime, default=datetime.utcnow)
