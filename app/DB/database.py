from sqlalchemy import create_engine
from models.model import Base
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL =  os.getenv("DATABASE_URL")

def create_table():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)