"""Personalized recommendation engine.

Recommendations are supportive suggestions derived from actual indicators.
They are never mandatory and never punitive.
"""
from typing import Dict, List

from sqlalchemy.orm import Session

from app.models.risk import Recommendation


def build_recommendations(indicators: Dict) -> List[Dict]:
    """Return recommendation descriptors based on the customer's indicators."""
    recs: List[Dict] = []
    utilization = indicators.get("credit_utilization", 0)
    upcoming_emi = indicators.get("upcoming_emi", 0)
    delay_freq = indicators.get("payment_delay_frequency", 0)
    expense_trend = indicators.get("expense_trend", 0)
    account_balance = indicators.get("account_balance", 0)

    if utilization > 60:
        recs.append(
            {
                "title": "Reduce Credit Utilization",
                "description": "Your current utilization is relatively high. Review discretionary spending and consider prioritizing high-cost debt.",
                "priority": "high",
                "category": "Debt Management",
            }
        )
    elif utilization > 30:
        recs.append(
            {
                "title": "Monitor Credit Utilization",
                "description": "Your utilization is moderate. Keeping it below 30% can improve your financial health.",
                "priority": "medium",
                "category": "Debt Management",
            }
        )

    if upcoming_emi > 0:
        if account_balance < upcoming_emi * 2:
            recs.append(
                {
                    "title": "Plan Your Upcoming EMI",
                    "description": "Your next EMI may place pressure on your balance. Review your cash flow and plan accordingly.",
                    "priority": "high",
                    "category": "Cash Flow",
                }
            )
        else:
            recs.append(
                {
                    "title": "EMI Payment Planning",
                    "description": "Your upcoming EMI is due soon. Setting up a reminder can help keep payments on schedule.",
                    "priority": "medium",
                    "category": "Cash Flow",
                }
            )

    if expense_trend > 10:
        recs.append(
            {
                "title": "Budget Planning",
                "description": "Your monthly expenses increased compared with recent months. Creating a budget can help manage spending.",
                "priority": "medium",
                "category": "Budgeting",
            }
        )

    if delay_freq > 0:
        recs.append(
            {
                "title": "Avoid Payment Delays",
                "description": "Consider automatic payments to reduce the chance of missing due dates.",
                "priority": "high",
                "category": "Repayment",
            }
        )

    recs.append(
        {
            "title": "Build an Emergency Fund",
            "description": "An emergency fund covering 3-6 months of expenses can be a strong safety net.",
            "priority": "medium",
            "category": "Savings",
        }
    )

    return recs


def persist_recommendations(
    db: Session, user_id: str, rec_descriptors: List[Dict]
) -> None:
    existing = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user_id)
        .all()
    )
    existing_titles = {r.title for r in existing}

    for rec in rec_descriptors:
        if rec["title"] in existing_titles:
            continue
        db.add(
            Recommendation(
                user_id=user_id,
                title=rec["title"],
                description=rec["description"],
                priority=rec["priority"],
                category=rec["category"],
                status="pending",
            )
        )
    db.commit()
