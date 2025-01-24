from sqlalchemy.orm import Session
from locker_repository import delete_locker_function,get_locker_function,get_unlocked_function, update_locker_function, get_locked_function,get_locked_specific
from schemas import LockerCreate, LockerUpdate
from models import Locker
from typing import List, Optional
from result import Result

class LockerService:
    def __init__(self, db: Session):
        self.db = db
        
    def update_locker(self, locker_id: int, locker_data: LockerUpdate) -> Result[Locker]:
        return update_locker_function(self.db, locker_id, locker_data)

    def get_unlocked(self, skip: int = 0, limit: int = 10) -> Result[List[Locker]]:
        return get_unlocked_function(self.db, skip, limit)
        
    def get_locked(self, skip: int = 0, limit: int = 10) -> Result[Optional[Locker]]:
        return get_locked_function(self.db,skip, limit)
    
    def get_locked_specific_user(self, phone_no:str, skip: int = 0, limit: int = 10) -> Result[Optional[Locker]]:
        return get_locked_specific(self.db,phone_no,skip, limit)
    
    def get_locker(self, locker_id: int) -> Result[Optional[Locker]]:
        return get_locker_function(self.db, locker_id)

    def delete_locker(self, locker_id: int) -> Result[Optional[Locker]]:
        return delete_locker_function(self.db, locker_id)
        
    
