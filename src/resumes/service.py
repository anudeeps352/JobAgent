import os
import json
import uuid
import re
from datetime import datetime
import pymupdf
from src.config import UPLOADED_DIRS, RESUMES_FILE
from src.resumes.exceptions import ResumeNotFoundException

os.makedirs(UPLOADED_DIRS, exist_ok=True)

# ── disk ──────────────────────────────────────────────────────
def save_to_disk(contents: bytes, filename: str) -> str:
    """Save uploaded PDF bytes to disk, return file path"""
    file_path = os.path.join(UPLOADED_DIRS, filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    return file_path

def get_file_path(filename: str) -> str:
    """Return full path to resume file, raise if missing"""
    path = os.path.join(UPLOADED_DIRS, filename)
    if not os.path.exists(path):
        raise ResumeNotFoundException(filename)
    return path

# ── metadata ──────────────────────────────────────────────────
def save_metadata(filename: str, label: str) -> dict:
    """Save resume metadata to resumes.json, return record"""
    resumes = get_all()
    record = {
        "id":          str(uuid.uuid4()),
        "label":       label,
        "filename":    filename,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    resumes.append(record)
    with open(RESUMES_FILE, "w") as f:
        json.dump(resumes, f, indent=2)
    return record

def get_all() -> list:
    """Return all resume metadata records"""
    if not os.path.exists(RESUMES_FILE):
        return []
    with open(RESUMES_FILE, "r") as f:
        return json.load(f)

def get_by_id(resume_id: str) -> dict:
    """Find resume by ID, raise if not found"""
    for resume in get_all():
        if resume["id"] == resume_id:
            return resume
    raise ResumeNotFoundException(resume_id)

# ── extraction ────────────────────────────────────────────────
def extract_text(file_path: str) -> str:
    """Extract and clean text from resume PDF"""
    doc = pymupdf.open(file_path)
    raw = "\n".join(page.get_text() for page in doc)
    return _clean(raw)

def _clean(text: str) -> str:
    """Remove noise from extracted PDF text"""
    # remove phone numbers
    text = re.sub(r'[\+\(]?[0-9][0-9\s\-\(\)]{7,}[0-9]', '', text)
    # remove emails
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    # remove URLs
    text = re.sub(r'(https?://\S+|www\.\S+|[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}/\S+)', '', text)
    # remove divider lines
    text = re.sub(r'[_\-=]{3,}', '', text)
    # collapse excess blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # strip whitespace per line
    text = "\n".join(line.strip() for line in text.splitlines())
    return text.strip()