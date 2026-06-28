from fastapi import APIRouter, HTTPException
from src.applications import service as app_service
from src.resumes import service as resume_service
from src.applications.schemas import AnalyzeRequest, StatusUpdate
from src.applications.exceptions import (
    ApplicationNotFoundException,
    InvalidStatusException
)
from src.resumes.exceptions import ResumeNotFoundException
from src.llm.client import analyze

router = APIRouter(tags=["applications"])

@router.post("/analyze")
async def analyze_resume(request: AnalyzeRequest):
    jd_hash = app_service.compute_jd_hash(request.jd_text)
    existing = app_service.check_duplicate(jd_hash)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Already analyzed this JD on {existing['timestamp']}"
        )
    try:
        resume_record = resume_service.get_by_id(request.resume_id)
    except ResumeNotFoundException:
        raise HTTPException(status_code=404, detail="Resume not found")

    file_path = resume_service.get_file_path(resume_record["filename"])
    resume_text = resume_service.extract_text(file_path)
    analysis = analyze(request.jd_text, resume_text)
    record = app_service.save(request.jd_text, file_path, analysis)
    return record

@router.get("/history")
async def get_history():
    return {"history": app_service.load_all()}

@router.patch("/status/{record_id}")
async def update_status(record_id: str, request: StatusUpdate):
    try:
        record = app_service.update_status(record_id, request.status)
        return {"message": "Status updated", "record": record}
    except ApplicationNotFoundException:
        raise HTTPException(status_code=404, detail="Application not found")
    except InvalidStatusException as e:
        raise HTTPException(status_code=400, detail=str(e))