"""Integration tests for API endpoints"""
import pytest
import json
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestProfileEndpoints:
    """Test profile CRUD endpoints"""
    
    def test_get_all_roles(self, client):
        """Test getting all available job roles"""
        response = client.get("/jobs/roles")
        assert response.status_code == 200
        data = response.json()
        assert "roles" in data
        assert len(data["roles"]) > 0
        assert "Backend Engineer" in data["roles"]
    
    def test_create_profile_with_skills(self, client):
        """Test creating a profile with manual skills"""
        form_data = {
            "name": "John Doe",
            "target_role": "Backend Engineer",
            "skills": "Python,SQL,Docker"
        }
        
        response = client.post("/profile/", data=form_data)
        
        # Should succeed
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["target_role"] == "Backend Engineer"
        assert "Python" in data["skills"]
        
        # Save for next test
        return data["id"]
    
    def test_create_profile_invalid_role(self, client):
        """Test creating profile with invalid role"""
        form_data = {
            "name": "Jane Doe",
            "target_role": "InvalidRole",
            "skills": "Python,SQL"
        }
        
        response = client.post("/profile/", data=form_data)
        
        # Should fail with 400 error
        assert response.status_code == 400
        assert "Invalid role" in response.json()["detail"]
    
    def test_create_profile_no_skills(self, client):
        """Test creating profile without skills"""
        form_data = {
            "name": "Bob Smith",
            "target_role": "Backend Engineer"
        }
        
        response = client.post("/profile/", data=form_data)
        
        # Should fail
        assert response.status_code == 400
        assert "skills" in response.json()["detail"].lower()


class TestAnalysisEndpoints:
    """Test skill analysis endpoints"""
    
    def test_skill_gap_analysis(self, client):
        """Test skill gap analysis endpoint"""
        payload = {
            "user_skills": ["Python", "SQL"],
            "job_role": "Backend Engineer",
            "user_name": "Test User"
        }
        
        response = client.post("/analyze/gap", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "missing_skills" in data
        assert "strong_skills" in data
        assert "proficiency" in data
        assert len(data["missing_skills"]) > 0
    
    def test_feedback_generation(self, client):
        """Test feedback generation endpoint"""
        payload = {
            "user_skills": ["Python", "SQL", "Docker"],
            "job_role": "Backend Engineer",
            "user_name": "Alice Johnson"
        }
        
        response = client.post("/analyze/feedback", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "gap_analysis" in data
        assert "feedback" in data
        assert "roadmap" in data
        assert isinstance(data["feedback"], str)
        assert len(data["roadmap"]) > 0
    
    def test_feedback_invalid_role(self, client):
        """Test feedback with invalid role"""
        payload = {
            "user_skills": ["Python"],
            "job_role": "UnknownRole",
            "user_name": "Test"
        }
        
        response = client.post("/analyze/feedback", json=payload)
        
        assert response.status_code == 400
