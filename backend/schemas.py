"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


class SkillsInput(BaseModel):
    """Schema for skills input"""
    skills: List[str] = Field(..., min_items=1, description="List of skills")


class ProfileCreate(BaseModel):
    """Schema for creating a user profile"""
    name: str = Field(..., min_length=1, max_length=255)
    target_role: str = Field(..., min_length=1)
    skills: List[str] = Field(default_factory=list)
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    socials: Optional[Dict[str, str]] = None


class ProfileUpdate(BaseModel):
    """Schema for updating a user profile"""
    name: Optional[str] = None
    target_role: Optional[str] = None
    skills: Optional[List[str]] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    socials: Optional[Dict[str, str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None


class ProfileResponse(BaseModel):
    """Schema for profile response"""
    id: str
    name: str
    target_role: str
    skills: List[str]
    email: Optional[str]
    phone: Optional[str] = None
    location: Optional[str] = None
    socials: Optional[Dict[str, str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime
    resume_path: Optional[str] = None
    resume_text: Optional[str] = None
    resume_last_updated: Optional[datetime] = None
    
    @field_validator('skills', mode='before')
    @classmethod
    def parse_skills(cls, v):
        """Parse skills if it's a JSON string"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v if isinstance(v, list) else []
    
    class Config:
        from_attributes = True


class GapAnalysisRequest(BaseModel):
    """Schema for gap analysis request"""
    user_skills: List[str] = Field(default_factory=list, description="List of user skills")
    job_role: str = Field(..., min_length=1)
    user_name: str = Field(..., min_length=1)


class SkillGapResponse(BaseModel):
    """Schema for skill gap analysis response"""
    matching_skills: List[str]
    missing_skills: List[str]
    current_skills_count: int
    required_skills_count: int
    matching_skills_count: int
    proficiency: float
    ai_feedback: str
    learning_roadmap: List[Dict[str, Any]]  # Changed from List[str] to support full roadmap objects


class FeedbackResponse(BaseModel):
    """Schema for feedback response"""
    gap_analysis: SkillGapResponse
    feedback: str
    roadmap: List[dict]


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str
    detail: Optional[str] = None


# -------- Auth --------
class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -------- Job recommendation --------
class JobRecommendRequest(BaseModel):
    user_skills: List[str] = Field(default_factory=list)


class JobRecommendItem(BaseModel):
    role: str
    score: float
    matching_skills: List[str]
    missing_skills: List[str]


class JobRecommendResponse(BaseModel):
    recommendations: List[JobRecommendItem]
