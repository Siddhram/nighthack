from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

Base = declarative_base()


class JobDescriptionModel(Base):
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_title = Column(String(200), nullable=False, index=True)
    company_name = Column(String(200), nullable=False, index=True)
    location = Column(String(50), nullable=False, index=True)  # Hyderabad, Bangalore, etc.
    experience_required = Column(String(100), nullable=False)
    must_have_skills = Column(JSON, nullable=False)  # List[str]
    good_to_have_skills = Column(JSON, nullable=False)  # List[str]
    qualifications = Column(JSON, nullable=False)  # List[str]
    job_description = Column(Text, nullable=False)
    salary_range = Column(String(100))
    uploaded_by = Column(String(100), nullable=False)  # Placement team member
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    resume_analyses = relationship("RelevanceAnalysisModel", back_populates="job_description")


class StudentResumeModel(Base):
    __tablename__ = "student_resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(200), nullable=False, index=True)
    email = Column(String(200), index=True)
    phone = Column(String(20))
    current_location = Column(String(100))
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    
    # Extracted information from resume parsing
    extracted_skills = Column(JSON, default=[])  # List[str]
    work_experience = Column(JSON, default=[])  # List[Dict]
    education = Column(JSON, default=[])  # List[Dict]
    projects = Column(JSON, default=[])  # List[Dict]
    certifications = Column(JSON, default=[])  # List[str]
    total_experience_years = Column(Float, default=0.0, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_processed = Column(Boolean, default=False, index=True)
    
    # Relationships
    resume_analyses = relationship("RelevanceAnalysisModel", back_populates="student_resume")


class RelevanceAnalysisModel(Base):
    __tablename__ = "relevance_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("student_resumes.id"), nullable=False, index=True)
    
    # Hard Match Results
    matched_must_have_skills = Column(JSON, default=[])  # List[str]
    matched_good_to_have_skills = Column(JSON, default=[])  # List[str]
    missing_must_have_skills = Column(JSON, default=[])  # List[str]
    missing_good_to_have_skills = Column(JSON, default=[])  # List[str]
    qualification_match = Column(Boolean, default=False)
    experience_match = Column(Boolean, default=False)
    hard_match_score = Column(Float, default=0.0, index=True)  # 0-50
    
    # Soft Match Results (Semantic Analysis)
    semantic_similarity_score = Column(Float, default=0.0)  # 0-50
    role_alignment_score = Column(Float, default=0.0)
    project_relevance_score = Column(Float, default=0.0)
    overall_semantic_score = Column(Float, default=0.0)  # 0-50
    
    # Final Results
    relevance_score = Column(Float, nullable=False, index=True)  # 0-100
    fit_verdict = Column(String(10), nullable=False, index=True)  # High/Medium/Low
    missing_elements = Column(JSON, default=[])  # List[str] - what's missing
    improvement_suggestions = Column(JSON, default=[])  # List[str] - personalized feedback
    
    # Analysis metadata
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    analyzed_by = Column(String(100), default="AI System")
    
    # Relationships
    job_description = relationship("JobDescriptionModel", back_populates="resume_analyses")
    student_resume = relationship("StudentResumeModel", back_populates="resume_analyses")


class PlacementTeamModel(Base):
    __tablename__ = "placement_team"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    location = Column(String(50), nullable=False)  # Hyderabad, Bangalore, etc.
    role = Column(String(100), default="Placement Coordinator")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SystemLogModel(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # "resume_upload", "analysis_complete", etc.
    entity_type = Column(String(50), nullable=False)  # "job", "resume", "analysis"
    entity_id = Column(Integer, nullable=False)
    details = Column(JSON)  # Additional context
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user = Column(String(100))  # Who performed the action