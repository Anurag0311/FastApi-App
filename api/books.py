from fastapi import APIRouter, status, Query
from fastapi.responses import JSONResponse
from typing import Optional

import traceback

from DB.connection import db_dependency
from schema.request_schema import BookSchema, BookUpdateSchema
from models.model import Book
from utils.helpers import (
    find_by_title_author,
    response_format_success,
    response_format_failure,
)
from logger.logging import get_logger

# Initialize router for book-related endpoints
router = APIRouter()

# Application logger
logger = get_logger()


@router.post("")
async def add_book(book: BookSchema, session: db_dependency):
    """
    Create a new book record.

    Parameters
    ----------
    book : BookSchema
        Pydantic schema containing new book details.
    session : db_dependency
        Database session dependency.

    Returns
    -------
    JSONResponse
        - 201 Created if successful.
        - 409 Conflict if title + author already exists.
    """
    # Check for duplicates (title + author)
    if find_by_title_author(book.title, book.author, session):
        logger.warning(
            f"Book already exists: title='{book.title}', author='{book.author}'"
        )
        return JSONResponse(
            content=response_format_failure("Title and Author already present"),
            status_code=status.HTTP_409_CONFLICT,
        )

    # Add new book to session (commit handled by dependency)
    session.add(Book(**book.model_dump()))

    logger.info(
        f"Book created successfully: title='{book.title}', author='{book.author}'"
    )
    return JSONResponse(
        content=response_format_success("Sucessfully created"),
        status_code=status.HTTP_201_CREATED,
    )


@router.get("")
async def get_book(
    session: db_dependency,
    author: Optional[str] = None,
    genre: Optional[str] = None,
    available: Optional[bool] = None,
    start: Optional[int] = Query(None, ge=0, description="Starting index (offset)"),
    limit: Optional[int] = Query(
        None, ge=1, le=100, description="Number of items to fetch"
    ),
):
    """
    Retrieve a list of books with optional filters and pagination.

    Parameters
    ----------
    session : db_dependency
        Database session.
    author : str, optional
        Filter by author.
    genre : str, optional
        Filter by genre.
    available : bool, optional
        Filter by availability.
    start : int, optional
        Pagination offset (>= 0).
    limit : int, optional
        Number of items to fetch (1–100).

    Returns
    -------
    dict
        Success response with books and optional pagination metadata.
    """
    query = session.query(Book)

    # Apply filters if provided
    if author is not None:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if genre is not None:
        query = query.filter(Book.genre == genre)
    if available is not None:
        query = query.filter(Book.available == available)

    # Exclude soft-deleted (terminated) books
    query = query.filter(Book.status != "Terminated")

    total_items = query.count()

    # Apply pagination only if both start and limit are set
    if start is not None and limit is not None:
        query = query.offset(start).limit(limit)

    results = query.all()

    # Convert ORM objects into serializable dictionaries
    items = [
        {
            "id": row.id,
            "title": row.title,
            "author": row.author,
            "published_year": row.published_year,
            "genre": row.genre,
            "available": row.available,
        }
        for row in results
    ]

    # Paginated vs. full response payload
    if start is not None and limit is not None:
        payload = {
            "data": items,
            "pagination": {
                "start": start,
                "limit": limit,
                "total_items": total_items,
            },
        }
        logger.info(
            f"Fetched {len(items)}/{total_items} books "
            f"(filters: author={author}, genre={genre}, available={available})"
        )
    else:
        payload = {"items": items}
        logger.info(
            f"Fetched {len(items)}/{total_items} books "
            f"(filters: author={author}, genre={genre}, available={available}, "
            f"start={start}, limit={limit})"
        )

    return response_format_success(message="Successfully Fetched", data=payload)


@router.get("/{id}")
async def get_book_by_id(id: int, session: db_dependency):
    """
    Retrieve a book by its ID.

    Parameters
    ----------
    id : int
        Book ID.
    session : db_dependency
        Database session.

    Returns
    -------
    dict or JSONResponse
        - 200 Success with book details.
        - 404 Not Found if ID does not exist.
    """
    data = session.query(Book).filter(Book.id == id, Book.status != "Terminated").first()

    if not data:
        logger.warning(f"Book not found (id={id})")
        return JSONResponse(
            content=response_format_failure("id not found"),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    response = {
        "title": data.title,
        "author": data.author,
        "published_year": data.published_year,
        "genre": data.genre,
        "available": data.available,
    }
    logger.info(f"Fetched book details successfully (id={id})")
    return response_format_success(message="Successfully Fetched", data=response)


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_book(id: int, book_data: BookUpdateSchema, session: db_dependency):
    """
    Update an existing book record.

    Parameters
    ----------
    id : int
        Book ID to update.
    book_data : BookUpdateSchema
        Partial update fields (only provided ones are updated).
    session : db_dependency
        Database session.

    Returns
    -------
    dict or JSONResponse
        - 200 Success with updated ID.
        - 200 with failure message if no fields provided.
        - 404 Not Found if ID does not exist or is terminated.
    """
    # Only update if book exists and not terminated
    book = (
        session.query(Book)
        .filter(Book.id == id, Book.status != "Terminated")
        .first()
    )

    if not book:
        logger.warning(f"Book not found for update (id={id})")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response_format_failure(message="Book with provided ID Not Found"),
        )

    updates = book_data.model_dump(exclude_unset=True)
    if not updates:
        logger.info(f"No updates provided for book (id={id})")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_format_failure("No changes provided", data={"id": id}),
        )

    # Apply changes to the ORM object
    for attr, value in updates.items():
        if hasattr(book, attr):
            setattr(book, attr, value)

    # Re-add to session (not strictly needed, but safe)
    session.add(book)

    logger.info(f"Book updated successfully (id={id}, updates={updates})")
    return response_format_success("Successfully Updated", data={"id": id})


@router.delete("/{id}")
async def delete_book(id: int, session: db_dependency):
    """
    Soft-delete a book by marking status as 'Terminated'.

    Parameters
    ----------
    id : int
        Book ID to delete.
    session : db_dependency
        Database session.

    Returns
    -------
    JSONResponse
        - 200 Success if deleted or already terminated.
        - 404 Not Found if ID does not exist.
    """
    data = session.query(Book).filter(Book.id == id).first()

    if not data:
        logger.warning(f"Book not found for delete (id={id})")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response_format_success(message="Book with provided ID Not Found"),
        )

    if data.status == "Terminated":
        logger.info(f"Book already terminated (id={id})")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_format_success(message="Book is already terminated"),
        )

    # Soft-delete by setting status instead of removing row
    data.status = "Terminated"

    logger.info(f"Book terminated successfully (id={id})")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_format_success(message="Successfully Deleted"),
    )
