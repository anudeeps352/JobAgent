import uuid
import hashlib
import re
from datetime import datetime
from sqlalchemy.orm import Session
from src.job_descriptions.models import JobDescription

def compute_jd_hash(jd_text: str) -> str:
    normalized = jd_text.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)
    return hashlib.sha256(normalized.encode()).hexdigest()

def get_by_hash(db: Session, jd_hash: str) -> JobDescription | None:
    return db.query(JobDescription).filter(JobDescription.jd_hash == jd_hash).first()

def create(db: Session, jd_text: str, company: str, role: str) -> JobDescription:
    record = JobDescription(
        id=str(uuid.uuid4()),
        jd_hash=compute_jd_hash(jd_text),
        jd_text=jd_text,
        company=company,
        role=role,
        created_at=datetime.now()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record