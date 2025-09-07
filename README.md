# 📚 Book Inventory App - Setup

A **FastAPI-based application** with a MySQL database, containerized using Docker & Docker Compose.  
This setup ensures seamless app + database deployment with persistent logs and database storage on the host machine.

---

## 🚀 Tech Stack
- **Backend**: FastAPI  
- **Database**: MySQL 8.0  
- **Containerization**: Docker & Docker Compose  
- **ORM**: SQLAlchemy + PyMySQL  

---

## 📂 Project Structure
```
.FastApi-App
├── Dockerfile
├── docker-compose.yml
├── api
├── DB
├── exception
├── models
├── schema
├── tests
├── utils
├── requirements.txt
├── main.py
└── .env
```

---

## ⚙️ Setup Instructions

### 1️⃣ Prerequisites
Make sure you have installed:
- [Docker](https://docs.docker.com/get-docker/)  
- [Docker Compose](https://docs.docker.com/compose/install/)  

---

### 2️⃣ Clone the Repository
```bash
git clone <your-repo-url>
cd <your-project-folder>
```

---

### 3️⃣ Configure Environment Variables
Update `.env` file with your settings:
```env
# Database
MYSQL_ROOT_PASSWORD=DB_PASS
MYSQL_DATABASE=DB_NAME

# Web app
DATABASE_URL=mysql+pymysql://root:DB_PASS@db:3306/DB_NAME
APPLICATION_NAME=APP_NAME

# Host paths for volumes
HOST_LOGS_PATH=DIRECTORY_ON_YOUR_PC
HOST_DB_PATH=ANOTHER_DIRECTORY_ON_YOUR_PC
```
> ⚠️ Replace host paths (`HOST_LOGS_PATH`, `HOST_DB_PATH`) according to your system.

> ⚠️ Replace (`DB_PASS`, `DB_NAME`) with your database name and password.

---

### 4️⃣ Build & Start the Application

Note: 1 ) Make sure you are in the directory where Dockerfile, docker-compose.yml and .env files are in same place.

2 ) If Docker Compose cannot find your Dockerfile, rename it from "DockerFile" to "Dockerfile". 

Run:
```bash
docker-compose up --build
```

- FastAPI app → **http://localhost:8000**  
- MySQL DB → **localhost:3306**

---

### 5️⃣ Verify Services
- **Swagger UI (API Docs)** → [http://localhost:8000/docs](http://localhost:8000/docs)  
- **ReDoc** → [http://localhost:8000/redoc](http://localhost:8000/redoc)  

---

### 6️⃣ Useful Commands
- Stop containers:
  ```bash
  docker-compose down
  ```
- Rebuild without cache:
  ```bash
  docker-compose build --no-cache
  ```
- View logs:
  ```bash
  docker-compose logs -f
  ```
- Access MySQL container:
  ```bash
  docker exec -it <db_container_name> mysql -u root -p
  ```

---

## 📌 Notes
- Logs persist at: `${HOST_LOGS_PATH}`  
- MySQL data persists at: `${HOST_DB_PATH}`  
- Containers auto-restart on failure.  

---

✅ Your **Book Inventory FastAPI app** with MySQL should now be running successfully!  
