from fastapi import FastAPI
from src.resumes.router import router as resumes_router
from src.applications.router import router as applications_router

app = FastAPI(title="Job Hunt Agent")

app.include_router(resumes_router)
app.include_router(applications_router)

@app.get("/health")
async def health():
    return {"status": "ok"}