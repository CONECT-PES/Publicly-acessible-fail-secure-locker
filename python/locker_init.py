from sqlalchemy.orm import Session
from models import Locker 
from database import engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

def populate_default_lockers(db: Session):
    """
    Populates the database with 10 default lockers.
    
    Args:
        db (Session): Database session.
    """
    default_lockers = [
        Locker(phone="NA", status="available") for _ in range(8)
    ]
    
   
    
    db.add_all(default_lockers)
    db.commit()
    print("8 lockers added with default values.")


if __name__ == "__main__":
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    populate_default_lockers(db)
    db.close()
