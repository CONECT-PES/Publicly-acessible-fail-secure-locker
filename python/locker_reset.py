from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Locker
from schemas import LockerCreate, LockerUpdate
from typing import List, Optional
from datetime import datetime, timezone  
from result import Result
import requests



def update_locker_function(db: Session, locker_id: int, locker_data: LockerUpdate) -> Result[Locker]:
    try:
        db_locker = db.query(Locker).filter(Locker.id == locker_id).first()
        if not db_locker:
            return Result(error="Locker not found.")
            
        update_data=locker_data.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(db_locker, key, value)
        db_locker.created_on=datetime.now(timezone.utc)
        db_locker.status="Occupied"
        db.commit()
        db.refresh(db_locker)
        return Result(value=db_locker)

    except SQLAlchemyError:
        db.rollback()
        return Result(error=f"An error occurred while updating the locker with ID {locker_id}")


def get_unlocked_function(db: Session, skip: int = 0, limit: int = 10) -> Result[List[Locker]]: 
     try:
         
         lockers = db.query(Locker).filter(Locker.status == "Available").all()
         return Result(value=lockers)
        
     except SQLAlchemyError:
         return Result(error="Could not retrieve the list of available lockers. Please try again.")

from sqlalchemy.orm import Session
from models import Locker 
from database import engine
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

def initialize_default_lockers(db: Session):   
    try:
        
        for locker_id in range(1,9):
            
            db_locker = db.query(Locker).filter(Locker.id == locker_id).first()                
            db_locker.phone = "NA" 
            db_locker.password = "NA"  
            db_locker.status = "Available"  
            db_locker.createdon = datetime.now(timezone.utc)
            db_locker.unlock_time=datetime.now(timezone.utc)
            db.commit()
            
        print("8 lockers reset to default values.")
        
    except SQLAlchemyError:
        db.rollback()
        return Result(error="An error occurred while initializing the lockers. No changes were made to the database.")



if __name__ == "__main__":
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    initialize_default_lockers(db)
    db.close()
