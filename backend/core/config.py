import os
from typing import List

class Settings:
    # Application settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Processing settings
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB default
    ALLOWED_FILE_TYPES: List[str] = os.getenv("ALLOWED_FILE_TYPES", "pdf,jpg,jpeg,png,tiff").split(",")
    PROCESSING_TIMEOUT: int = int(os.getenv("PROCESSING_TIMEOUT", "300"))  # 5 minutes

    # OCR settings
    OCR_ENHANCEMENT_ENABLED: bool = os.getenv("OCR_ENHANCEMENT_ENABLED", "True").lower() == "true"
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
    LOW_CONFIDENCE_THRESHOLD: float = float(os.getenv("LOW_CONFIDENCE_THRESHOLD", "0.5"))

    # Storage settings
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "./uploads")
    PROCESSED_FOLDER: str = os.getenv("PROCESSED_FOLDER", "./processed")
    EXPORT_FOLDER: str = os.getenv("EXPORT_FOLDER", "./exports")
    TEMP_FOLDER: str = os.getenv("TEMP_FOLDER", "./temp")

    # CORS settings
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")

settings = Settings()

# Create directories if they don't exist
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.PROCESSED_FOLDER, exist_ok=True)
os.makedirs(settings.EXPORT_FOLDER, exist_ok=True)
os.makedirs(settings.TEMP_FOLDER, exist_ok=True)