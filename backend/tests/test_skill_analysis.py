"""Tests for skill analysis service"""
import pytest
from services.skill_analysis import SkillAnalysisService


@pytest.fixture
def skill_service():
    """Create skill analysis service"""
    return SkillAnalysisService()


class TestSkillGapAnalysis:
    """Test skill gap analysis functionality"""
    
    def test_gap_analysis_happy_path(self, skill_service):
        """Test happy path: valid input produces correct gap analysis"""
        user_skills = ["Python", "SQL", "Docker"]
        job_skills = ["Python", "SQL", "Docker", "Kubernetes", "AWS"]
        
        result = skill_service.analyze_gap(user_skills, job_skills)
        
        # Should have 3 strong skills
        assert len(result["strong_skills"]) == 3
        # Should have 2 missing skills
        assert len(result["missing_skills"]) == 2
        # Proficiency should be 60%
        assert result["proficiency"] == 60.0
    
    def test_gap_analysis_no_matching_skills(self, skill_service):
        """Test edge case: no matching skills between user and job"""
        user_skills = ["Ruby", "JavaScript"]
        job_skills = ["Python", "SQL", "Docker"]
        
        result = skill_service.analyze_gap(user_skills, job_skills)
        
        # Should have 0 strong skills
        assert len(result["strong_skills"]) == 0
        # Should have 3 missing skills (all job skills)
        assert len(result["missing_skills"]) == 3
        # Proficiency should be 0%
        assert result["proficiency"] == 0.0
    
    def test_gap_analysis_all_skills_match(self, skill_service):
        """Test edge case: all user skills match job skills"""
        skills = ["Python", "SQL", "Docker"]
        user_skills = skills.copy()
        job_skills = skills.copy()
        
        result = skill_service.analyze_gap(user_skills, job_skills)
        
        # Should have 3 strong skills
        assert len(result["strong_skills"]) == 3
        # Should have 0 missing skills
        assert len(result["missing_skills"]) == 0
        # Proficiency should be 100%
        assert result["proficiency"] == 100.0
    
    def test_gap_analysis_case_insensitive(self, skill_service):
        """Test that skill matching is case-insensitive"""
        user_skills = ["PYTHON", "sql"]
        job_skills = ["Python", "SQL"]
        
        result = skill_service.analyze_gap(user_skills, job_skills)
        
        # Should recognize case-insensitive matches
        assert len(result["strong_skills"]) == 2
        assert len(result["missing_skills"]) == 0


class TestFeedbackGeneration:
    """Test feedback generation with fallback"""
    
    def test_feedback_fallback_high_proficiency(self, skill_service):
        """Test fallback feedback for high proficiency"""
        user_name = "Alice"
        job_role = "Backend Engineer"
        analysis = {
            "missing_skills": ["Docker", "Kubernetes"],
            "strong_skills": ["Python", "SQL"],
            "proficiency": 85.0
        }
        
        feedback = skill_service.generate_feedback(user_name, job_role, analysis)
        
        assert isinstance(feedback, str)
        assert len(feedback) > 0
        assert "Alice" in feedback or "you" in feedback.lower()
    
    def test_feedback_fallback_low_proficiency(self, skill_service):
        """Test fallback feedback for low proficiency"""
        user_name = "Bob"
        job_role = "Data Scientist"
        analysis = {
            "missing_skills": ["ML", "Statistics", "Pandas"],
            "strong_skills": ["Python"],
            "proficiency": 25.0
        }
        
        feedback = skill_service.generate_feedback(user_name, job_role, analysis)
        
        assert isinstance(feedback, str)
        assert len(feedback) > 0


class TestRoadmapGeneration:
    """Test learning roadmap generation"""
    
    def test_roadmap_generation_fallback(self, skill_service):
        """Test roadmap generation with fallback"""
        missing_skills = ["Docker", "Kubernetes", "AWS"]
        
        roadmap = skill_service.generate_roadmap(missing_skills)
        
        # Should have 3 steps
        assert len(roadmap) == 3
        
        # Each step should have required fields
        for i, step in enumerate(roadmap):
            assert "step" in step
            assert step["step"] == i + 1
            assert "title" in step
            assert "description" in step
            assert len(step["description"]) > 0
    
    def test_roadmap_generation_empty_skills(self, skill_service):
        """Test roadmap generation with no missing skills"""
        missing_skills = []
        
        roadmap = skill_service.generate_roadmap(missing_skills)
        
        # Should still return a roadmap
        assert len(roadmap) >= 1
        assert roadmap[0]["step"] == 1
