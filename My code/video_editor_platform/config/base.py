"""
Base configuration for GenAI Video Editor
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "GenAI Video Editor"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://localhost:3000",
    ]

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/video_editor"
    )
    DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() == "true"

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", "3600"))  # 1 hour

    # AWS
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "video-editor-uploads")

    # File Upload
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
    ALLOWED_VIDEO_FORMATS: List[str] = ["mp4", "mov", "avi", "mkv", "webm"]
    UPLOAD_TEMP_DIR: str = os.getenv("UPLOAD_TEMP_DIR", "/tmp/video_uploads")

    # Optional template directory for promotional backgrounds
    # can be set via the TEMPLATES_DIR env var or defaults to "sample templates"
    TEMPLATES_DIR: str = os.getenv("TEMPLATES_DIR", "sample templates")

    # API Keys (Optional - for when using paid models)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")  # Optional, only needed for GPT-4
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")  # Optional, only needed for premium TTS
    
    # LLM Local Setup
    USE_LOCAL_LLM: bool = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"  # Use LLaMA-2 locally
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")  # Local model name
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")  # Ollama server URL
    
    # TTS Configuration
    USE_LOCAL_TTS: bool = os.getenv("USE_LOCAL_TTS", "true").lower() == "true"  # Use pyttsx3 locally
    TTS_VOICE_ID: str = os.getenv("TTS_VOICE_ID", "default")  # Voice for pyttsx3

    # Processing
    VIDEO_ENHANCEMENT_ENABLED: bool = True
    COMPRESSION_QUALITY: int = 85  # 0-100
    TARGET_FPS: int = 24
    TARGET_RESOLUTION_HEIGHT: int = 1920  # 9:16 aspect ratio

    # GPU
    USE_GPU: bool = os.getenv("USE_GPU", "true").lower() == "true"
    CUDA_DEVICE_ID: int = int(os.getenv("CUDA_DEVICE_ID", "0"))

    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/2"
    )
    CELERY_TASK_TIME_LIMIT: int = 3600  # 1 hour

    # Timeouts
    VIDEO_PROCESSING_TIMEOUT: int = 300  # 5 minutes
    API_REQUEST_TIMEOUT: int = 30  # 30 seconds

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 3600

    class Config:
        env_file = ".env"
        case_sensitive = True
