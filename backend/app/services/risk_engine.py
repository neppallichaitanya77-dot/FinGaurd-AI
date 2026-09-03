"""Risk engine: converts financial indicators into a risk score, risk level,
explainable risk factors, and a financial-health score.

Explanations are derived from the actual indicator values (not fabricated),
which keeps the results explainable and auditable.
"""
from typing import Dict, List

from app.core.config import get_settings
from app.ml.predict import predict_distress_probability

settings = get_settings()


def risk_level_from_score(score: int) -> str:
    """Map a 0-100 risk score to a level using configurable thresholds."""
    if score <= settings.RISK_LOW_MEDIUM:
        return "LOW"
    if score <= settings.RISK_MEDIUM_HIGH:
        return "MEDIUM"
    if score <= settings.RISK_HIGH_CRITICAL:
        return "HIGH"
    return "CRITICAL"


def _build_factors(indicators: Dict) -> List[Dict]:
    """Build explainable risk factors from indicator values."""
    factors: List[Dict] = []

    utilization = indicators.get("credit_utilization", 0)
    if utilization > 60:
        factors.append(
            {
                "name": "Credit Utilization",
                "value": f"{utilization:.0f}%",
                "impact": "HIGH",
            }
        )
    elif utilization > 30:
        factors.append(
            {
                "name": "Credit Utilization",
                "value": f"{utilization:.0f}%",
                "impact": "MEDIUM",
            }
        )

    balance_trend = indicators.get("balance_trend", "STABLE")
    if balance_trend == "DECLINING":
        factors.append(
            {"name": "Balance Trend", "value": "DECLINING", "impact": "MEDIUM"}
        )
    elif balance_trend == "INCREASING":
        factors.append(
            {"name": "Balance Trend", "value": "INCREASING", "impact": "LOW"}
        )

    dti = indicators.get("dti", 0)
    if dti > 50:
        factors.append(
            {"name": "Debt-to-Income Ratio", "value": f"{dti:.0f}%", "impact": "HIGH"}
        )
    elif dti > 35:
        factors.append(
            {"name": "Debt-to-Income Ratio", "value": f"{dti:.0f}%", "impact": "MEDIUM"}
        )

    delay_freq = indicators.get("payment_delay_frequency", 0)
    if delay_freq > 0.2:
        factors.append(
            {
                "name": "Payment Delays",
                "value": f"{delay_freq * 100:.0f}%",
                "impact": "HIGH",
            }
        )
    elif delay_freq > 0:
        factors.append(
            {"name": "Payment Delays", "value": f"{delay_freq * 100:.0f}%", "impact": "MEDIUM"}
        )

    expense_trend = indicators.get("expense_trend", 0)
    if expense_trend > 15:
        factors.append(
            {"name": "Expense Trend", "value": f"+{expense_trend:.0f}%", "impact": "MEDIUM"}
        )

    upcoming_emi = indicators.get("upcoming_emi", 0)
    if upcoming_emi > 0:
        factors.append(
            {"name": "Upcoming EMI", "value": f"₹{upcoming_emi:,.0f}", "impact": "MEDIUM"}
        )

    return factors


def score_risk(indicators: Dict) -> Dict:
    """Compute risk score, level, factors, and financial health score."""
    probability = predict_distress_probability(indicators)
    # Combine ML probability with heuristic penalties so scores are stable and explainable.
    utilization = min(indicators.get("credit_utilization", 0) / 100, 1.0)
    dti = min(indicators.get("dti", 0) / 100, 1.0)
    delay_freq = min(indicators.get("payment_delay_frequency", 0), 1.0)

    heuristic = (0.35 * utilization + 0.30 * dti + 0.35 * delay_freq) * 100
    risk_score = int(round(0.6 * (probability * 100) + 0.4 * heuristic))
    risk_score = max(0, min(100, risk_score))

    level = risk_level_from_score(risk_score)
    factors = _build_factors(indicators)
    health_score = max(0, min(100, 100 - risk_score))

    return {
        "risk_score": risk_score,
        "risk_level": level,
        "probability": round(probability, 3),
        "risk_factors": factors,
        "financial_health_score": health_score,
    }
