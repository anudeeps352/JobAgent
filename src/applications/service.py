from sqlalchemy.orm import Session, joinedload

from src.applications.models import Application
from src.config import VALID_STATUSES


def get_all(db: Session) -> list[Application]:
    return (
        db.query(Application)
        .options(
            joinedload(Application.analysis),
            joinedload(Application.resume),
            joinedload(Application.job_description),
        )
        .order_by(Application.created_at.desc())
        .all()
    )


def get_by_id(db: Session, application_id: str) -> Application | None:
    return (
        db.query(Application)
        .options(
            joinedload(Application.analysis),
            joinedload(Application.resume),
            joinedload(Application.job_description),
        )
        .filter(Application.id == application_id)
        .first()
    )


def validate_status(status: str) -> None:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}. Choose from {VALID_STATUSES}")
