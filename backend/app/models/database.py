from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

from app.config import settings

# Database setup
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database Models
class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(Text)  # JSON string of skills
    preferred_skills = Column(Text)  # JSON string of skills
    qualifications = Column(Text)
    experience_required = Column(String)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    evaluations = relationship("Evaluation", back_populates="job")


class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    extracted_text = Column(Text)
    skills = Column(Text)  # JSON string of extracted skills
    experience = Column(Text)  # JSON string of experience
    education = Column(Text)  # JSON string of education
    projects = Column(Text)  # JSON string of projects
    certifications = Column(Text)  # JSON string of certifications
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    evaluations = relationship("Evaluation", back_populates="resume")


class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    # Scores
    relevance_score = Column(Float, nullable=False)  # 0-100
    hard_match_score = Column(Float, nullable=False)
    semantic_match_score = Column(Float, nullable=False)
    
    # Analysis Results
    matched_skills = Column(Text)  # JSON string
    missing_skills = Column(Text)  # JSON string
    matched_qualifications = Column(Text)  # JSON string
    missing_qualifications = Column(Text)  # JSON string
    
    # Verdict
    suitability = Column(String, nullable=False)  # High/Medium/Low
    feedback = Column(Text)  # Personalized feedback for candidate
    
    # Metadata
    evaluated_at = Column(DateTime, default=datetime.utcnow)
    evaluation_time_seconds = Column(Float)
    
    # Relationships
    job = relationship("Job", back_populates="evaluations")
    resume = relationship("Resume", back_populates="evaluations")


# Create all tables
Base.metadata.create_all(bind=engine)