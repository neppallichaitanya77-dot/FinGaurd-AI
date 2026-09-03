from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.domain import RiskScoreOut
from app.services import user_finance_service

router = APIRouter(prefix="/risk-score", tags=["Risk"])


@router.get("", response_model=RiskScoreOut, summary="Get current risk score")
def get_risk_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    indicators = user_finance_service.get_indicators(db, current_user.id)
    result = user_finance_service.get_risk_summary(db, current_user.id, indicators)
    return result
