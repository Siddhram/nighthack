from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
import time

from app.models.database import get_db, Evaluation as DBEvaluation, Job as DBJob, Resume as DBResume
from app.models.schemas import (
    EvaluationResponse, EvaluationResult, Evaluation, EvaluationListResponse
)
from app.services.evaluation_engine import EvaluationEngine
from app.config import settings

router = APIRouter()
evaluation_engine = EvaluationEngine()


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_resume(
    job_id: int,
    resume_id: int,
    db: Session = Depends(get_db)
):
    """Evaluate a resume against a job posting"""
    start_time = time.time()
    
    try:
        # Get job and resume from database
        job = db.query(DBJob).filter(DBJob.id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        resume = db.query(DBResume).filter(DBResume.id == resume_id).first()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        # Check if evaluation already exists
        existing_evaluation = db.query(DBEvaluation).filter(
            DBEvaluation.job_id == job_id,
            DBEvaluation.resume_id == resume_id
        ).first()
        
        if existing_evaluation:
            # Return existing evaluation
            result = {
                "relevance_score": existing_evaluation.relevance_score,
                "hard_match_score": existing_evaluation.hard_match_score,
                "semantic_match_score": existing_evaluation.semantic_match_score,
                "matched_skills": json.loads(existing_evaluation.matched_skills or "[]"),
                "missing_skills": json.loads(existing_evaluation.missing_skills or "[]"),
                "matched_qualifications": json.loads(existing_evaluation.matched_qualifications or "[]"),
                "missing_qualifications": json.loads(existing_evaluation.missing_qualifications or "[]"),
                "suitability": existing_evaluation.suitability,
                "feedback": existing_evaluation.feedback
            }
            
            return EvaluationResponse(
                success=True,
                message="Evaluation retrieved from cache",
                data=EvaluationResult(**result)
            )
        
        # Prepare data for evaluation
        job_data = {
            "title": job.title,
            "description": job.description,
            "required_skills": json.loads(job.required_skills or "[]"),
            "preferred_skills": json.loads(job.preferred_skills or "[]"),
            "qualifications": job.qualifications,
            "experience_required": job.experience_required
        }
        
        resume_data = {
            "text": resume.extracted_text,
            "skills": json.loads(resume.skills or "[]"),
            "experience": json.loads(resume.experience or "[]"),
            "education": json.loads(resume.education or "[]"),
            "projects": json.loads(resume.projects or "[]"),
            "certifications": json.loads(resume.certifications or "[]")
        }
        
        # Run evaluation
        result = await evaluation_engine.evaluate(job_data, resume_data)
        
        # Calculate evaluation time
        evaluation_time = time.time() - start_time
        
        # Save evaluation to database
        db_evaluation = DBEvaluation(
            job_id=job_id,
            resume_id=resume_id,
            relevance_score=result["relevance_score"],
            hard_match_score=result["hard_match_score"],
            semantic_match_score=result["semantic_match_score"],
            matched_skills=json.dumps(result["matched_skills"]),
            missing_skills=json.dumps(result["missing_skills"]),
            matched_qualifications=json.dumps(result["matched_qualifications"]),
            missing_qualifications=json.dumps(result["missing_qualifications"]),
            suitability=result["suitability"],
            feedback=result["feedback"],
            evaluation_time_seconds=evaluation_time
        )
        
        db.add(db_evaluation)
        db.commit()
        db.refresh(db_evaluation)
        
        return EvaluationResponse(
            success=True,
            message="Resume evaluated successfully",
            data=EvaluationResult(**result)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate resume: {str(e)}"
        )


@router.get("/", response_model=EvaluationListResponse)
async def list_evaluations(
    job_id: int = None,
    resume_id: int = None,
    suitability: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List evaluations with optional filters"""
    try:
        query = db.query(DBEvaluation)
        
        # Apply filters
        if job_id:
            query = query.filter(DBEvaluation.job_id == job_id)
        if resume_id:
            query = query.filter(DBEvaluation.resume_id == resume_id)
        if suitability:
            query = query.filter(DBEvaluation.suitability == suitability)
        
        # Order by relevance score descending (highest scores first)
        query = query.order_by(DBEvaluation.relevance_score.desc())
        
        total = query.count()
        evaluations = query.offset(skip).limit(limit).all()
        
        evaluation_list = []
        for db_eval in evaluations:
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
                "job": None,  # Could populate with job data if needed
                "resume": None  # Could populate with resume data if needed
            }
            evaluation_list.append(Evaluation(**eval_dict))
        
        return EvaluationListResponse(
            success=True,
            message="Evaluations retrieved successfully",
            data=evaluation_list,
            total=total
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve evaluations: {str(e)}"
        )


@router.get("/{evaluation_id}")
async def get_evaluation(evaluation_id: int, db: Session = Depends(get_db)):
    """Get a specific evaluation by ID"""
    try:
        db_eval = db.query(DBEvaluation).filter(DBEvaluation.id == evaluation_id).first()
        if not db_eval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found"
            )
        
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
        
        return {
            "success": True,
            "message": "Evaluation retrieved successfully",
            "data": Evaluation(**eval_dict)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve evaluation: {str(e)}"
        )


@router.delete("/{evaluation_id}")
async def delete_evaluation(evaluation_id: int, db: Session = Depends(get_db)):
    """Delete an evaluation"""
    try:
        db_eval = db.query(DBEvaluation).filter(DBEvaluation.id == evaluation_id).first()
        if not db_eval:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found"
            )
        
        db.delete(db_eval)
        db.commit()
        
        return {"success": True, "message": "Evaluation deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete evaluation: {str(e)}"
        )