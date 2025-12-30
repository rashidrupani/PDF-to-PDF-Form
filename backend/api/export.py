from fastapi import APIRouter, HTTPException, Response
from typing import Optional
import os
from pathlib import Path
import json
import csv
import pandas as pd
from io import BytesIO

from core.config import settings

router = APIRouter()

@router.post("/documents/{job_id}/export")
async def export_document(job_id: str, format_type: str):
    """
    Export processed document in specified format
    """
    from api.documents import processing_jobs

    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Document processing job not found")

    job = processing_jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Document has not been processed yet or processing failed")

    if not job.get("result"):
        raise HTTPException(status_code=400, detail="No processed data available for export")

    # Validate format type
    if format_type.lower() not in ['xlsx', 'csv', 'json', 'pdf']:
        raise HTTPException(status_code=400, detail="Invalid format type. Supported: xlsx, csv, json, pdf")

    # Generate export filename
    timestamp = job["created_at"].replace(":", "").replace("-", "").replace(".", "")
    filename = f"export_{job['file_id']}_{timestamp}.{format_type.lower()}"
    export_path = Path(settings.EXPORT_FOLDER) / filename

    try:
        if format_type.lower() == 'json':
            # Export as JSON
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(job["result"], f, ensure_ascii=False, indent=2, default=str)

        elif format_type.lower() == 'csv':
            # Export as CSV
            fields = job["result"].get("fields", [])
            if fields:
                df = pd.DataFrame(fields)
            else:
                text_blocks = job["result"].get("text_blocks", [])
                df = pd.DataFrame(text_blocks)

            df.to_csv(export_path, index=False)

        elif format_type.lower() == 'xlsx':
            # Export as Excel
            fields = job["result"].get("fields", [])
            if fields:
                df = pd.DataFrame(fields)
            else:
                text_blocks = job["result"].get("text_blocks", [])
                df = pd.DataFrame(text_blocks)

            df.to_excel(export_path, index=False, engine='openpyxl')

        elif format_type.lower() == 'pdf':
            # For PDF export, we'll need to implement this functionality
            # For now, just export as JSON and rename
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(job["result"], f, ensure_ascii=False, indent=2, default=str)

        # Return file for download
        with open(export_path, "rb") as file:
            file_content = file.read()

        media_types = {
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'csv': 'text/csv',
            'json': 'application/json',
            'pdf': 'application/pdf'
        }

        return Response(
            content=file_content,
            media_type=media_types.get(format_type.lower(), 'application/octet-stream'),
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# Add the export route to the main app