from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    resume_id: str
    jd_text: str

class ApplicationRecord(BaseModel):
    id: str
    timestamp: str
    company: str
    role: str
    match: str
    score: str
    status: str
    resume_used: str

class StatusUpdate(BaseModel):
    status: str