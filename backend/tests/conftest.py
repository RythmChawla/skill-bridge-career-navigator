"""Pytest configuration and fixtures"""
import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models import Base
from services.database_service import DatabaseService


@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db_service(test_db):
    """Create database service with test database"""
    service = DatabaseService("sqlite:///:memory:")
    return service


@pytest.fixture(scope="function")
def client():
    """Create test client"""
    return TestClient(app)
