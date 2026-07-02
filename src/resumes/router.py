from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from src.database import get_db
from src.resumes import service
from src.resumes.exceptions import ResumeNotFoundException

router = APIRouter(prefix="/resumes", tags=["resumes"])

@router.get("")
async def get_resumes(db: Session = Depends(get_db)):
    return {"resumes": service.get_all(db)}

@router.get("/{filename}")
async def get_resume_file(filename: str):
    try:
        file_path = service.get_file_path(filename)
        return FileResponse(path=file_path, media_type="application/pdf", filename=filename)
    except ResumeNotFoundException:
        raise HTTPException(status_code=404, detail="File not found")

@router.post("")
async def upload_resume(file: UploadFile = File(...), label: str = "default", db: Session = Depends(get_db)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    try:
        contents = await file.read()
        service.save_to_disk(contents, file.filename)
        record = service.save_metadata(db, file.filename, label)
        return {"message": "File uploaded successfully", "resume": record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()