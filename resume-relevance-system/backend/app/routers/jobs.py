from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.models.database import get_db, Job as DBJob
from app.models.schemas import (
    JobCreate, Job, JobResponse, JobListResponse
)

router = APIRouter()


@router.post("/", response_model=JobResponse)
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Create a new job posting"""
    try:
        db_job = DBJob(
            title=job.title,
            company=job.company,
            description=job.description,
            required_skills=json.dumps(job.required_skills),
            preferred_skills=json.dumps(job.preferred_skills),
            qualifications=job.qualifications,
            experience_required=job.experience_required,
            location=job.location,
        )
        
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        
        # Convert back to Pydantic model
        job_dict = {
            "id": db_job.id,
            "title": db_job.title,
            "company": db_job.company,
            "description": db_job.description,
            "required_skills": json.loads(db_job.required_skills or "[]"),
            "preferred_skills": json.loads(db_job.preferred_skills or "[]"),
            "qualifications": db_job.qualifications,
            "experience_required": db_job.experience_required,
            "location": db_job.location,
            "created_at": db_job.created_at,
            "is_active": db_job.is_active
        }
        
        return JobResponse(
            success=True,
            message="Job created successfully",
            data=Job(**job_dict)
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    skip: int = 0,
    limit: int = 50,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """List all jobs with pagination"""
    try:
        query = db.query(DBJob)
        if active_only:
            query = query.filter(DBJob.is_active == True)
        
        total = query.count()
        jobs = query.offset(skip).limit(limit).all()
        
        job_list = []
        for db_job in jobs:
            job_dict = {
                "id": db_job.id,
                "title": db_job.title,
                "company": db_job.company,
                "description": db_job.description,
                "required_skills": json.loads(db_job.required_skills or "[]"),
                "preferred_skills": json.loads(db_job.preferred_skills or "[]"),
                "qualifications": db_job.qualifications,
                "experience_required": db_job.experience_required,
                "location": db_job.location,
                "created_at": db_job.created_at,
                "is_active": db_job.is_active
            }
            job_list.append(Job(**job_dict))
        
        return JobListResponse(
            success=True,
            message="Jobs retrieved successfully",
            data=job_list,
            total=total
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve jobs: {str(e)}"
        )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job by ID"""
    try:
        db_job = db.query(DBJob).filter(DBJob.id == job_id).first()
        if not db_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        job_dict = {
            "id": db_job.id,
            "title": db_job.title,
            "company": db_job.company,
            "description": db_job.description,
            "required_skills": json.loads(db_job.required_skills or "[]"),
            "preferred_skills": json.loads(db_job.preferred_skills or "[]"),
            "qualifications": db_job.qualifications,
            "experience_required": db_job.experience_required,
            "location": db_job.location,
            "created_at": db_job.created_at,
            "is_active": db_job.is_active
        }
        
        return JobResponse(
            success=True,
            message="Job retrieved successfully",
            data=Job(**job_dict)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job: {str(e)}"
        )


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(job_id: int, job: JobCreate, db: Session = Depends(get_db)):
    """Update a job posting"""
    try:
        db_job = db.query(DBJob).filter(DBJob.id == job_id).first()
        if not db_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        db_job.title = job.title
        db_job.company = job.company
        db_job.description = job.description
        db_job.required_skills = json.dumps(job.required_skills)
        db_job.preferred_skills = json.dumps(job.preferred_skills)
        db_job.qualifications = job.qualifications
        db_job.experience_required = job.experience_required
        db_job.location = job.location
        
        db.commit()
        db.refresh(db_job)
        
        job_dict = {
            "id": db_job.id,
            "title": db_job.title,
            "company": db_job.company,
            "description": db_job.description,
            "required_skills": json.loads(db_job.required_skills or "[]"),
            "preferred_skills": json.loads(db_job.preferred_skills or "[]"),
            "qualifications": db_job.qualifications,
            "experience_required": db_job.experience_required,
            "location": db_job.location,
            "created_at": db_job.created_at,
            "is_active": db_job.is_active
        }
        
        return JobResponse(
            success=True,
            message="Job updated successfully",
            data=Job(**job_dict)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job: {str(e)}"
        )


@router.delete("/{job_id}")
async def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete (deactivate) a job posting"""
    try:
        db_job = db.query(DBJob).filter(DBJob.id == job_id).first()
        if not db_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        db_job.is_active = False
        db.commit()
        
        return {"success": True, "message": "Job deactivated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job: {str(e)}"
        )