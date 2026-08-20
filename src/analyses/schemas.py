from pydantic import BaseModel, Field


class ApplicationRecord(BaseModel):
    id: str
    timestamp: str
    company: str
    role: str
    match: str
    score: str
    status: str | None = None
    resume_used: str
    gaps: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    full_analysis: str | None = None

class AnalyzeRequest(BaseModel):
    resume_id: str
    jd_text: str

class StatusUpdate(BaseModel):
    status: str


class HistoryResponse(BaseModel):
    history: list[ApplicationRecord]


class AnalysesResponse(BaseModel):
    analyses: list[ApplicationRecord]
