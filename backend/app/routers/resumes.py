from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os
import uuid
from datetime import datetime

from app.models.database import get_db, Resume as DBResume
from app.models.schemas import Resume, ResumeResponse, ResumeListResponse, FileUploadResponse
from app.services.resume_parser import ResumeParser
from app.config import settings

router = APIRouter()
resume_parser = ResumeParser()


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    candidate_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload and parse a resume file"""
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file selected"
            )
        
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in settings.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Supported formats: {', '.join(settings.allowed_extensions)}"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size is 10MB"
            )
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(settings.upload_dir, unique_filename)
        
        # Save file
        os.makedirs(settings.upload_dir, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Parse resume
        parsed_data = resume_parser.parse_resume(file_path)
        
        # Use extracted contact info if not provided in form
        contact_info = parsed_data.get('contact_info', {})
        final_candidate_name = candidate_name or contact_info.get('name', 'Unknown Candidate')
        final_email = email or contact_info.get('email', '')
        final_phone = phone or contact_info.get('phone', '')
        
        # If still no name, try to extract from filename
        if final_candidate_name == 'Unknown Candidate' and file.filename:
            # Remove extension and clean filename for candidate name
            base_name = os.path.splitext(file.filename)[0]
            # Replace underscores/dashes with spaces and title case
            final_candidate_name = base_name.replace('_', ' ').replace('-', ' ').title()
        
        # Save to database
        db_resume = DBResume(
            candidate_name=final_candidate_name,
            email=final_email,
            phone=final_phone,
            filename=file.filename,
            file_path=file_path,
            extracted_text=parsed_data.get('text', ''),
            skills=json.dumps(parsed_data.get('skills', [])),
            experience=json.dumps(parsed_data.get('experience', [])),
            education=json.dumps(parsed_data.get('education', [])),
            projects=json.dumps(parsed_data.get('projects', [])),
            certifications=json.dumps(parsed_data.get('certifications', []))
        )
        
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        
        # Convert to response format
        resume_dict = {
            "id": db_resume.id,
            "candidate_name": db_resume.candidate_name,
            "email": db_resume.email,
            "phone": db_resume.phone,
            "filename": db_resume.filename,
            "file_path": db_resume.file_path,
            "skills": json.loads(db_resume.skills or "[]"),
            "experience": json.loads(db_resume.experience or "[]"),
            "education": json.loads(db_resume.education or "[]"),
            "projects": json.loads(db_resume.projects or "[]"),
            "certifications": json.loads(db_resume.certifications or "[]"),
            "uploaded_at": db_resume.uploaded_at
        }
        
        return ResumeResponse(
            success=True,
            message=f"Resume uploaded successfully for {db_resume.candidate_name}",
            data=Resume(**resume_dict)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        # Clean up file if database operation fails
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process resume: {str(e)}"
        )


@router.get("/", response_model=ResumeListResponse)
async def list_resumes(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all resumes with pagination"""
    try:
        query = db.query(DBResume)
        total = query.count()
        resumes = query.offset(skip).limit(limit).all()
        
        resume_list = []
        for db_resume in resumes:
            resume_dict = {
                "id": db_resume.id,
                "candidate_name": db_resume.candidate_name,
                "email": db_resume.email,
                "phone": db_resume.phone,
                "filename": db_resume.filename,
                "file_path": db_resume.file_path,
                "skills": json.loads(db_resume.skills or "[]"),
                "experience": json.loads(db_resume.experience or "[]"),
                "education": json.loads(db_resume.education or "[]"),
                "projects": json.loads(db_resume.projects or "[]"),
                "certifications": json.loads(db_resume.certifications or "[]"),
                "uploaded_at": db_resume.uploaded_at
            }
            resume_list.append(Resume(**resume_dict))
        
        return ResumeListResponse(
            success=True,
            message="Resumes retrieved successfully",
            data=resume_list,
            total=total
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve resumes: {str(e)}"
        )


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """Get a specific resume by ID"""
    try:
        db_resume = db.query(DBResume).filter(DBResume.id == resume_id).first()
        if not db_resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        resume_dict = {
            "id": db_resume.id,
            "candidate_name": db_resume.candidate_name,
            "email": db_resume.email,
            "phone": db_resume.phone,
            "filename": db_resume.filename,
            "file_path": db_resume.file_path,
            "skills": json.loads(db_resume.skills or "[]"),
            "experience": json.loads(db_resume.experience or "[]"),
            "education": json.loads(db_resume.education or "[]"),
            "projects": json.loads(db_resume.projects or "[]"),
            "certifications": json.loads(db_resume.certifications or "[]"),
            "uploaded_at": db_resume.uploaded_at
        }
        
        return ResumeResponse(
            success=True,
            message="Resume retrieved successfully",
            data=Resume(**resume_dict)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve resume: {str(e)}"
        )


@router.delete("/{resume_id}")
async def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    """Delete a resume and its associated file"""
    try:
        db_resume = db.query(DBResume).filter(DBResume.id == resume_id).first()
        if not db_resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        # Delete file from filesystem
        if os.path.exists(db_resume.file_path):
            os.remove(db_resume.file_path)
        
        # Delete from database
        db.delete(db_resume)
        db.commit()
        
        return {"success": True, "message": "Resume deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete resume: {str(e)}"
        )