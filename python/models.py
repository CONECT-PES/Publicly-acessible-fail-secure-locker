from sqlalchemy import Column, Integer, String, DateTime , Enum
from datetime import datetime, timezone 
from database import Base
import enum


class LockerStatus(enum.Enum):
    available="Available"
    occupied="Occupied"
    

class Locker(Base):
    __tablename__ = 'locker'

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(15), nullable=True, default="NA") 
    password= Column(String(255), nullable=False,default="NA")
    created_on = Column(DateTime, default=(datetime.now(timezone.utc)))  
    status = Column(Enum(LockerStatus), nullable=False, default="Available")
    unlock_time= Column(DateTime, nullable=True, default=datetime.now(timezone.utc))