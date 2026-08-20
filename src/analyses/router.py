from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.analyses import service as analyses_service
from src.resumes import service as resume_service
from src.job_descriptions import service as jd_service
from src.analyses.schemas import AnalyzeRequest, ApplicationRecord, AnalysesResponse, HistoryResponse, StatusUpdate
from src.resumes.exceptions import ResumeNotFoundException
from src.llm.client import analyze

router = APIRouter(tags=["analyses"])


def serialize_analysis(record) -> ApplicationRecord:
    return ApplicationRecord(
        id=record.id,
        timestamp=record.analyzed_at.strftime("%Y-%m-%d %H:%M:%S"),
        company=record.job_description.company,
        role=record.job_description.role,
        match=record.match,
        score=record.score,
        status=record.status,
        resume_used=record.resume.filename,
        gaps=record.gaps or [],
        suggestions=record.suggestions or [],
        full_analysis=record.full_analysis,
    )

@router.post("/analyze", response_model=ApplicationRecord)
async def analyze_resume(request: AnalyzeRequest, db: Session = Depends(get_db)):
    # Reuse the job description, but deduplicate only the same resume/job pair.
    jd_hash = jd_service.compute_jd_hash(request.jd_text)
    existing_jd = jd_service.get_by_hash(db, jd_hash)
    if existing_jd and analyses_service.get_by_resume_and_jd(db, request.resume_id, existing_jd.id):
        raise HTTPException(
            status_code=409,
            detail=f"This resume has already been analyzed for {existing_jd.company} - {existing_jd.role}"
        )

    # get resume
    try:
        resume = resume_service.get_by_id(db, request.resume_id)
        file_path = resume_service.get_file_path(resume.filename)
    except ResumeNotFoundException:
        raise HTTPException(status_code=404, detail="Resume not found")

    # extract, analyze, save
    resume_text = resume_service.extract_text(file_path)
    analysis = analyze(request.jd_text, resume_text)

    # save JD
    jd_record = existing_jd or jd_service.create(
        db, request.jd_text, analysis["company"], analysis["role"]
    )

    # save analysis
    record = analyses_service.create(db, resume.id, jd_record.id, analysis)

    return serialize_analysis(record)

@router.get("/analyses", response_model=AnalysesResponse)
async def get_analyses(db: Session = Depends(get_db)):
    return {"analyses": [serialize_analysis(record) for record in analyses_service.get_all(db)]}


@router.get("/history", response_model=HistoryResponse, include_in_schema=False)
async def get_history(db: Session = Depends(get_db)):
    return {"history": [serialize_analysis(record) for record in analyses_service.get_all(db)]}

@router.patch("/status/{analysis_id}")
async def update_status(analysis_id: str, request: StatusUpdate, db: Session = Depends(get_db)):
    raise HTTPException(
        status_code=410,
        detail="Analysis records do not have application status. Create an application first.",
    )
