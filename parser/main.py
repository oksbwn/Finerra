import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# Allow running from inside the 'parser' directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser.db.database import init_db
# from parser.core.scheduler import start_cleanup_job
from parser.api import ingestion, config, analytics, system

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Init DB, Start Scheduler
    print("Starting Parser Service...")
    init_db()
    # start_cleanup_job()
    yield
    # Shutdown
    print("Shutting down Parser Service...")

app = FastAPI(
    title="Financial Parser Microservice",
    description="A robust microservice for parsing financial transactions from SMS, Email, and Files.",
    version="1.1.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Categorized Routers
app.include_router(system.router)
app.include_router(ingestion.router)
app.include_router(config.router)
app.include_router(analytics.router)

if __name__ == "__main__":
    uvicorn.run("parser.main:app", host="0.0.0.0", port=8001, reload=True)
