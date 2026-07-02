from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from src.database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id:            Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id:     Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("resumes.id"))
    jd_id:         Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("job_descriptions.id"))
    match:         Mapped[str] = mapped_column(String(20))
    score:         Mapped[str] = mapped_column(String(50))
    full_analysis: Mapped[str] = mapped_column(Text)
    status:        Mapped[str | None] = mapped_column(String(50), nullable=True)
    analyzed_at:   Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    resume:          Mapped["Resume"] = relationship("Resume", back_populates="analyses")
    job_description: Mapped["JobDescription"] = relationship("JobDescription", back_populates="analyses")