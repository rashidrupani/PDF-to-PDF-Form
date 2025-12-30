from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import tempfile
import os
from typing import Optional
import uuid
from datetime import datetime
from pathlib import Path
import json
import asyncio

from core.config import settings
from services.ocr_engine import OCREngine
from services.document_preprocessor import DocumentPreprocessor
from services.form_field_detector import FormFieldDetector
from services.confidence_scorer import ConfidenceScorer
from services.structured_output_creator import StructuredOutputCreator

router = APIRouter()

# In-memory storage for document processing status (in production, use Redis or similar)
processing_jobs = {}

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Upload a document for processing
    """
    # Validate file type
    allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed types: {allowed_extensions}"
        )

    # Validate file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds {settings.MAX_FILE_SIZE} bytes limit"
        )

    # Save uploaded file
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_FOLDER, f"{file_id}{file_extension}")

    with open(file_path, "wb") as f:
        f.write(file_content)

    # Create processing job record
    job_id = str(uuid.uuid4())
    processing_jobs[job_id] = {
        "id": job_id,
        "file_id": file_id,
        "original_filename": file.filename,
        "file_path": file_path,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "progress": 0,
        "result": None,
        "error": None
    }

    # Add background task for document processing
    background_tasks.add_task(
        process_uploaded_document,
        job_id,
        file_path
    )

    return {
        "job_id": job_id,
        "file_id": file_id,
        "original_filename": file.filename,
        "status": "pending",
        "created_at": processing_jobs[job_id]["created_at"]
    }

async def process_uploaded_document(job_id: str, file_path: str):
    """
    Process uploaded document in background
    """
    try:
        # Update job status to started
        processing_jobs[job_id]["status"] = "processing"
        processing_jobs[job_id]["progress"] = 10

        # Initialize processing components
        preprocessor = DocumentPreprocessor()
        ocr_engine = OCREngine()
        field_detector = FormFieldDetector()
        confidence_scorer = ConfidenceScorer()
        output_creator = StructuredOutputCreator()

        # Preprocess document
        processing_jobs[job_id]["progress"] = 20
        preprocessed_pages = preprocessor.preprocess_document(file_path)

        # Process with OCR engines
        processing_jobs[job_id]["progress"] = 40
        if preprocessed_pages:
            # For simplicity, process first page (in real app, process all pages)
            from services.multi_ocr_engine import MultiOCREngine, EnsembleMethod
            multi_ocr = MultiOCREngine()
            multi_ocr_results = multi_ocr.process_image(
                preprocessed_pages[0],
                ensemble_method=EnsembleMethod.VOTE_BY_CONFIDENCE
            )

            # Convert multi-ocr results to standard format
            from services.ocr_engine import OCRResult
            ocr_results = []
            for result in multi_ocr_results:
                ocr_results.append(OCRResult(
                    text=result.text,
                    bbox=result.bbox,
                    confidence=result.confidence,
                    engine=result.primary_engine
                ))
        else:
            ocr_results = []

        # Detect form fields
        processing_jobs[job_id]["progress"] = 60
        detected_fields = field_detector.detect_fields(
            preprocessed_pages[0] if preprocessed_pages else None,
            ocr_results
        )

        # Calculate confidence scores
        from services.ocr_engine import ExtractionResult
        temp_extraction = ExtractionResult(
            text_blocks=ocr_results,
            fields=detected_fields,
            confidence_scores={},
            processing_time=0.0
        )

        # Update confidence scores
        processing_jobs[job_id]["progress"] = 80
        updated_extraction = confidence_scorer.update_confidence_scores(temp_extraction)

        # Create structured output
        processing_jobs[job_id]["progress"] = 90
        processed_doc = output_creator.create_structured_output(
            updated_extraction,
            file_path,
            document_id=processing_jobs[job_id]["file_id"]
        )

        # Store result
        processing_jobs[job_id]["result"] = processed_doc
        processing_jobs[job_id]["status"] = "completed"
        processing_jobs[job_id]["progress"] = 100

    except Exception as e:
        # Update job status to failed
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["error"] = str(e)
        processing_jobs[job_id]["progress"] = 100

        print(f"Error processing document {job_id}: {str(e)}")

@router.get("/documents/{job_id}")
async def get_document(job_id: str):
    """
    Get document processing result
    """
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Document processing job not found")

    job = processing_jobs[job_id]

    return {
        "job_id": job["id"],
        "file_id": job["file_id"],
        "original_filename": job["original_filename"],
        "status": job["status"],
        "created_at": job["created_at"],
        "progress": job["progress"],
        "result": job["result"],
        "error": job["error"]
    }

@router.get("/documents/{job_id}/status")
async def get_document_processing_status(job_id: str):
    """
    Get document processing status
    """
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Document processing job not found")

    job = processing_jobs[job_id]

    return {
        "job_id": job["id"],
        "status": job["status"],
        "original_filename": job["original_filename"],
        "progress": job["progress"],
        "created_at": job["created_at"],
        "error": job["error"]
    }

@router.get("/documents")
async def list_documents():
    """
    List all documents in memory
    """
    return {
        "documents": [
            {
                "job_id": job["id"],
                "file_id": job["file_id"],
                "original_filename": job["original_filename"],
                "status": job["status"],
                "created_at": job["created_at"],
                "progress": job["progress"]
            }
            for job in processing_jobs.values()
        ],
        "total": len(processing_jobs)
    }