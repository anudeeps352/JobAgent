from datetime import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("analysis_id", name="uq_applications_analysis_id"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    analysis_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("analyses.id"), nullable=True
    )
    resume_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("resumes.id"), nullable=True
    )
    jd_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("job_descriptions.id"), nullable=True
    )
    company: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="planned")
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    job_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    analysis = relationship("Analysis", back_populates="application")
    resume = relationship("Resume")
    job_description = relationship("JobDescription")
