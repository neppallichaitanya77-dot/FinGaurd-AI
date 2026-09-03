"""Early-warning / intervention engine.

Generates supportive early-warning alerts based on the customer's actual
indicators. The intent is to help, never to punish or threaten.
"""
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.risk import Alert


def evaluate_intervention(indicators: Dict) -> List[Dict]:
    """Return a list of alert descriptors based on indicator values."""
    alerts: List[Dict] = []

    balance_trend = indicators.get("balance_trend", "STABLE")
    utilization = indicators.get("credit_utilization", 0)
    upcoming_emi = indicators.get("upcoming_emi", 0)
    delay_freq = indicators.get("payment_delay_frequency", 0)
    expense_trend = indicators.get("expense_trend", 0)
    debt_growth = indicators.get("debt_growth", 0)
    account_balance = indicators.get("account_balance", 0)

    # Combination scenario: declining balance + high utilization + upcoming EMI
    if (
        balance_trend == "DECLINING"
        and utilization > 40
        and upcoming_emi > 0
        and account_balance < (upcoming_emi * 3)
    ):
        alerts.append(
            {
                "title": "Possible Financial Pressure",
                "key": "pressure_combination",
                "description": (
                    "Your balance is decreasing while credit utilization is increasing, "
                    "and an EMI is approaching. Would you like to review your options?"
                ),
                "severity": "high",
                "recommended_action": "Review your cash flow and available balance before the payment date.",
            }
        )

    if utilization > 60:
        alerts.append(
            {
                "title": "High Credit Utilization",
                "key": "high_utilization",
                "description": f"Your credit utilization is at {utilization:.0f}%, above the recommended 30% threshold.",
                "severity": "high",
                "recommended_action": "Aim to reduce utilization below 30% for better financial health.",
            }
        )
    elif utilization > 40:
        alerts.append(
            {
                "title": "Elevated Credit Utilization",
                "key": "utilization_elevated",
                "description": f"Your credit utilization has increased to {utilization:.0f}%.",
                "severity": "medium",
                "recommended_action": "Review discretionary spending and consider prioritizing high-cost debt.",
            }
        )

    if balance_trend == "DECLINING":
        alerts.append(
            {
                "title": "Declining Account Balance",
                "key": "balance_declining",
                "description": "Your account balance has been declining over the past period.",
                "severity": "medium",
                "recommended_action": "Review income vs. expense patterns to identify adjustment areas.",
            }
        )

    if upcoming_emi > 0 and account_balance < (upcoming_emi * 2):
        alerts.append(
            {
                "title": "Upcoming EMI Pressure",
                "key": "emi_pressure",
                "description": (
                    f"Your upcoming EMI of ₹{upcoming_emi:,.0f} may reduce your available "
                    "balance significantly."
                ),
                "severity": "medium",
                "recommended_action": "Plan for the EMI payment and review upcoming cash needs.",
            }
        )

    if delay_freq > 0:
        alerts.append(
            {
                "title": "Payment Delay Detected",
                "key": "payment_delay",
                "description": f"Payment delays represent {delay_freq * 100:.0f}% of recent payments.",
                "severity": "medium",
                "recommended_action": "Set up automatic payments to avoid future delays.",
            }
        )

    if expense_trend > 15:
        alerts.append(
            {
                "title": "Increasing Monthly Expenses",
                "key": "expense_increasing",
                "description": f"Your monthly expenses are up {expense_trend:.0f}% compared with recent months.",
                "severity": "medium",
                "recommended_action": "Review spending categories to find potential savings.",
            }
        )

    if debt_growth > 5:
        alerts.append(
            {
                "title": "Increasing Debt",
                "key": "debt_growing",
                "description": "Your outstanding debt has been increasing over time.",
                "severity": "medium",
                "recommended_action": "Prioritize debt repayment to control future interest costs.",
            }
        )

    return alerts


UNIQUE_ALERT_TITLES = {
    "Possible Financial Pressure",
    "High Credit Utilization",
    "Elevated Credit Utilization",
    "Declining Account Balance",
    "Upcoming EMI Pressure",
    "Payment Delay Detected",
    "Increasing Monthly Expenses",
    "Increasing Debt",
}


def persist_active_alerts(
    db: Session, user_id: str, alert_descriptors: List[Dict]
) -> None:
    """Insert any new alerts into the DB, skipping ones already present & unread."""
    existing = (
        db.query(Alert)
        .filter(Alert.user_id == user_id, Alert.status == "unread")
        .all()
    )
    existing_titles = {a.title for a in existing}

    for descriptor in alert_descriptors:
        title = descriptor["title"]
        if title in existing_titles:
            continue
        alert = Alert(
            user_id=user_id,
            title=title,
            description=descriptor["description"],
            severity=descriptor["severity"],
            recommended_action=descriptor.get("recommended_action"),
            status="unread",
        )
        db.add(alert)
    db.commit()
