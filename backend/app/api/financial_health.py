from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.domain import FinancialHealthOut
from app.services import user_finance_service

router = APIRouter(prefix="/financial-health", tags=["Financial Health"])


@router.get("", response_model=FinancialHealthOut, summary="Get financial health score")
def get_financial_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    indicators = user_finance_service.get_indicators(db, current_user.id)
    risk = user_finance_service.score_risk(indicators)
    score = risk["financial_health_score"]

    positive = []
    concerns = []

    if indicators["repayment_consistency"] >= 0.9:
        positive.append("Consistent payment behaviour")
    if indicators["credit_utilization"] <= 30:
        positive.append("Healthy credit utilization")
    if indicators["balance_trend"] == "INCREASING":
        positive.append("Rising account balance")
    if indicators["dti"] <= 35:
        positive.append("Manageable debt-to-income ratio")
    if not positive:
        positive.append("Active financial monitoring with FinGuard AI")

    if indicators["credit_utilization"] > 40:
        concerns.append("Credit utilization is above the recommended level")
    if indicators["balance_trend"] == "DECLINING":
        concerns.append("Account balance is declining")
    if indicators["upcoming_emi"] > 0:
        concerns.append("Upcoming EMI obligations")
    if indicators["expense_trend"] > 10:
        concerns.append("Monthly expenses are trending upward")
    if not concerns:
        concerns.append("No significant concerns detected")

    charts = user_finance_service.get_chart_data(db, current_user.id)
    status_str = (
        "Excellent"
        if score >= 80
        else "Good"
        if score >= 70
        else "Fair"
        if score >= 60
        else "Needs Attention"
    )

    income = indicators["monthly_income"]
    expenses = max(income * 0.7, 0)
    chart_exp = charts.get("expense_chart", [])
    if chart_exp:
        expenses = chart_exp[-1]["expenses"]

    return {
        "financial_health_score": score,
        "financial_health_status": status_str,
        "health_score": score,
        "health_status": status_str,
        "key_positive_factors": positive,
        "positive_factors": positive,
        "key_concerns": concerns,
        "concerns": concerns,
        "balance": indicators["account_balance"],
        "income": income,
        "expenses": expenses,
        "debt": indicators["total_debt"],
        "credit_utilization": round(indicators["credit_utilization"], 1),
        "upcoming_emi": indicators["upcoming_emi"],
        "balance_chart": charts.get("balance_chart", []),
        "expense_chart": charts.get("expense_chart", []),
        "debt_chart": charts.get("debt_chart", []),
    }
