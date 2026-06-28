import json
import uuid
import hashlib
import re
import os
from datetime import datetime
from src.config import RESULTS_FILE, VALID_STATUSES
from src.applications.exceptions import (
    DuplicateJDException,
    ApplicationNotFoundException,
    InvalidStatusException
)

def compute_jd_hash(jd_text: str) -> str:
    normalized = jd_text.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)
    return hashlib.sha256(normalized.encode()).hexdigest()

def load_all() -> list:
    if not os.path.exists(RESULTS_FILE):
        return []
    with open(RESULTS_FILE, "r") as f:
        return json.load(f)

def check_duplicate(jd_hash: str) -> dict | None:
    for record in load_all():
        if record["jd_hash"] == jd_hash:
            return record
    return None

def save(jd_text: str, resume_path: str, analysis: dict, force: bool = False) -> dict:
    jd_hash = compute_jd_hash(jd_text)
    existing = check_duplicate(jd_hash)

    if existing and not force:
        raise DuplicateJDException(
            existing["company"],
            existing["role"],
            existing["timestamp"]
        )

    record = {
        "id":            str(uuid.uuid4()),
        "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "jd_hash":       jd_hash,
        "jd_text":       jd_text,
        "company":       analysis["company"],
        "role":          analysis["role"],
        "resume_used":   resume_path,
        "match":         analysis["match"],
        "score":         analysis["score"],
        "full_analysis": analysis["full_analysis"],
        "status":        "applied"
    }

    records = load_all()
    records.append(record)
    with open(RESULTS_FILE, "w") as f:
        json.dump(records, f, indent=2)

    return record

def update_status(record_id: str, new_status: str) -> dict:
    if new_status not in VALID_STATUSES:
        raise InvalidStatusException(new_status)

    records = load_all()
    for record in records:
        if record["id"] == record_id:
            record["status"] = new_status
            with open(RESULTS_FILE, "w") as f:
                json.dump(records, f, indent=2)
            return record

    raise ApplicationNotFoundException(record_id)