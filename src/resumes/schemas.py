from pydantic import BaseModel
from datetime import datetime

class ResumeRecord(BaseModel):
    id: str
    label: str
    filename: str
    uploaded_at: str

class ResumeUploadResponse(BaseModel):
    message: str
    resume: ResumeRecord