from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)      # bike, scooter, ski
    status = Column(String, nullable=False)    # available, rented
    location = Column(String, nullable=False)  # campus, dorm
    created_at = Column(DateTime, default=datetime.utcnow)
