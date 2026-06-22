import os
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

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