from datetime import datetime

from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    analysis_id: str | None = None
    resume_id: str | None = None
    jd_id: str | None = None
    company: str = Field(min_length=1, max_length=255)
    role: str = Field(min_length=1, max_length=255)
    status: str = "planned"
    source: str | None = None
    job_url: str | None = None
    notes: str | None = None
    applied_at: datetime | None = None


class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=255)
    role: str | None = Field(default=None, min_length=1, max_length=255)
    status: str | None = None
    source: str | None = None
    job_url: str | None = None
    notes: str | None = None
    applied_at: datetime | None = None


class ApplicationRecord(BaseModel):
    id: str
    analysis_id: str | None
    resume_id: str | None
    jd_id: str | None
    company: str
    role: str
    status: str
    source: str | None
    job_url: str | None
    notes: str | None
    applied_at: datetime | None
    created_at: datetime
    updated_at: datetime
    score: str | None = None
    match: str | None = None
    resume_used: str | None = None
    gaps: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class ApplicationListResponse(BaseModel):
    applications: list[ApplicationRecord]
