from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./resume_system.db"
    
    # OpenAI
    openai_api_key: str = ""
    
    # Application
    app_name: str = "Resume Relevance Check System"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = ["pdf", "docx"]
    upload_dir: str = "uploads"
    
    # AI Settings
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "gpt-3.5-turbo"
    similarity_threshold: float = 0.7
    
    # Scoring Weights
    hard_match_weight: float = 0.4
    semantic_match_weight: float = 0.6
    
    class Config:
        env_file = ".env"


settings = Settings()