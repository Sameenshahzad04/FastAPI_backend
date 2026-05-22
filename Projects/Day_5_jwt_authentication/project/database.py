from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
from config.config import DATABASE_URL

# from this file i get engine ,session ,getdb,base




#database step
# load .env file with os
# -create engine
# -session maker
# base def 



#connect py to db
engine=create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#parent to all table in my hdb
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

