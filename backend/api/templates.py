from fastapi import APIRouter
from typing import List, Dict, Any
import json
import uuid
from datetime import datetime

router = APIRouter()

# In-memory storage for templates
templates = {}

@router.post("/templates")
async def create_template(name: str, description: str, fields: List[Dict[str, Any]]):
    """
    Create a new template
    """
    template_id = str(uuid.uuid4())

    template = {
        "id": template_id,
        "name": name,
        "description": description,
        "fields": fields,
        "field_types": {field.get("name", ""): field.get("field_type", "text") for field in fields},
        "confidence_threshold": 0.7,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    templates[template_id] = template

    return template

@router.get("/templates")
async def list_templates():
    """
    List all templates
    """
    return {"templates": list(templates.values()), "total": len(templates)}

@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """
    Get a template by ID
    """
    if template_id not in templates:
        return {"error": "Template not found"}

    return templates[template_id]

@router.post("/templates/learn-from-document/{job_id}")
async def learn_template_from_document(job_id: str):
    """
    Learn a new template from a processed document
    """
    from api.documents import processing_jobs

    if job_id not in processing_jobs:
        return {"error": "Document processing job not found"}

    job = processing_jobs[job_id]

    if job["status"] != "completed":
        return {"error": "Document has not been processed yet"}

    if not job.get("result"):
        return {"error": "No processed data available"}

    # Extract fields from processed document
    fields = job["result"].get("fields", [])

    if not fields:
        return {"error": "No fields detected in document"}

    # Create template from fields
    template_fields = []
    for field in fields:
        template_field = {
            "name": field.get("name", ""),
            "field_type": field.get("field_type", "text"),
            "bbox": field.get("bbox", {}),
            "confidence_threshold": field.get("confidence", 0.7)
        }
        template_fields.append(template_field)

    # Create new template
    template_id = str(uuid.uuid4())
    template_name = f"template_from_{job['original_filename']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    template = {
        "id": template_id,
        "name": template_name,
        "description": f"Auto-generated template from {job['original_filename']}",
        "fields": template_fields,
        "field_types": {field["name"]: field["field_type"] for field in template_fields},
        "confidence_threshold": 0.7,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    templates[template_id] = template

    return template

# Add the template routes to the main app