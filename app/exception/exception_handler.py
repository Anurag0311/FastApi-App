from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from utils.helpers import response_format_failure


#Handler for RequestValidationError
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        errors.append(err.get('msg').replace("Value error, ", ""))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_format_failure(message= " & ".join(errors))
    )


# Handler for ValueError
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": str(exc)}
    )



# Handle database errors
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    print(request.state)
    if hasattr(request.state, "db_session"):
        request.state.db_session.rollback()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"},
    )

# Handle uncaught exceptions (fallback)
async def generic_exception_handler(request: Request, exc: Exception):
    if hasattr(request.state, "db_session"):
        request.state.db_session.rollback()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Something went wrong"},
    )