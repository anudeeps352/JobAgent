from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from src.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id:          Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    label:       Mapped[str] = mapped_column(String(100))
    filename:    Mapped[str] = mapped_column(String(255))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    analyses: Mapped[list["Analysis"]] = relationship("Analysis", back_populates="resume")