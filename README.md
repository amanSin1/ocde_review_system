<img width="980" height="358" alt="image" src="https://github.com/user-attachments/assets/15409105-b04e-46ec-9a1d-6ed50103afd9" />🧠 Collaborative Code Review System (Backend)

A production-style backend system for collaborative code reviews, designed for students and mentors.
Built with FastAPI, PostgreSQL, SQLAlchemy, JWT Authentication, and Docker.

This project focuses on real backend engineering concepts such as role-based access control, relational data modeling, optimized querying, background-ready notifications, and containerization.

🚀 Features
👤 Authentication & Authorization

User registration & login

JWT-based authentication

Role-based access:

Student

Mentor

Admin (future scope)

📄 Submissions

Students can:

Create code submissions

Edit submissions while pending

View their own submissions

Mentors/Admin can:

View all submissions

Submissions include:

Title, description, code content

Language

Status (pending, reviewed)

Tags (many-to-many)

🏷️ Tags System

Reusable tags (e.g. python, django, authentication)

Many-to-many relationship using association table

Optimized querying for filtering

📝 Reviews & Annotations

Mentors can:

Review any submission

Add overall feedback & rating

Add line-level annotations

Students can:

View all reviews for their submissions

Nested response structure:

Submission → Reviews → Annotations

🔔 Notifications

Database-backed notifications

Created automatically when:

A mentor reviews a submission

Students can:

View notifications

Mark notifications as read

⚡ Performance & Scalability

Pagination (skip, limit)

Filtering by status & language

Indexed frequently queried columns

Fixed N+1 query issues using joinedload

Database connection pooling

🧪 Testing

Pytest-based test suite

Tests include:

Auth flow

Role-based access

Submissions

Reviews

Uses isolated test database

No effect on production DB

🐳 Dockerized

Fully containerized backend

PostgreSQL + FastAPI using Docker Compose

Environment separation:

.env → local

.env.docker → container

Image published to Docker Hub



🏗️ Tech Stack
Layer	Technology
API	FastAPI
ORM	SQLAlchemy
DB	PostgreSQL
Auth	JWT
Migrations	Alembic
Rate Limiting	SlowAPI
Testing	Pytest
Containerization	Docker & Docker Compose


📂 Project Structure
code-review-system/
├── app/
│   ├── api/
│   │   └── routes/
│   ├── models/
│   ├── schemas/
│   ├── core/
│   │   ├── logger.py
│   │   └── rate_limiter.py
│   ├── database.py
│   ├── oauth2.py
│   └── main.py
├── alembic/
├── tests/
├── docker/
│   └── entrypoint.sh
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md

🔐 Environment Variables
.env (Local)
DATABASE_URL=postgresql://postgres:password@localhost:5432/code_review_db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

.env.docker (Docker)
DATABASE_URL=postgresql://postgres:password@db:5432/code_review_db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

🐳 Running with Docker
Build & Run
docker compose up --build


API will be available at:

http://localhost:8000


Docs:

http://localhost:8000/docs

📦 Docker Image

Published on Docker Hub:

docker pull amansingh3413/code-review-system

🧪 Running Tests
pytest -v


All tests run against an isolated test database.

🧠 Design Decisions (Interview Gold)

Role-based authorization at query level, not frontend

No redundant mentor–student mapping — mentors review any submission

Annotations stored separately for scalability

Explicit serialization instead of dumping ORM objects

Indexes added for high-read endpoints

Eager loading (joinedload) to prevent N+1 queries

Database-backed notifications (extensible to WebSockets later)

Local Development Setup

Clone the repository

bash   git clone https://github.com/yourusername/code-review-system.git
   cd code-review-system

Create virtual environment

bash   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Mac/Linux
   source venv/bin/activate

Install dependencies

bash   pip install -r requirements.txt

Setup PostgreSQL database

bash   # Create database
   createdb code_review_db
   
   # Or using psql
   psql -U postgres
   CREATE DATABASE code_review_db;
   \q

Configure environment variables
Create .env file in project root:

env   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/code_review_db
   SECRET_KEY=your-super-secret-key-min-32-chars-generate-with-openssl
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   PROJECT_NAME=Code Review System
   DEBUG=True
   ENVIRONMENT=development
   RATE_LIMIT_ENABLED=True
Generate a secure SECRET_KEY:
bash   openssl rand -hex 32
   # Or in Python:
   python -c "import secrets; print(secrets.token_urlsafe(32))"

Run database migrations

bash   alembic upgrade head

Start the development server

bash   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

8. **Access the application**
   - API: http://localhost:8000
   - Interactive API Docs (Swagger): http://localhost:8000/docs
   - Alternative Docs (ReDoc): http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

---

## 📚 API Documentation

### Base URL
```
1️⃣ Open Swagger UI

Once your app is running (Docker or local):

http://localhost:8000/docs


You’ll see:

List of all API endpoints

Sections like Authentication, Submissions, Reviews, Notifications, etc.

This UI is auto-generated by FastAPI.
```

### Authentication

All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>

Endpoints Overview
<img width="769" height="694" alt="image" src="https://github.com/user-attachments/assets/400bf8f0-e988-4680-a667-f55960e68990" />
<img width="784" height="646" alt="image" src="https://github.com/user-attachments/assets/c1f324f2-663a-424d-b0cf-2648fee9ff52" />


🔮 Future Enhancements

Admin dashboard

WebSocket real-time notifications

Review versioning

Code diffing

Full frontend integration

CI/CD pipeline

👨‍💻 Author

Aman Singh
Backend-focused developer
