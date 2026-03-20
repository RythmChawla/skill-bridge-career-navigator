from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class UserProfile(Base):
    """Database model for user profiles"""
    __tablename__ = "profiles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)
    target_role = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    socials = Column(Text, nullable=True)       # JSON dict: linkedin, github, portfolio
    skills = Column(Text, nullable=False)       # JSON list
    experience = Column(Text, nullable=True)    # JSON list of dict
    projects = Column(Text, nullable=True)      # JSON list of dict
    education = Column(Text, nullable=True)     # JSON list of dict
    resume_text = Column(Text, nullable=True)
    resume_path = Column(String(255), nullable=True)
    resume_last_updated = Column(DateTime, nullable=True)
    manual_overrides = Column(Text, nullable=True)  # JSON dict of field -> bool
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, name={self.name}, role={self.target_role})>"


class User(Base):
    """Database model for authenticated users"""
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
