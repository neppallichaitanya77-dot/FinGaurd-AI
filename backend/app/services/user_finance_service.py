"""Service to assemble per-user financial context for the dashboard, health,
risk, alerts and recommendations."""
from typing import Dict

from sqlalchemy.orm import Session

from app.models.risk import Alert, Recommendation, RiskFactor, RiskScore
from app.services import financial_indicators as fi
from app.services.intervention_engine import evaluate_intervention, persist_active_alerts
from app.services.recommendation_engine import build_recommendations, persist_recommendations
from app.services.risk_engine import score_risk


def get_indicators(db: Session, user_id: str) -> Dict:
    return fi.compute_all_indicators(db, user_id)


def get_risk_summary(db: Session, user_id: str, indicators: Dict) -> Dict:
    result = score_risk(indicators)
    # Persist a RiskScore row and its factors for auditability
    risk_score_row = RiskScore(
        user_id=user_id,
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        probability=result["probability"],
        financial_health_score=result["financial_health_score"],
    )
    db.add(risk_score_row)
    db.flush()
    for f in result["risk_factors"]:
        db.add(
            RiskFactor(
                risk_score_id=risk_score_row.id,
                name=f["name"],
                value=f.get("value"),
                impact=f["impact"],
            )
        )
    db.commit()
    return result


def refresh_alerts(db: Session, user_id: str, indicators: Dict) -> int:
    descriptors = evaluate_intervention(indicators)
    persist_active_alerts(db, user_id, descriptors)
    return len(descriptors)


def refresh_recommendations(db: Session, user_id: str, indicators: Dict) -> int:
    descriptors = build_recommendations(indicators)
    persist_recommendations(db, user_id, descriptors)
    return len(descriptors)


def get_alerts(db: Session, user_id: str):
    return (
        db.query(Alert)
        .filter(Alert.user_id == user_id)
        .order_by(Alert.created_at.desc())
        .all()
    )


def get_recommendations(db: Session, user_id: str):
    return (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user_id)
        .order_by(Recommendation.created_at.desc())
        .all()
    )


def get_chart_data(db: Session, user_id: str) -> Dict:
    from datetime import datetime, timedelta

    txns = db.query(fi.Transaction).filter(fi.Transaction.user_id == user_id).all()
    balance = fi.get_balance(db, user_id)

    now = datetime.utcnow()
    days = 30
    balance_chart = []
    current = balance
    for transaction in sorted(txns, key=lambda item: item.date):
        balance_chart.append({
            "date": transaction.date.strftime("%Y-%m-%d"),
            "balance": round(transaction.balance, 0),
        })
    if not balance_chart or balance_chart[-1]["date"] != now.strftime("%Y-%m-%d"):
        balance_chart.append({"date": now.strftime("%Y-%m-%d"), "balance": round(balance, 0)})

    # Expense chart by month (last 5 months)
    expense_chart = {}
    for t in txns:
        month = t.date.strftime("%b")
        if month not in expense_chart:
            expense_chart[month] = {"income": 0, "expenses": 0}
        if t.transaction_type == "credit":
            expense_chart[month]["income"] += t.amount
        else:
            expense_chart[month]["expenses"] += abs(t.amount)
    expense_chart_list = [
        {"month": k, "income": round(v["income"], 0), "expenses": round(v["expenses"], 0)}
        for k, v in expense_chart.items()
    ]

    # Debt chart (outstanding debt flat/trend over time)
    debt = fi.get_total_debt(db, user_id)
    debt_chart = [{"date": (now - timedelta(days=i)).strftime("%Y-%m-%d"), "debt": round(debt, 0)} for i in range(days, -1, -1)]

    return {
        "balance_chart": balance_chart,
        "expense_chart": expense_chart_list,
        "debt_chart": debt_chart,
    }


def build_dashboard(db: Session, user_id: str) -> Dict:
    indicators = get_indicators(db, user_id)
    risk = get_risk_summary(db, user_id, indicators)
    refresh_alerts(db, user_id, indicators)
    refresh_recommendations(db, user_id, indicators)

    alerts = [a for a in get_alerts(db, user_id)]
    recommendations = get_recommendations(db, user_id)
    charts = get_chart_data(db, user_id)

    income = indicators["monthly_income"]
    expenses = max(income * 0.7, 0)
    balance = indicators["account_balance"]

    def alert_to_dict(a):
        return {
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "severity": a.severity,
            "status": a.status,
            "recommended_action": a.recommended_action,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }

    def rec_to_dict(r):
        return {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "priority": r.priority,
            "category": r.category,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }

    # Expenses: approximate from expense trend data if available
    chart_exp = charts["expense_chart"]
    if chart_exp:
        expenses = chart_exp[-1]["expenses"]

    return {
        "health_score": risk["financial_health_score"],
        "health_status": _health_status(risk["financial_health_score"]),
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "risk_factors": risk["risk_factors"],
        "balance": balance,
        "income": income,
        "expenses": expenses,
        "debt": indicators["total_debt"],
        "credit_utilization": indicators["credit_utilization"],
        "upcoming_emi": indicators["upcoming_emi"],
        "alerts": [alert_to_dict(a) for a in alerts[:5]],
        "recommendations": [rec_to_dict(r) for r in recommendations[:5]],
        "balance_chart": charts["balance_chart"],
        "expense_chart": charts["expense_chart"],
        "debt_chart": charts["debt_chart"],
    }


def _health_status(score: int) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 60:
        return "Fair"
    if score >= 40:
        return "Needs Attention"
    return "Concerning"
