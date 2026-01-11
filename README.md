# Family Finance Platform

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, DuckDB
- **Frontend**: Vue 3, TypeScript, Pinia, Vite

## Setup Instructions

### Backend
1.  Navigate to the `backend` directory (or root).
2.  Install dependencies:
    ```bash
    pip install fastapi uvicorn[standard] sqlalchemy duckdb duckdb-engine python-jose[cryptography] "bcrypt==4.0.1" python-multipart pydantic-settings email-validator
    ```
3.  Run the server:
    ```bash
    # Run this from the project root
    python run_backend.py
    ```
    The API will be available at `http://localhost:8000`.

### Frontend
1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies (Node.js required):
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
    The app will be available at `http://localhost:5173`.

## Architecture
- `backend/app/modules`: Contains modularized business logic (Auth, Finance).
- `frontend/src`: Vue 3 application with Clean Architecture components.
