from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime


# Job Models
class JobBase(BaseModel):
    title: str
    company: str
    description: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    qualifications: str = ""
    experience_required: str = ""
    location: str = ""


class JobCreate(JobBase):
    pass


class Job(JobBase):
    id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


# Resume Models
class ResumeBase(BaseModel):
    candidate_name: str
    email: Optional[str] = None
    phone: Optional[str] = None


class ResumeCreate(ResumeBase):
    filename: str
    file_path: str


class Resume(ResumeBase):
    id: int
    filename: str
    file_path: str
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    certifications: List[str] = []
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# Evaluation Models
class EvaluationBase(BaseModel):
    job_id: int
    resume_id: int


class EvaluationResult(BaseModel):
    relevance_score: float  # 0-100
    hard_match_score: float
    semantic_match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    matched_qualifications: List[str]
    missing_qualifications: List[str]
    suitability: str  # High/Medium/Low
    feedback: str


class Evaluation(EvaluationResult):
    id: int
    job_id: int
    resume_id: int
    evaluated_at: datetime
    evaluation_time_seconds: Optional[float] = None
    job: Optional[Job] = None
    resume: Optional[Resume] = None
    
    class Config:
        from_attributes = True


# Response Models
class JobResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Job] = None


class ResumeResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Resume] = None


class EvaluationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[EvaluationResult] = None


class JobListResponse(BaseModel):
    success: bool
    message: str
    data: List[Job] = []
    total: int = 0


class ResumeListResponse(BaseModel):
    success: bool
    message: str
    data: List[Resume] = []
    total: int = 0


class EvaluationListResponse(BaseModel):
    success: bool
    message: str
    data: List[Evaluation] = []
    total: int = 0


# Upload Models
class FileUploadResponse(BaseModel):
    success: bool
    message: str
    filename: Optional[str] = None
    file_path: Optional[str] = None


# Dashboard Models
class DashboardStats(BaseModel):
    total_jobs: int
    total_resumes: int
    total_evaluations: int
    high_suitability_count: int
    medium_suitability_count: int
    low_suitability_count: int
    recent_evaluations: List[Evaluation] = []