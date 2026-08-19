from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.dashboard import service as dashboard_service
from src.dashboard.schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: Session = Depends(get_db)):
    return dashboard_service.get_summary(db)
