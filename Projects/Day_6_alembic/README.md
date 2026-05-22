# Backend Phase 1

## Handler and config implementation

This is a **FastAPI backend** project for managing **users**, **projects**, and **tasks**.  
The project follows **clean architecture** by separating **routes**, **handlers**, and **config**, making it maintainable, scalable, and production-ready.

Key Features:

- User registration and JWT authentication
- Project CRUD operations (Create, Read, Delete)
- Task CRUD operations within projects
- Centralized database handlers for clean SQLAlchemy queries
- Environment-based configuration using `.env`

---

## Project Structure
project/
│
├── .env # Environment variables
├── main.py # FastAPI entrypoint
├── database.py # SQLAlchemy engine, session, Base
├── config/
│ └── config.py # Loads .env variables
├── routers/ # API routes
│ ├── user_routes.py
│ ├── project_routes.py
│ └── task_routes.py
├── handlers/ # Database query logic
│ ├── user_handler.py
│ ├── project_handler.py
│ └── task_handler.py
├── models/ # SQLAlchemy models
├── schemas/ # Pydantic schemas
└── requirements.txt # Project dependencies
Installation & Setup

Clone the repository

git clone <your-repo-url>
cd backend_phase_1


Install dependencies

pip install -r requirements.txt


Run the server

uvicorn main:app --reload
API Endpoints
Users

POST /users/register – Register a new user

POST /users/login – Login and receive JWT token

Projects

POST /projects/ – Create a new project

GET /projects/ – Get all projects for the current user

GET /projects/{id} – Get a single project

DELETE /projects/{id} – Delete a project

Tasks

POST /tasks/projects/{project_id} – Create a task for a project

GET /tasks/projects/{project_id} – Get all tasks of a project

PUT /tasks/{task_id} – Update a task

DELETE /tasks/{task_id} – Delete a task
