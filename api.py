import os
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from extract_and_clean import extract_resume
from llm import analyze as run_analysis
from storage import save as save_analysis,load_all
from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    resume_id: str
    jd_text: str

app = FastAPI()


RESUMES_FILE = "resumes.json"

def save_resume_metadata(filename, label):
    if os.path.exists(RESUMES_FILE):
        with open(RESUMES_FILE, "r") as f:
            resumes = json.load(f)
    else:
        resumes = []

    record = {
        "id": str(uuid.uuid4()),
        "label": label,
        "filename": filename,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    resumes.append(record)

    with open(RESUMES_FILE, "w") as f:
        json.dump(resumes, f, indent=2)

    return record

UPLOADED_DIRS = 'uploaded_files'
os.makedirs(UPLOADED_DIRS, exist_ok=True)


@app.get("/resume")
async def get_resume():
    if not os.path.exists(RESUMES_FILE):
        return {"resumes": []}
    with open(RESUMES_FILE, "r") as f:
        resumes = json.load(f)
    return {"resumes": resumes}

@app.get("/resume/{filename}")
async def get_resume_file(filename: str):
    file_path = os.path.join(UPLOADED_DIRS,filename)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )
    return FileResponse(path=file_path, media_type="application/pdf",filename=filename)

@app.post("/resume")
async def upload_resume(file: UploadFile = File(...), label: str = "default"):
    if(file.content_type != "application/pdf"):
       raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only PDF files are allowed."
        )
    #define file path
    file_path = os.path.join(UPLOADED_DIRS, file.filename)

    #write file to disk safely
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error occurred while uploading the file."
        )
    finally:
        # close the file even if an exception or success occurs
        file.file.close()
    record = save_resume_metadata(file.filename, label)
    return {"message": "File uploaded successfully", "resume": record}


# Takes as input resume uuid and job jd
# Check in resume.json if it exists, if not return error
# if yes then build a path to file and call extract resume function to extract text from pdf
# then call analyze function to analyze the text and return the result
@app.post("/analyze")
async def analyze_resume(request: AnalyzeRequest):

    with open(RESUMES_FILE, "r") as f:
        resumes = json.load(f)
        try:
            resume_record = next(resume for resume in resumes if resume["id"] == request.resume_id)
        except StopIteration:
            raise HTTPException(
                status_code=404,
                detail="Resume not found."
            )
    RESUME_PATH = os.path.join(UPLOADED_DIRS, resume_record["filename"])
    if not os.path.exists(RESUME_PATH):
        raise HTTPException(
            status_code=404,
            detail="Resume file not found."
        )
    
    resume_text = extract_resume(RESUME_PATH)
    resume_analysis = run_analysis(request.jd_text, resume_text)
    save_analysis(request.jd_text, RESUME_PATH, resume_analysis)
    return resume_analysis 

@app.get("/history")
async def get_history():
    records = load_all()
    return {"history": records}