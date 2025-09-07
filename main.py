from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi.exceptions import RequestValidationError

import uvicorn
import time

from crud import books
from DB.database import create_table
from DB.connection import db_dependency
from exception.exception_handler import (
    value_error_handler,
    validation_error_handler,
    sqlalchemy_error_handler,
    generic_exception_handler,
)

# Initialize FastAPI application instance
app = FastAPI()

# Record application start time for uptime calculation
start_time = time.time()


@app.get("/health")
def health(db: db_dependency):
    """
    Health check endpoint.

    Returns application uptime and database connectivity status.

    Parameters
    ----------
    db : db_dependency
        Database session dependency injected by FastAPI.

    Returns
    -------
    dict
        {
            "status": "ok",               # Application status
            "uptime_seconds": <int>,      # Seconds since app start (actually seconds, despite name)
            "database": "up" or "down"    # Database status string
        }

    Notes
    -----
    - The database is checked using a simple `SELECT 1` query.
    - Uptime is measured from the moment the application started.
    """
    uptime_seconds = int(time.time() - start_time)
    try:
        # Test DB connectivity
        db.execute(text("SELECT 1"))
        db_status = "up"
    except Exception as e:
        # Capture DB error and return as part of health status
        db_status = f"down ({str(e)})"

    return {
        "status": "ok",
        "uptime_seconds": uptime_seconds,
        "database": db_status,
    }


# Include Books router under /books prefix
app.include_router(books.router, prefix="/books")


# Register exception handlers with FastAPI app
# Each maps an exception type to a custom handler
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)


if __name__ == "__main__":
    """
    Entry point for running the application directly.

    - Ensures database tables are created before starting.
    - Runs the FastAPI app using Uvicorn on host 0.0.0.0:8000 with autoreload enabled.
    """
    create_table()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
