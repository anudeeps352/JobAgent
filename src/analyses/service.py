import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from src.analyses.models import Analysis
from src.analyses.exceptions import AnalysisNotFoundException, InvalidStatusException
from src.config import VALID_STATUSES

def create(db: Session, resume_id: str, jd_id: str, analysis: dict) -> Analysis:
    record = Analysis(
        id=str(uuid.uuid4()),
        resume_id=resume_id,
        jd_id=jd_id,
        match=analysis["match"],
        score=analysis["score"],
        gaps=analysis.get("gaps", []),
        suggestions=analysis.get("suggestions", []),
        full_analysis=analysis["full_analysis"],
        status="applied",
        analyzed_at=datetime.now()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_all(db: Session) -> list[Analysis]:
    return db.query(Analysis).options(
        joinedload(Analysis.resume),
        joinedload(Analysis.job_description),
    ).order_by(Analysis.analyzed_at.desc()).all()

def get_by_resume_and_jd(db: Session, resume_id: str, jd_id: str) -> Analysis | None:
    return db.query(Analysis).filter(
        Analysis.resume_id == resume_id,
        Analysis.jd_id == jd_id,
    ).first()

def get_by_id(db: Session, analysis_id: str) -> Analysis:
    record = db.query(Analysis).options(
        joinedload(Analysis.resume),
        joinedload(Analysis.job_description),
    ).filter(Analysis.id == analysis_id).first()
    if not record:
        raise AnalysisNotFoundException(analysis_id)
    return record

def update_status(db: Session, analysis_id: str, new_status: str) -> Analysis:
    if new_status not in VALID_STATUSES:
        raise InvalidStatusException(new_status)
    record = get_by_id(db, analysis_id)
    record.status = new_status
    db.commit()
    db.refresh(record)
    return record
