import os
from sqlalchemy import create_engine 
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker 
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST", "127.0.0.1")
db_name = os.getenv("DB_NAME")

engine = create_engine(f'mysql+pymysql://root:{db_password}@{db_host}/{db_name}', echo=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 
Base = sqlalchemy.orm.declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        print(f"An error occurred while yielding the DB session: {e}")
    except Exception as e:  
        print(f"An unexpected error occurred: {e}")
        
    finally:
        db.close()