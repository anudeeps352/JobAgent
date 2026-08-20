from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.analyses.models import Analysis
from src.applications import service
from src.applications.models import Application
from src.applications.schemas import (
    ApplicationCreate,
    ApplicationListResponse,
    ApplicationRecord,
    ApplicationUpdate,
)
from src.database import get_db
from src.job_descriptions.models import JobDescription
from src.resumes.models import Resume

router = APIRouter(prefix="/applications", tags=["applications"])


def serialize_application(record: Application) -> ApplicationRecord:
    analysis = record.analysis
    resume = record.resume or (analysis.resume if analysis else None)
    return ApplicationRecord(
        id=record.id,
        analysis_id=record.analysis_id,
        resume_id=record.resume_id,
        jd_id=record.jd_id,
        company=record.company,
        role=record.role,
        status=record.status,
        source=record.source,
        job_url=record.job_url,
        notes=record.notes,
        applied_at=record.applied_at,
        created_at=record.created_at,
        updated_at=record.updated_at,
        score=analysis.score if analysis else None,
        match=analysis.match if analysis else None,
        resume_used=resume.filename if resume else None,
        gaps=(analysis.gaps if analysis else []) or [],
        suggestions=(analysis.suggestions if analysis else []) or [],
    )


@router.get("", response_model=ApplicationListResponse)
async def get_applications(db: Session = Depends(get_db)):
    return {"applications": [serialize_application(item) for item in service.get_all(db)]}


@router.post("", response_model=ApplicationRecord, status_code=201)
async def create_application(request: ApplicationCreate, db: Session = Depends(get_db)):
    try:
        service.validate_status(request.status)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    analysis = None
    if request.analysis_id:
        analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        existing = db.query(Application).filter(Application.analysis_id == analysis.id).first()
        if existing:
            return serialize_application(service.get_by_id(db, existing.id))

    resume_id = request.resume_id or (analysis.resume_id if analysis else None)
    jd_id = request.jd_id or (analysis.jd_id if analysis else None)

    if resume_id and not db.query(Resume).filter(Resume.id == resume_id).first():
        raise HTTPException(status_code=404, detail="Resume not found")
    if jd_id and not db.query(JobDescription).filter(JobDescription.id == jd_id).first():
        raise HTTPException(status_code=404, detail="Job description not found")

    record = Application(
        analysis_id=analysis.id if analysis else None,
        resume_id=resume_id,
        jd_id=jd_id,
        company=request.company,
        role=request.role,
        status=request.status,
        source=request.source,
        job_url=request.job_url,
        notes=request.notes,
        applied_at=request.applied_at,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return serialize_application(service.get_by_id(db, record.id))


@router.patch("/{application_id}", response_model=ApplicationRecord)
async def update_application(
    application_id: str, request: ApplicationUpdate, db: Session = Depends(get_db)
):
    record = service.get_by_id(db, application_id)
    if not record:
        raise HTTPException(status_code=404, detail="Application not found")

    values = request.model_dump(exclude_unset=True)
    if "status" in values:
        try:
            service.validate_status(values["status"])
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
    for field, value in values.items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return serialize_application(service.get_by_id(db, record.id))
