from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from utils.helpers import response_format_failure
from logger.logging import get_logger


# Initialize application logger
logger = get_logger()



async def validation_error_handler(request: Request, exc: RequestValidationError):
    """
    Handle FastAPI validation errors (e.g., request body/query param validation failures).

    Parameters
    ----------
    request : Request
        The HTTP request that triggered the validation error.
    exc : RequestValidationError
        The validation error details raised by FastAPI/Pydantic.

    Returns
    -------
    JSONResponse
        HTTP 422 response with a standardized error format.
    """
    errors = []
    # Extract human-readable messages from validation errors
    for err in exc.errors():
        errors.append(err.get("msg").replace("Value error, ", ""))

    # Log warning with request details and error messages
    logger.warning(
        f"Validation error on {request.method} {request.url}: {errors}"
    )

    # Return 422 response with concatenated error messages
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_format_failure(message=" & ".join(errors)),
    )


async def value_error_handler(request: Request, exc: ValueError):
    """
    Handle Python built-in ValueError exceptions raised during request processing.

    Parameters
    ----------
    request : Request
        The HTTP request that caused the exception.
    exc : ValueError
        The ValueError exception instance.

    Returns
    -------
    JSONResponse
        HTTP 400 response with the error message.
    """
    # Log warning with request details and exception string
    logger.warning(
        f"ValueError on {request.method} {request.url}: {exc}"
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": str(exc)},  # Note: not using response_format_failure here
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle SQLAlchemy-related database errors.

    Parameters
    ----------
    request : Request
        The HTTP request that caused the exception.
    exc : SQLAlchemyError
        The SQLAlchemy exception instance.

    Returns
    -------
    JSONResponse
        HTTP 500 response with a generic failure message.
    """
    # Log full stack trace and request details
    logger.error(
        f"SQLAlchemyError on {request.method} {request.url}: {exc}",
        exc_info=True,  # Includes stack trace in logs
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_format_failure(message="Something went wrong"),
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unexpected/unhandled exceptions.

    Parameters
    ----------
    request : Request
        The HTTP request that caused the exception.
    exc : Exception
        The exception instance.

    Returns
    -------
    JSONResponse
        HTTP 500 response with a generic failure message.
    """
    # Log full stack trace and request details
    logger.error(
        f"Unhandled exception on {request.method} {request.url}: {exc}",
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_format_failure(message="Something went wrong"),
    )
