from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.modules.auth import models as auth_models
from backend.app.modules.auth.dependencies import get_current_user
from backend.app.modules.finance.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/metrics")
def get_metrics(
    account_id: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    current_user: auth_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_summary_metrics(
        db, 
        str(current_user.tenant_id), 
        user_role=current_user.role,
        account_id=account_id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/forecast")
def get_forecast(
    days: int = 30,
    account_id: str = None,
    current_user: auth_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_balance_forecast(
        db, 
        str(current_user.tenant_id), 
        days=days,
        account_id=account_id
    )
