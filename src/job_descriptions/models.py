from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from src.database import Base

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id:         Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    jd_hash:    Mapped[str] = mapped_column(String(64), unique=True, index=True)
    jd_text:    Mapped[str] = mapped_column(Text)
    company:    Mapped[str] = mapped_column(String(255))
    role:       Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    analyses: Mapped[list["Analysis"]] = relationship("Analysis", back_populates="job_description")