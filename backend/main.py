from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import tempfile
import os
from typing import Optional
from datetime import datetime
import uuid
from pathlib import Path
import asyncio
import json

from api.documents import router as documents_router
from api.templates import router as templates_router
from api.export import router as export_router
from core.config import settings

app = FastAPI(
    title="Simple AI Document Processor API",
    description="Simplified document processing with OCR, field detection, and validation - no database required",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(documents_router, prefix="", tags=["documents"])
app.include_router(templates_router, prefix="", tags=["templates"])
app.include_router(export_router, prefix="", tags=["export"])

@app.get("/")
async def root():
    return {"message": "Simple AI Document Processor API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )