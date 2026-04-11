"""Database service for CRUD operations"""
import json
import logging
import os
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from models import Base, UserProfile, User

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations"""
    
    def __init__(self, db_url: str = None):
        # Use provided URL, environment variable, or default to SQLite
        if db_url is None:
            db_url = os.getenv("DATABASE_URL", "sqlite:///./skill_bridge.db")
        
        # SQLAlchemy requires postgresql:// not postgres://
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        
        # Configure engine based on database type
        if db_url.startswith("postgresql"):
            self.engine = create_engine(db_url, pool_pre_ping=True)
        else:
            self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    # ---------- User operations ----------
    def create_user(self, email: str, hashed_password: str, name: Optional[str] = None) -> User:
        """Create a new user"""
        db = self.get_session()
        try:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                raise ValueError("User already exists")
            user = User(email=email, hashed_password=hashed_password, name=name)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()

    def get_user_by_email(self, email: str) -> Optional[User]:
        db = self.get_session()
        try:
            return db.query(User).filter(User.email == email).first()
        finally:
            db.close()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        db = self.get_session()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()
    
    def create_profile(self, name: str, target_role: str, skills: List[str], email: Optional[str] = None, phone: Optional[str] = None, location: Optional[str] = None, socials: Optional[dict] = None, experience: Optional[List[dict]] = None, projects: Optional[List[dict]] = None, education: Optional[List[dict]] = None, user_id: Optional[str] = None, resume_path: Optional[str] = None, resume_text: Optional[str] = None, resume_last_updated=None) -> UserProfile:
        """Create a new user profile"""
        db = self.get_session()
        try:
            profile = UserProfile(
                name=name,
                email=email,
                phone=phone,
                location=location,
                socials=json.dumps(socials) if socials else None,
                target_role=target_role,
                skills=json.dumps(skills),
                experience=json.dumps(experience) if experience else None,
                projects=json.dumps(projects) if projects else None,
                education=json.dumps(education) if education else None,
                user_id=user_id,
                resume_path=resume_path,
                resume_text=resume_text,
                resume_last_updated=resume_last_updated
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            return self.deserialize_profile(profile)
        finally:
            db.close()
    
    def get_profile(self, profile_id: str) -> Optional[UserProfile]:
        """Get profile by ID"""
        db = self.get_session()
        try:
            profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
            return self.deserialize_profile(profile)
        finally:
            db.close()
    
    def update_profile(self, profile_id: str, **kwargs) -> Optional[UserProfile]:
        """Update profile fields"""
        db = self.get_session()
        try:
            profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
            if not profile:
                return None
            
            # Handle skills separately (JSON serialization)
            if "skills" in kwargs:
                kwargs["skills"] = json.dumps(kwargs["skills"])
            for key in ["socials", "experience", "projects", "education"]:
                if key in kwargs and kwargs[key] is not None:
                    kwargs[key] = json.dumps(kwargs[key])
            
            for key, value in kwargs.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            db.commit()
            db.refresh(profile)
            # Deserialize JSON fields before returning
            return self.deserialize_profile(profile)
        finally:
            db.close()
    
    def get_profiles_by_role(self, role: str) -> List[UserProfile]:
        """Get all profiles for a specific role"""
        db = self.get_session()
        try:
            profiles = db.query(UserProfile).filter(UserProfile.target_role == role).all()
            # Parse JSON strings back to lists
            for profile in profiles:
                if isinstance(profile.skills, str):
                    try:
                        profile.skills = json.loads(profile.skills)
                    except (json.JSONDecodeError, TypeError):
                        profile.skills = []
            return profiles
        finally:
            db.close()
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile"""
        db = self.get_session()
        try:
            profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
            if not profile:
                return False
            db.delete(profile)
            db.commit()
            return True
        finally:
            db.close()
    
    def get_all_profiles(self, user_id: Optional[str] = None) -> List[UserProfile]:
        """Get all profiles (optionally for a user)"""
        db = self.get_session()
        try:
            query = db.query(UserProfile)
            if user_id:
                query = query.filter(UserProfile.user_id == user_id)
            profiles = query.all()
            return [self.deserialize_profile(p) for p in profiles]
        finally:
            db.close()

    def deserialize_profile(self, profile: Optional[UserProfile]) -> Optional[UserProfile]:
        if not profile:
            return None
        if isinstance(profile.skills, str):
            try:
                profile.skills = json.loads(profile.skills)
            except (json.JSONDecodeError, TypeError):
                profile.skills = []
        for key in ["socials", "experience", "projects", "education", "manual_overrides"]:
            val = getattr(profile, key, None)
            if isinstance(val, str):
                try:
                    setattr(profile, key, json.loads(val))
                except (json.JSONDecodeError, TypeError):
                    setattr(profile, key, None)
        return profile
