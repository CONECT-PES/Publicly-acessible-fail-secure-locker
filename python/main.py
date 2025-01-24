from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db, engine, Base
from locker_service import LockerService
from result import Result


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_locker_service(db: Session = Depends(get_db)) -> LockerService:

    return LockerService(db)


@app.put("/lockers/{locker_id}", response_model=schemas.LockerOut)
def update_locker(locker_id: int, locker: schemas.LockerUpdate, locker_service: LockerService = Depends(get_locker_service)):
   
    result = locker_service.update_locker(locker_id, locker)

    if result.is_failure:
        raise HTTPException(status_code=404, detail=result.error)

    return result.value

@app.get("/lockers/empty", response_model=list[schemas.LockerOut])
def read_lockers(skip: int = 0, limit: int = 10, locker_service: LockerService = Depends(get_locker_service)):
  
    result = locker_service.get_unlocked(skip, limit)
    return result.value
    
    
@app.get("/lockers/locked/{phone_no}", response_model=list[schemas.LockerOut])
def read_lockers(phone_no:str, skip: int = 0, limit: int = 10, locker_service: LockerService = Depends(get_locker_service)):
  
    result = locker_service.get_locked_specific_user(phone_no,skip, limit)
    return result.value

@app.get("/lockers/{locker_id}", response_model=schemas.LockerOut)
def read_locker(locker_id: int,locker_service: LockerService = Depends(get_locker_service)):

    result = locker_service.get_locker(locker_id)

    if result.is_failure:
        raise HTTPException(status_code=404, detail=result.error)

    return result.value

@app.delete("/lockers/{locker_id}", response_model=schemas.LockerOut)
def delete_locker(locker_id: int, locker_service: LockerService = Depends(get_locker_service)):

    result = locker_service.delete_locker(locker_id)

    if result.is_failure:
        raise HTTPException(status_code=404, detail=result.error)

    return result.value
