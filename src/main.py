from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.dashboard.router import router as dashboard_router
from src.resumes.router import router as resumes_router
from src.analyses.router import router as applications_router

app = FastAPI(title="Job Hunt Agent")

app.include_router(dashboard_router)
app.include_router(resumes_router)
app.include_router(applications_router)

app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default dev port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

@app.get("/health")
async def health():
    return {"status": "ok"}
