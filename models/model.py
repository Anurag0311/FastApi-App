from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime,  Enum
from sqlalchemy.sql import func


Base = declarative_base()

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    published_year = Column(Integer, nullable=False)
    genre = Column(Enum('fiction', 'non-fiction', 'science', 'history', 'other'), nullable=False)
    available = Column(Boolean, default=True)
    status = Column(String(20), default='Present')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())