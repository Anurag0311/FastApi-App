from sqlalchemy import create_engine
from models.model import Base
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection URL (expected in .env as DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL")


def create_table():
    """
    Create database tables defined in SQLAlchemy ORM models.

    This function:
    - Creates a new SQLAlchemy engine using the DATABASE_URL from environment variables.
    - Uses SQLAlchemy's metadata to create all tables defined in `Base`.

    Notes
    -----
    - Tables are created only if they do not already exist.
    - `Base` must be imported from your models package where all SQLAlchemy ORM classes inherit from it.
    - Typically called once at application startup to ensure schema exists.

    Raises
    ------
    sqlalchemy.exc.OperationalError
        If the database connection cannot be established.
    """
    # Initialize SQLAlchemy engine for the given database
    engine = create_engine(DATABASE_URL)

    # Create all tables defined on the declarative Base
    Base.metadata.create_all(engine)
