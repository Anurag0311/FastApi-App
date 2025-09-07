from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi.exceptions import RequestValidationError

import uvicorn
import time

from crud import books
from DB.database import create_table
from DB.connection import db_dependency
from exception.exception_handler import value_error_handler, validation_error_handler, sqlalchemy_error_handler, generic_exception_handler

app = FastAPI()


start_time = time.time()

@app.get("/health")
def health(db: db_dependency):
    uptime_seconds = int(time.time() - start_time)

    # Check DB connection
    try:
        db.execute(text("SELECT 1"))
        db_status = "up"
    except Exception as e:
        db_status = f"down ({str(e)})"

    return {
        "status": "ok",
        "uptime_minutes": uptime_seconds,
        "database": db_status
    }


app.include_router(books.router, prefix="/books")


# Register exception handlers
app.add_exception_handler(ValueError, value_error_handler)

app.add_exception_handler(RequestValidationError, validation_error_handler)

app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)

app.add_exception_handler(Exception, generic_exception_handler)


if __name__ == "__main__":
    create_table()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
