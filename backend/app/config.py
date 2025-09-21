from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./resume_system.db"
    
    # Pinecone Configuration
    pinecone_api_key: str = "pcsk_4B27To_tY2jeLoxqgm97GKUfwxMccU39ZsN3jcd2D8Lq7UjZhjwEyHerwKDc8hpeinqpe"
    pinecone_index_name: str = "lang"
    pinecone_environment: str = "us-east-1"
    
    # Nomic AI Configuration (for embeddings)
    nomic_api_key: str = "nk-LeXriqiihZl6pT8TT4QhSB8JQVhmJBAznO6Y-EaaDX4"
    
    # Google Gemini Configuration
    gemini_api_key: str = "AIzaSyCdJtJj4eHmFEGU2iyyiVrwlf4jrH3P45Q"  # Default from .env.render
    
    # Application
    app_name: str = "Resume Relevance Check System"
    debug: bool = False  # Default to False for production
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", 8000))  # Support Render's PORT env var
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    allowed_origins: List[str] = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
        "https://nighthack-ytan.vercel.app",  # Your Vercel frontend
        "https://nighthack-ytan.vercel.app/"  # With trailing slash
    ]
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = ["pdf", "docx"]
    upload_dir: str = "uploads"
    
    # AI Settings
    embedding_model: str = "nomic-embed-text-v1.5"
    llm_model: str = "gemini-1.5-flash"  # Changed from OpenAI to Gemini
    similarity_threshold: float = 0.7
    embedding_dimensionality: int = 256
    
    # Text Processing Settings
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Scoring Weights
    hard_match_weight: float = 0.4
    semantic_match_weight: float = 0.6
    
    class Config:
        env_file = ".env"


settings = Settings()