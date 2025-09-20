from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import os
import shutil
from datetime import datetime

# Import Innomatics-specific modules
from app.models.innomatics_models import Base, JobDescriptionModel, StudentResumeModel, RelevanceAnalysisModel
from app.models.innomatics_schemas import (
    JobDescriptionCreate, JobDescription, JobDescriptionResponse,
    StudentResumeCreate, StudentResume, RelevanceAnalysisResult,
    PlacementDashboardStats, ResumeSearchFilters, SearchResults
)
from app.models.database import engine, SessionLocal
from app.services.jd_parser import InnomaticsJDParser
from app.services.innomatics_resume_analyzer import InnomaticsResumeAnalyzer
from app.services.hybrid_scoring_engine import InnomaticsHybridScoringEngine

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Innomatics Research Labs - Resume Relevance Check System",
    description="AI-powered resume evaluation system for placement teams across Hyderabad, Bangalore, Pune, and Delhi NCR",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
jd_parser = InnomaticsJDParser()
resume_analyzer = InnomaticsResumeAnalyzer()
scoring_engine = InnomaticsHybridScoringEngine()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ensure upload directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {
        "message": "Innomatics Research Labs - Resume Relevance Check System",
        "status": "Active",
        "locations": ["Hyderabad", "Bangalore", "Pune", "Delhi NCR"],
        "features": [
            "AI-powered resume analysis",
            "0-100 relevance scoring",
            "High/Medium/Low fit verdicts", 
            "Personalized improvement suggestions",
            "Placement team dashboard"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# Job Description Management
@app.post("/api/jobs", response_model=JobDescriptionResponse)
async def create_job_description(
    role_title: str = Form(...),
    company_name: str = Form(...),
    location: str = Form(...),
    experience_required: str = Form(...),
    job_description: str = Form(...),
    uploaded_by: str = Form(...),
    must_have_skills: str = Form(""),  # Comma-separated
    good_to_have_skills: str = Form(""),  # Comma-separated
    qualifications: str = Form(""),  # Comma-separated
    salary_range: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new job description for Innomatics Research Labs"""
    
    # Parse comma-separated skills
    must_have_list = [s.strip() for s in must_have_skills.split(",") if s.strip()]
    good_to_have_list = [s.strip() for s in good_to_have_skills.split(",") if s.strip()]
    qualifications_list = [q.strip() for q in qualifications.split(",") if q.strip()]
    
    # If skills not provided, use AI to extract from JD
    if not must_have_list and not good_to_have_list:
        jd_analysis = jd_parser.parse_job_description(job_description, role_title, company_name)
        must_have_list = jd_analysis.must_have_skills
        good_to_have_list = jd_analysis.good_to_have_skills
        if not qualifications_list:
            qualifications_list = jd_analysis.qualifications
    
    # Create job description in database
    db_job = JobDescriptionModel(
        role_title=role_title,
        company_name=company_name,
        location=location,
        experience_required=experience_required,
        must_have_skills=must_have_list,
        good_to_have_skills=good_to_have_list,
        qualifications=qualifications_list,
        job_description=job_description,
        salary_range=salary_range,
        uploaded_by=uploaded_by
    )
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return JobDescriptionResponse(job=db_job)

@app.get("/api/jobs", response_model=List[JobDescription])
async def get_job_descriptions(
    location: Optional[str] = None,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """Get all job descriptions with optional filtering"""
    query = db.query(JobDescriptionModel).filter(JobDescriptionModel.is_active == is_active)
    
    if location:
        query = query.filter(JobDescriptionModel.location == location)
    
    jobs = query.order_by(JobDescriptionModel.created_at.desc()).all()
    return jobs

@app.get("/api/jobs/{job_id}", response_model=JobDescriptionResponse)
async def get_job_description(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job description"""
    job = db.query(JobDescriptionModel).filter(JobDescriptionModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    return JobDescriptionResponse(job=job)

# Resume Upload and Analysis
@app.post("/api/resumes/upload")
async def upload_resume(
    file: UploadFile = File(...),
    student_name: str = Form(...),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    current_location: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload and analyze a student resume"""
    
    # Validate file type
    if not file.filename.lower().endswith(('.pdf', '.docx', '.doc')):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Analyze resume using Innomatics analyzer
        resume_analysis = resume_analyzer.analyze_resume(file_path, file.filename)
        
        # Create resume record in database
        db_resume = StudentResumeModel(
            student_name=student_name or resume_analysis.student_name,
            email=email or resume_analysis.contact_info.get('email', ''),
            phone=phone or resume_analysis.contact_info.get('phone', ''),
            current_location=current_location or resume_analysis.contact_info.get('location', ''),
            filename=file.filename,
            file_path=file_path,
            extracted_skills=resume_analysis.extracted_skills,
            work_experience=[exp.__dict__ if hasattr(exp, '__dict__') else exp for exp in resume_analysis.work_experience],
            education=[edu.__dict__ if hasattr(edu, '__dict__') else edu for edu in resume_analysis.education],
            projects=[proj.__dict__ if hasattr(proj, '__dict__') else proj for proj in resume_analysis.projects],
            certifications=resume_analysis.certifications,
            total_experience_years=resume_analysis.total_experience_years,
            is_processed=True
        )
        
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        
        return {
            "message": "Resume uploaded and analyzed successfully",
            "resume_id": db_resume.id,
            "student_name": db_resume.student_name,
            "analysis_summary": resume_analyzer.get_resume_summary(resume_analysis),
            "file_path": file_path
        }
        
    except Exception as e:
        # Clean up file if analysis failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Resume analysis failed: {str(e)}")

# Resume-Job Matching and Evaluation
@app.post("/api/evaluate/{job_id}/{resume_id}")
async def evaluate_resume_for_job(
    job_id: int,
    resume_id: int,
    db: Session = Depends(get_db)
):
    """Evaluate a resume against a specific job description"""
    
    # Get job description
    job = db.query(JobDescriptionModel).filter(JobDescriptionModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Get resume
    resume = db.query(StudentResumeModel).filter(StudentResumeModel.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    try:
        # Parse job description
        jd_analysis = jd_parser.parse_job_description(
            job.job_description,
            job.role_title,
            job.company_name
        )
        jd_analysis.must_have_skills = job.must_have_skills
        jd_analysis.good_to_have_skills = job.good_to_have_skills
        jd_analysis.qualifications = job.qualifications
        jd_analysis.experience_required = job.experience_required
        
        # Analyze resume
        resume_analysis = resume_analyzer.analyze_resume(resume.file_path, resume.filename)
        
        # Perform relevance evaluation
        relevance_result = scoring_engine.evaluate_resume_relevance(jd_analysis, resume_analysis)
        
        # Save analysis to database
        db_analysis = RelevanceAnalysisModel(
            job_id=job_id,
            resume_id=resume_id,
            matched_must_have_skills=relevance_result.hard_match.matched_must_have_skills,
            matched_good_to_have_skills=relevance_result.hard_match.matched_good_to_have_skills,
            missing_must_have_skills=relevance_result.hard_match.missing_must_have_skills,
            missing_good_to_have_skills=relevance_result.hard_match.missing_good_to_have_skills,
            qualification_match=relevance_result.hard_match.qualification_match,
            experience_match=relevance_result.hard_match.experience_match,
            hard_match_score=relevance_result.hard_match.hard_match_score,
            semantic_similarity_score=relevance_result.soft_match.semantic_similarity_score,
            role_alignment_score=relevance_result.soft_match.role_alignment_score,
            project_relevance_score=relevance_result.soft_match.project_relevance_score,
            overall_semantic_score=relevance_result.soft_match.overall_semantic_score,
            relevance_score=relevance_result.relevance_score,
            fit_verdict=relevance_result.fit_verdict.value,
            missing_elements=relevance_result.missing_elements,
            improvement_suggestions=relevance_result.improvement_suggestions
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        return {
            "analysis_id": db_analysis.id,
            "job_title": job.role_title,
            "student_name": resume.student_name,
            "relevance_score": relevance_result.relevance_score,
            "fit_verdict": relevance_result.fit_verdict,
            "detailed_analysis": {
                "hard_match": {
                    "score": relevance_result.hard_match.hard_match_score,
                    "matched_must_have": relevance_result.hard_match.matched_must_have_skills,
                    "missing_must_have": relevance_result.hard_match.missing_must_have_skills,
                    "qualification_match": relevance_result.hard_match.qualification_match,
                    "experience_match": relevance_result.hard_match.experience_match
                },
                "soft_match": {
                    "score": relevance_result.soft_match.overall_semantic_score,
                    "semantic_similarity": relevance_result.soft_match.semantic_similarity_score,
                    "role_alignment": relevance_result.soft_match.role_alignment_score,
                    "project_relevance": relevance_result.soft_match.project_relevance_score
                },
                "missing_elements": relevance_result.missing_elements,
                "improvement_suggestions": relevance_result.improvement_suggestions
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

# Bulk Evaluation
@app.post("/api/evaluate-bulk/{job_id}")
async def bulk_evaluate_resumes(
    job_id: int,
    resume_ids: List[int],
    db: Session = Depends(get_db)
):
    """Evaluate multiple resumes against a job description"""
    
    job = db.query(JobDescriptionModel).filter(JobDescriptionModel.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    results = []
    high_fit_count = 0
    medium_fit_count = 0
    low_fit_count = 0
    
    for resume_id in resume_ids:
        try:
            # Call individual evaluation
            result = await evaluate_resume_for_job(job_id, resume_id, db)
            results.append(result)
            
            # Count fit verdicts
            verdict = result["fit_verdict"]
            if verdict == "High":
                high_fit_count += 1
            elif verdict == "Medium":
                medium_fit_count += 1
            else:
                low_fit_count += 1
                
        except Exception as e:
            print(f"Error evaluating resume {resume_id}: {e}")
            continue
    
    return {
        "job_title": job.role_title,
        "total_processed": len(results),
        "high_fit_count": high_fit_count,
        "medium_fit_count": medium_fit_count,
        "low_fit_count": low_fit_count,
        "results": results
    }

# Dashboard and Analytics
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get placement dashboard statistics"""
    
    # Get counts
    total_jobs = db.query(JobDescriptionModel).filter(JobDescriptionModel.is_active == True).count()
    total_resumes = db.query(StudentResumeModel).count()
    total_analyses = db.query(RelevanceAnalysisModel).count()
    
    # Get fit verdict counts
    high_fit = db.query(RelevanceAnalysisModel).filter(RelevanceAnalysisModel.fit_verdict == "High").count()
    medium_fit = db.query(RelevanceAnalysisModel).filter(RelevanceAnalysisModel.fit_verdict == "Medium").count()
    low_fit = db.query(RelevanceAnalysisModel).filter(RelevanceAnalysisModel.fit_verdict == "Low").count()
    
    # Calculate average relevance score
    avg_score_result = db.query(func.avg(RelevanceAnalysisModel.relevance_score)).scalar()
    avg_score = float(avg_score_result) if avg_score_result else 0.0
    
    # Get stats by location
    location_stats = {}
    for location in ["Hyderabad", "Bangalore", "Pune", "Delhi NCR"]:
        location_jobs = db.query(JobDescriptionModel).filter(
            JobDescriptionModel.location == location,
            JobDescriptionModel.is_active == True
        ).count()
        location_stats[location] = location_jobs
    
    return {
        "total_jobs_this_week": total_jobs,  # Simplified for demo
        "total_resumes_analyzed": total_resumes,
        "total_evaluations": total_analyses,
        "high_fit_candidates": high_fit,
        "medium_fit_candidates": medium_fit,
        "low_fit_candidates": low_fit,
        "avg_relevance_score": round(avg_score, 2),
        "by_location": location_stats
    }

# Search and Filter
@app.get("/api/search/analyses")
async def search_analyses(
    job_id: Optional[int] = None,
    fit_verdict: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Search and filter resume analyses"""
    
    query = db.query(RelevanceAnalysisModel)
    
    if job_id:
        query = query.filter(RelevanceAnalysisModel.job_id == job_id)
    
    if fit_verdict:
        query = query.filter(RelevanceAnalysisModel.fit_verdict == fit_verdict)
    
    if min_score is not None:
        query = query.filter(RelevanceAnalysisModel.relevance_score >= min_score)
    
    if max_score is not None:
        query = query.filter(RelevanceAnalysisModel.relevance_score <= max_score)
    
    analyses = query.order_by(RelevanceAnalysisModel.relevance_score.desc()).limit(limit).all()
    
    # Calculate stats for filtered results
    total_count = query.count()
    avg_score_result = query.with_entities(func.avg(RelevanceAnalysisModel.relevance_score)).scalar()
    avg_score = float(avg_score_result) if avg_score_result else 0.0
    
    return {
        "analyses": analyses,
        "total_count": total_count,
        "avg_score": round(avg_score, 2),
        "filters_applied": {
            "job_id": job_id,
            "fit_verdict": fit_verdict,
            "min_score": min_score,
            "max_score": max_score
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)