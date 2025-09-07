from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from typing import Annotated
from app.logger.logging import get_logger

import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(url=DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind=engine)

# Initialize logger (global instance for this module)
logger = get_logger()


def get_db_session():
    """
    FastAPI dependency for database session.
    - Yields a session for request handlers.
    - Commits on success, rollbacks on exception, and always closes.
    - Logs important session lifecycle events.
    """
    db = SessionLocal()
    try:
        logger.debug("DB session opened.")
        yield db
        db.commit()
        logger.debug("DB session committed successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"DB session rollback due to error: {e}", exc_info=True)
        raise
    finally:
        db.close()
        logger.debug("DB session closed.")


# Dependency annotation for FastAPI routes
db_dependency = Annotated[Session, Depends(get_db_session)]