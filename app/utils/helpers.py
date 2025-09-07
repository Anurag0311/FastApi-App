from sqlalchemy import func, exists

from models.model import Book


def response_format_success(message: str, data: dict | None = None):
    body = {"status": True, "message": message}
    if data is not None:
        body["data"] = data
    return body

def response_format_failure(message):
    return {"message": message, "status": False}


def find_by_title_author(title, author, session):
    return session.query(
        exists().where(
            func.lower(Book.title) == title.lower(),
        ).where(
            func.lower(Book.author) == author.lower()
        )
    ).scalar()


