import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
LLM_MODEL = os.environ.get("LLM_MODEL")
LLM_MAX_TOKENS    = os.environ.get("LLM_MAX_TOKENS")

#storage
UPLOADED_DIRS = "uploaded_files"
RESUMES_FILE  = "resumes.json"
RESULTS_FILE  = "results.json"

# Database
DATABASE_URL = os.environ.get("DATABASE_URL")

# Application
VALID_STATUSES = ["planned", "applied", "oa", "interviewing", "offer", "rejected", "ghosted", "withdrawn"]
STALE_DAYS     = 14
