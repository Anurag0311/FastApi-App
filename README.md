# 📘 Assignment: Book Inventory REST API (FastAPI + MySQL + Docker)

## 📌 Overview
You are required to build a **Book Inventory REST API** using **FastAPI**.  
The system should allow users to manage books in a library/inventory.  

This assignment will test your skills in:
- Python (FastAPI framework)
- REST API design
- CRUD operations
- MySQL database integration
- Docker containerization
- API documentation (Swagger/OpenAPI)

---

## 📂 Requirements

### 1. Framework
- Use **FastAPI** as the backend framework.

### 2. Database
- Use **MySQL** for persistence.

---

## 📚 Book Model

Each book should have the following fields:

| Field          | Type                                | Constraints/Default |
|----------------|-------------------------------------|---------------------|
| id             | int (auto-increment, primary key)   | Required            |
| title          | string                              | Required            |
| author         | string                              | Required            |
| published_year | int                                 | Required            |
| genre          | enum (`fiction`, `non-fiction`, `science`, `history`, `other`) | Required |
| available      | boolean                             | Default: `true`     |
| created_at     | timestamp                           | Auto-generated      |
| updated_at     | timestamp                           | Auto-generated      |

---

## 🔗 Endpoints

### Health
- **GET** `/health` → Health check with uptime & DB status

### Books
- **POST** `/books` → Add a new book  
- **GET** `/books` → List all books (with optional filters)  
- **GET** `/books/{id}` → Get details of a book by ID  
- **PUT** `/books/{id}` → Update a book’s details  
- **DELETE** `/books/{id}` → Delete a book  


---

## 🔍 Filters (for `GET /books`)
- Search by **author**
- Filter by **genre**
- Filter by **available**

---

## 📖 Documentation
- Expose **Swagger docs** at `/docs` (FastAPI default).

---

## 🚀 Deployment
- Write a **Dockerfile** for the FastAPI app.
- Use **Docker Compose** to run both:
  - FastAPI app (on port `8000`)
  - MySQL DB (on port `3306`)
