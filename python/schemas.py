from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone

class LockerBase(BaseModel): 
    phone: str="NA"
    password: str 
    

class LockerCreate(LockerBase):
    unlock_time: Optional[datetime]
    pass 

class LockerUpdate(LockerBase):
    
    pass

class LockerOut(LockerBase): 
    id: int
    status:str
    model_config = ConfigDict(from_attributes=True)
    
