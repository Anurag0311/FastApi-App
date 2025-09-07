from fastapi import APIRouter, status, Query
from fastapi.responses import JSONResponse
from DB.connection import db_dependency
from typing import Optional

import traceback

from schema.request_schema import BookSchema, BookUpdateSchema
from models.model import Book
from utils.helpers import find_by_title_author, response_format_success, response_format_failure

router = APIRouter()


@router.post("/")
async def add_book(book:BookSchema, session:db_dependency):

    if find_by_title_author(book.title, book.author, session):
        return JSONResponse(content=response_format_failure("Title and Author already present"), status_code=status.HTTP_409_CONFLICT)

    with session.begin():
        session.add(Book(**book.model_dump()))

    return JSONResponse(content=response_format_success("Sucessfully created"), status_code=status.HTTP_201_CREATED)



@router.get("/")
async def get_book(
    session: db_dependency,
    author: Optional[str] = None,
    genre: Optional[str] = None,
    available: Optional[bool] = None,
    start: Optional[int] = Query(None, ge=0, description="Starting index (offset)"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Number of items to fetch"),
):
    query = session.query(Book)

    if author is not None:
        query = query.filter(Book.author == author)

    if genre is not None:
        query = query.filter(Book.genre == genre)

    if available is not None:
        query = query.filter(Book.available == available)

    query = query.filter(Book.status != "Terminated")

    total_items = query.count()

    if start is not None and limit is not None:
        query = query.offset(start).limit(limit)

    results = query.all()

    items = [
        {
            "title": row.title,
            "author": row.author,
            "published_year": row.published_year,
            "genre": row.genre,
            "available": row.available,
        }
        for row in results
    ]

    if start is not None and limit is not None:
        payload = {
            "data": items,
            "pagination": {
                "start": start,
                "limit": limit,
                "total_items": total_items
            },
        }
    else:
        payload = {"items": items}

    return response_format_success(message="Successfully Fetched", data=payload)



@router.get("/{id}")
async def get_book_by_id(id : int, session : db_dependency):

    data = session.query(Book).filter(Book.id == id).first()
    
    if not data:
        return JSONResponse(content=response_format_failure("id not found"), status_code=status.HTTP_404_NOT_FOUND)
    
    response = {
        "title": data.title,
        "author": data.author,
        "published_year": data.published_year,
        "genre": data.genre,
        "available": data.available
    }

    return response_format_success(message="Successfully Fetched", data=response)



@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_book(id: int, book_data: BookUpdateSchema, session: db_dependency):
    
    book = session.query(Book).filter(
        Book.id == id,
        Book.status != "Terminated"
    ).first()

    if not book:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response_format_success(message="Book with provided ID Not Found"),
        )

    updates = book_data.model_dump(exclude_unset=True)
    if not updates:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_format_success("No changes provided", data={"id": id}),
        )

    # transaction context ensures rollback on error
    with session.begin():
        for attr, value in updates.items():
            if hasattr(book, attr):
                setattr(book, attr, value)

        session.add(book)  # safe, will be rolled back if exception occurs

    # refresh after transaction is committed
    session.refresh(book)

    return response_format_success("Successfully Updated", data={"id": id})



@router.delete("/{id}")
async def delete_book(id: int, session: db_dependency):
    data = session.query(Book).filter(Book.id == id).first()

    if not data:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response_format_success(message="Book with provided ID Not Found"),
        )

    if data.status == "Terminated":
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_format_success(message="Book is already terminated"),
        )

    # transaction context ensures rollback if anything inside fails
    with session.begin():
        data.status = "Terminated"

    return response_format_success("Successfully Deleted")