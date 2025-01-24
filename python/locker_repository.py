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


def get_locked_specific(db: Session, phone_no:str, skip: int = 0, limit: int = 10) -> Result[List[Locker]]: 
     try:
         
         lockers = db.query(Locker).filter(Locker.phone == phone_no).all()
         return Result(value=lockers)
        
     except SQLAlchemyError:
         return Result(error="Could not retrieve the list of available lockers. Please try again.")


def get_locker_function(db: Session, locker_id: int) -> Result[Locker]:
    try:
        locker = db.query(Locker).filter(Locker.id == locker_id).first()
        if locker is None:
            return Result(error="Locker not found.")

        return Result(value=locker)
        
    except SQLAlchemyError:
        return Result(error="Could not retrieve locker data. Please try again.")

def delete_locker_function(db: Session, locker_id: int) -> Result[Locker]:   
    try:
        db_locker = db.query(Locker).filter(Locker.id == locker_id).first()
        if not db_locker:
            return Result(error="Locker not found.")
        
        db_locker.phone = "NA" 
        db_locker.password = "NA"  
        db_locker.status = "Available"  
        db_locker.createdon = datetime.now(timezone.utc)
        db_locker.unlock_time=datetime.now(timezone.utc)
        db.commit()
        
        
        esp_ip = "<ESP_IP_ADDRESS>"  
        relay_url = f"http://{esp_ip}/ACTIVATE_RELAY?id={locker_id}"

        
        try:
            response = requests.get(relay_url)
            if response.status_code == 200:
                print("Relay request received by ESP8266.")
            else:
                print("Failed to send request. Status code:", response.status_code)
        
        except requests.RequestException as e:
            print("Error sending request to ESP8266:", e)
        
        return Result(value=db_locker)
        
    except SQLAlchemyError:
        db.rollback()
        return Result(error="An error occurred while deleting the locker. No changes were made to the database.")


def get_locked_function(db: Session, skip: int = 0, limit: int = 10) -> Result[List[Locker]]: 
     try:
         
         lockers = db.query(Locker).filter(Locker.status == "occupied").all()
         return Result(value=lockers)
        
     except SQLAlchemyError:
         return Result(error="Could not retrieve the list of available lockers. Please try again.")
