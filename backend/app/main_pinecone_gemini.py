from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from typing import Optional

from app.config import settings
from app.services.pinecone_gemini_service import pinecone_gemini_service

# Pydantic models for API requests
class PDFUrlRequest(BaseModel):
    url: str
    document_id: Optional[str] = None

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5

class ResumeEvaluationRequest(BaseModel):
    resume_text: str
    job_description: str

# Initialize FastAPI app
app = FastAPI(
    title="Resume Relevance System with Pinecone + Gemini",
    description="An AI-powered system using Pinecone vector database and Google Gemini AI",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
os.makedirs(settings.upload_dir, exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Resume Relevance System with Pinecone + Gemini AI",
        "version": "2.0.0",
        "docs": "/docs",
        "features": [
            "PDF processing from URLs and file uploads",
            "Vector storage with Pinecone",
            "Semantic search and RAG",
            "Google Gemini AI integration",
            "Resume evaluation"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Pinecone + Gemini endpoints
@app.post("/api/pdf/upload-url")
async def upload_pdf_from_url(request: PDFUrlRequest):
    """Upload PDF from URL to Pinecone vector database"""
    try:
        success = pinecone_gemini_service.process_pdf_url(
            pdf_url=request.url,
            document_id=request.document_id
        )
        
        if success:
            return {
                "message": f"PDF from {request.url} processed and stored successfully",
                "document_id": request.document_id,
                "status": "success"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to process PDF")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/api/pdf/upload-file")
async def upload_pdf_file(file: UploadFile = File(...), document_id: Optional[str] = Form(None)):
    """Upload PDF file to Pinecone vector database"""
    try:
        # Check file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save uploaded file temporarily
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        # Process the file
        success = pinecone_gemini_service.process_pdf_file(
            file_path=temp_file_path,
            document_id=document_id or file.filename
        )
        
        # Clean up temp file
        os.remove(temp_file_path)
        
        if success:
            return {
                "message": f"PDF file {file.filename} processed and stored successfully",
                "document_id": document_id or file.filename,
                "status": "success"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to process PDF")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/api/query")
async def query_documents(request: QueryRequest):
    """Query documents using RAG (Retrieval-Augmented Generation)"""
    try:
        result = pinecone_gemini_service.query_rag_system(
            query=request.question,
            top_k=request.top_k
        )
        
        return {
            "response": result["response"],
            "sources": result["sources"],
            "confidence": result["confidence"],
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying documents: {str(e)}")


@app.post("/api/resume/evaluate-with-gemini")
async def evaluate_resume_with_gemini(request: ResumeEvaluationRequest):
    """Evaluate resume relevance using Gemini AI"""
    try:
        result = pinecone_gemini_service.evaluate_resume_relevance(
            resume_text=request.resume_text,
            job_description=request.job_description
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "analysis": result["analysis"],
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating resume: {str(e)}")


@app.delete("/api/pinecone/clear")
async def clear_pinecone_index():
    """Clear all vectors from Pinecone index"""
    try:
        success = pinecone_gemini_service.clear_index()
        
        if success:
            return {"message": "Pinecone index cleared successfully", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear index")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing index: {str(e)}")


@app.get("/api/config/check")
async def check_configuration():
    """Check if all API keys and services are configured"""
    return {
        "pinecone_configured": bool(settings.pinecone_api_key),
        "nomic_configured": bool(settings.nomic_api_key),
        "gemini_configured": bool(settings.gemini_api_key),
        "services_status": "configured" if all([
            settings.pinecone_api_key,
            settings.nomic_api_key,
            settings.gemini_api_key
        ]) else "incomplete_configuration",
        "missing_configs": [
            key for key, value in {
                "gemini_api_key": settings.gemini_api_key,
                "pinecone_api_key": settings.pinecone_api_key,
                "nomic_api_key": settings.nomic_api_key
            }.items() if not value or value == "your_gemini_api_key_here"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.debug)