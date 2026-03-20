"""Main FastAPI application"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST, before any other imports
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import profiles, analysis, jobs, auth
from models import Base
from services.database_service import DatabaseService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title="Skill-Bridge Career Navigator API",
    description="API for analyzing skill gaps and generating learning roadmaps",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db_service = DatabaseService()

# Include routers
app.include_router(profiles.router)
app.include_router(analysis.router)
app.include_router(jobs.router)
app.include_router(auth.router)

# Serve uploaded resumes
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Skill-Bridge Career Navigator API",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Skill-Bridge Career Navigator API"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
