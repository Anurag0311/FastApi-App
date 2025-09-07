import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.DB.database import Base
from app.DB.connection import get_db_session
from app.main import app  # your FastAPI entrypoint file where router is included
from app.models.model import Book


# SQLite test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Fixture to provide a session
@pytest.fixture(scope="function")
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()  # rollback any changes after test
        session.close()


@pytest.fixture(scope="function", autouse=True)
def override_db_dependency(db_session):
    # Override get_db_session in FastAPI to use the test session
    app.dependency_overrides[get_db_session] = lambda: db_session


# Create schema once
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


# ---------- Fixtures ----------
@pytest.fixture
def sample_book(db_session):
    """Fixture to insert a book directly into DB before tests."""
    db = TestingSessionLocal()
    book = Book(
        title="Test Driven Development",
        author="Kent Beck",
        published_year=2003,
        genre="science",
        available=True
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    yield book
    db.close()


# ---------- Tests ----------
def test_add_book():
    response = client.post(
        "/books/",
        json={
            "title": "Clean Code",
            "author": "Robert Martin",
            "published_year": 2008,
            "genre": "science",
            "available": True
        },
    )
    assert response.status_code == 201
    data = response.json()
    print(data)
    assert data["status"] is True
    assert data["message"] == "Sucessfully created"


def test_add_duplicate_book(sample_book):
    response = client.post(
        "/books/",
        json={
            "title": "Test Driven Development",
            "author": "Kent Beck",
            "published_year": 2003,
            "genre": "science",
            "available": True
        },
    )
    assert response.status_code == 409
    data = response.json()
    assert data["status"] is False
    assert "Title and Author already present" in data["message"]


def test_get_books(sample_book):
    response = client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] is True
    assert "items" in data["data"] or "data" in data["data"]


def test_get_book_by_id(sample_book):
    response = client.get(f"/books/{sample_book.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] is True
    assert data["data"]["title"] == "Test Driven Development"


def test_get_book_by_invalid_id():
    response = client.get("/books/9999")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] is False


def test_update_book(sample_book):
    response = client.put(
        f"/books/{sample_book.id}",
        json={"title": "TDD Updated"}
    )
    assert response.status_code == 200
    data = response.json()
    print("DATA:",data)
    assert data["status"] is True
    assert data["message"] == "Successfully Updated"
    assert data['data'].get('id') == sample_book.id


def test_update_book_invalid_id():
    response = client.put("/books/9999", json={"title": "Does Not Exist"})
    assert response.status_code == 404
    data = response.json()
    print("DATA:",data)
    assert data["status"] is False  # careful: your API returns success=True with "Not Found"


def test_delete_book(sample_book, db_session):
    # First delete
    response = client.delete(f"/books/{sample_book.id}")
    data = response.json()
    print("First delete response:", data)
    assert response.status_code == 200
    assert data["message"] == "Successfully Deleted"

    # Second delete (should see terminated status)
    response = client.delete(f"/books/{sample_book.id}")
    data = response.json()
    print("Second delete response:", data)
    assert response.status_code == 200
    assert data["message"] == "Book is already terminated"

    # Optional: verify DB directly
    book_in_db = db_session.query(Book).filter(Book.id == sample_book.id).first()
    assert book_in_db.status.lower() == "terminated"
