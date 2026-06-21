import json
import uuid
import hashlib
import re
import os
from datetime import datetime

RESULTS_FILE = "results.json"

def compute_jd_hash(jd_text):
    normalized = jd_text.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)
    return hashlib.sha256(normalized.encode()).hexdigest()

def load_all():
    if not os.path.exists(RESULTS_FILE):
        return []
    with open(RESULTS_FILE, "r") as f:
        return json.load(f)

def check_duplicate(jd_hash):
    records = load_all()
    for record in records:
        if record["jd_hash"] == jd_hash:
            return record
    return None

def save(jd_text, resume_path, analysis, company_override=None):
    record = {
        "id":            str(uuid.uuid4()),
        "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "jd_hash":       compute_jd_hash(jd_text),
        "jd_text":       jd_text,
        "company":       company_override or analysis["company"],
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

    print(f"\n✅ Saved — ID: {record['id']}")
    return record

def print_history():
    records = load_all()
    if not records:
        print("No records yet.")
        return

    print(f"\n{'─' * 60}")
    for r in records:
        print(f"Date:    {r['timestamp']}")
        print(f"Company: {r['company']} | Role: {r['role']}")
        print(f"Match:   {r['match']} | Score: {r['score']} | Status: {r['status']}")
        print(f"ID:      {r['id']}")
        print(f"{'─' * 60}")