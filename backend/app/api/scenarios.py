import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.config import get_settings
from app.models.risk import ScenarioPrediction
from app.models.user import User
from app.schemas.ai import ScenarioInput, ScenarioOutput
from app.services.risk_engine import score_risk, risk_level_from_score
from app.services.recommendation_engine import build_recommendations

router = APIRouter(prefix="/scenario", tags=["Scenario Simulator"])

settings = get_settings()


@router.post("/analyze", response_model=ScenarioOutput, summary="Analyze a simulated scenario")
def analyze_scenario(
    payload: ScenarioInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Same indicator structure the risk engine expects.
    indicators = {
        "dti": (payload.upcoming_emi / payload.monthly_income) * 100 if payload.monthly_income else 0,
        "credit_utilization": payload.credit_utilization,
        "payment_delay_frequency": min(payload.payment_delays / 6.0, 1.0),
        "debt_growth": 0.0,
        "expense_trend": max((payload.monthly_expenses - payload.monthly_income * 0.6) / (payload.monthly_income * 0.6) * 100, 0),
        "overdraft_frequency": payload.payment_delays,
        "repayment_consistency": max(1.0 - min(payload.payment_delays / 12.0, 1.0), 0),
        "total_debt": payload.outstanding_debt,
        "upcoming_emi": payload.upcoming_emi,
        "account_balance": payload.monthly_income * 2.5,
        "monthly_income": payload.monthly_income,
    }

    result = score_risk(indicators)

    # Build recommendations from the scenario indicators
    rec_descriptors = build_recommendations(indicators)

    output = {
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "financial_health_score": result["financial_health_score"],
        "risk_factors": result["risk_factors"],
        "recommendations": [r["title"] for r in rec_descriptors],
    }

    db.add(
        ScenarioPrediction(
            user_id=current_user.id,
            input_json=json.dumps(payload.model_dump()),
            risk_score=output["risk_score"],
            risk_level=output["risk_level"],
            financial_health_score=output["financial_health_score"],
        )
    )
    db.commit()

    return output
