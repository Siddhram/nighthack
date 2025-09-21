from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums for Innomatics Research Labs system
class FitVerdict(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium" 
    LOW = "Low"


class Location(str, Enum):
    HYDERABAD = "Hyderabad"
    BANGALORE = "Bangalore"
    PUNE = "Pune"
    DELHI_NCR = "Delhi NCR"


# Job Description Models for Innomatics
class JobDescriptionBase(BaseModel):
    role_title: str
    company_name: str
    location: Location
    experience_required: str  # e.g., "2-5 years"
    must_have_skills: List[str]  # Critical skills
    good_to_have_skills: List[str]  # Nice to have skills
    qualifications: List[str]  # Education, certifications
    job_description: str  # Full JD text
    salary_range: Optional[str] = None


class JobDescriptionCreate(JobDescriptionBase):
    uploaded_by: str  # Placement team member name


class JobDescription(JobDescriptionBase):
    id: int
    created_at: datetime
    uploaded_by: str
    is_active: bool = True
    
    class Config:
        from_attributes = True


# Student Resume Models
class StudentResumeBase(BaseModel):
    student_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    current_location: Optional[str] = None


class StudentResumeCreate(StudentResumeBase):
    filename: str
    file_path: str


class StudentResume(StudentResumeBase):
    id: int
    filename: str
    file_path: str
    extracted_skills: List[str] = []
    work_experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    certifications: List[str] = []
    total_experience_years: float = 0.0
    created_at: datetime
    
    class Config:
        from_attributes = True


# Resume Relevance Analysis Models
class RelevanceAnalysisBase(BaseModel):
    job_id: int
    resume_id: int


class HardMatchResult(BaseModel):
    matched_must_have_skills: List[str]
    matched_good_to_have_skills: List[str]
    missing_must_have_skills: List[str]
    missing_good_to_have_skills: List[str]
    qualification_match: bool
    experience_match: bool
    hard_match_score: float  # 0-50


class SoftMatchResult(BaseModel):
    semantic_similarity_score: float  # 0-50
    role_alignment_score: float
    project_relevance_score: float
    overall_semantic_score: float  # 0-50


class RelevanceAnalysisResult(BaseModel):
    hard_match: HardMatchResult
    soft_match: SoftMatchResult
    relevance_score: float  # 0-100 (hard_match + soft_match)
    fit_verdict: FitVerdict
    missing_elements: List[str]  # Skills, certs, projects to improve
    improvement_suggestions: List[str]  # Personalized feedback


class RelevanceAnalysis(RelevanceAnalysisBase):
    id: int
    job_description: JobDescription
    student_resume: StudentResume
    analysis_result: RelevanceAnalysisResult
    analyzed_at: datetime
    analyzed_by: str  # System or evaluator name
    
    class Config:
        from_attributes = True


# Dashboard and Search Models
class PlacementDashboardStats(BaseModel):
    total_jobs_this_week: int
    total_resumes_analyzed: int
    high_fit_candidates: int
    medium_fit_candidates: int
    low_fit_candidates: int
    avg_relevance_score: float
    by_location: Dict[str, int]


class ResumeSearchFilters(BaseModel):
    job_id: Optional[int] = None
    fit_verdict: Optional[FitVerdict] = None
    min_relevance_score: Optional[float] = None
    max_relevance_score: Optional[float] = None
    location: Optional[Location] = None
    skills: Optional[List[str]] = None


class SearchResults(BaseModel):
    analyses: List[RelevanceAnalysis]
    total_count: int
    avg_score: float
    filters_applied: ResumeSearchFilters


# Response Models
class JobDescriptionResponse(BaseModel):
    job: JobDescription


class JobDescriptionListResponse(BaseModel):
    jobs: List[JobDescription]
    total: int


class ResumeAnalysisResponse(BaseModel):
    analysis: RelevanceAnalysis


class BulkAnalysisRequest(BaseModel):
    job_id: int
    resume_ids: List[int]


class BulkAnalysisResponse(BaseModel):
    analyses: List[RelevanceAnalysis]
    total_processed: int
    high_fit_count: int
    medium_fit_count: int
    low_fit_count: int