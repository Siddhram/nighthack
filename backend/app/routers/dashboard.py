from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import json

from app.models.database import get_db, Job as DBJob, Resume as DBResume, Evaluation as DBEvaluation
from app.models.schemas import DashboardStats

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    try:
        # Count totals
        total_jobs = db.query(DBJob).filter(DBJob.is_active == True).count()
        total_resumes = db.query(DBResume).count()
        total_evaluations = db.query(DBEvaluation).count()
        
        # Count by suitability
        suitability_counts = db.query(
            DBEvaluation.suitability,
            func.count(DBEvaluation.id)
        ).group_by(DBEvaluation.suitability).all()
        
        high_suitability_count = 0
        medium_suitability_count = 0
        low_suitability_count = 0
        
        for suitability, count in suitability_counts:
            if suitability == "High":
                high_suitability_count = count
            elif suitability == "Medium":
                medium_suitability_count = count
            elif suitability == "Low":
                low_suitability_count = count
        
        # Get recent evaluations
        recent_evaluations = db.query(DBEvaluation)\
            .order_by(DBEvaluation.evaluated_at.desc())\
            .limit(10)\
            .all()
        
        recent_eval_list = []
        for db_eval in recent_evaluations:
            eval_dict = {
                "id": db_eval.id,
                "job_id": db_eval.job_id,
                "resume_id": db_eval.resume_id,
                "relevance_score": db_eval.relevance_score,
                "hard_match_score": db_eval.hard_match_score,
                "semantic_match_score": db_eval.semantic_match_score,
                "matched_skills": json.loads(db_eval.matched_skills or "[]"),
                "missing_skills": json.loads(db_eval.missing_skills or "[]"),
                "matched_qualifications": json.loads(db_eval.matched_qualifications or "[]"),
                "missing_qualifications": json.loads(db_eval.missing_qualifications or "[]"),
                "suitability": db_eval.suitability,
                "feedback": db_eval.feedback,
                "evaluated_at": db_eval.evaluated_at,
                "evaluation_time_seconds": db_eval.evaluation_time_seconds,
                "job": None,
                "resume": None
            }
            recent_eval_list.append(eval_dict)
        
        return DashboardStats(
            total_jobs=total_jobs,
            total_resumes=total_resumes,
            total_evaluations=total_evaluations,
            high_suitability_count=high_suitability_count,
            medium_suitability_count=medium_suitability_count,
            low_suitability_count=low_suitability_count,
            recent_evaluations=recent_eval_list
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard stats: {str(e)}"
        )


@router.get("/job-performance/{job_id}")
async def get_job_performance(job_id: int, db: Session = Depends(get_db)):
    """Get performance metrics for a specific job"""
    try:
        job = db.query(DBJob).filter(DBJob.id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Get evaluations for this job
        evaluations = db.query(DBEvaluation).filter(DBEvaluation.job_id == job_id).all()
        
        if not evaluations:
            return {
                "job_id": job_id,
                "job_title": job.title,
                "total_applications": 0,
                "average_score": 0,
                "suitability_distribution": {
                    "High": 0,
                    "Medium": 0,
                    "Low": 0
                }
            }
        
        # Calculate metrics
        total_applications = len(evaluations)
        average_score = sum(eval.relevance_score for eval in evaluations) / total_applications
        
        suitability_counts = {"High": 0, "Medium": 0, "Low": 0}
        for eval in evaluations:
            suitability_counts[eval.suitability] = suitability_counts.get(eval.suitability, 0) + 1
        
        return {
            "job_id": job_id,
            "job_title": job.title,
            "total_applications": total_applications,
            "average_score": round(average_score, 2),
            "suitability_distribution": suitability_counts
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job performance: {str(e)}"
        )


@router.get("/top-candidates/{job_id}")
async def get_top_candidates(
    job_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top candidates for a specific job"""
    try:
        job = db.query(DBJob).filter(DBJob.id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Get top evaluations by score
        top_evaluations = db.query(DBEvaluation)\
            .filter(DBEvaluation.job_id == job_id)\
            .order_by(DBEvaluation.relevance_score.desc())\
            .limit(limit)\
            .all()
        
        candidates = []
        for eval in top_evaluations:
            resume = db.query(DBResume).filter(DBResume.id == eval.resume_id).first()
            if resume:
                candidate = {
                    "evaluation_id": eval.id,
                    "resume_id": resume.id,
                    "candidate_name": resume.candidate_name,
                    "email": resume.email,
                    "relevance_score": eval.relevance_score,
                    "suitability": eval.suitability,
                    "matched_skills": json.loads(eval.matched_skills or "[]"),
                    "evaluated_at": eval.evaluated_at
                }
                candidates.append(candidate)
        
        return {
            "job_id": job_id,
            "job_title": job.title,
            "candidates": candidates
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve top candidates: {str(e)}"
        )