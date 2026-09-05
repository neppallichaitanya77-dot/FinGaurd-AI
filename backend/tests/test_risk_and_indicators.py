import pytest
from app.services.financial_indicators import (
    compute_dti,
    compute_credit_utilization,
    compute_payment_delay_frequency,
    classify_balance_trend,
    compute_expense_trend,
)
from app.services.risk_engine import score_risk, risk_level_from_score
from app.services.intervention_engine import evaluate_intervention
from app.services.recommendation_engine import build_recommendations
from app.services.financial_indicators import get_monthly_expenses, get_monthly_income


def test_compute_dti():
    assert compute_dti(15000, 50000) == 30.0
    assert compute_dti(0, 50000) == 0.0
    assert compute_dti(10000, 0) == 0.0  # Zero division guard


def test_compute_credit_utilization():
    assert compute_credit_utilization(25000, 100000) == 25.0
    assert compute_credit_utilization(0, 100000) == 0.0
    assert compute_credit_utilization(50000, 0) == 0.0  # Zero division guard


def test_compute_payment_delay_frequency():
    assert compute_payment_delay_frequency(2, 20) == 0.1
    assert compute_payment_delay_frequency(0, 20) == 0.0
    assert compute_payment_delay_frequency(5, 0) == 0.0  # Zero division guard


def test_classify_balance_trend():
    assert classify_balance_trend([50000, 52000, 58000]) == "INCREASING"
    assert classify_balance_trend([60000, 55000, 48000]) == "DECLINING"
    assert classify_balance_trend([50000, 50100, 50200]) == "STABLE"
    assert classify_balance_trend([]) == "STABLE"
    assert classify_balance_trend([50000]) == "STABLE"


def test_compute_expense_trend():
    assert compute_expense_trend(30000, 20000) == 50.0
    assert compute_expense_trend(20000, 20000) == 0.0
    assert compute_expense_trend(15000, 0) == 0.0  # Zero division guard


def test_monthly_totals_are_derived_from_transactions(db_session):
    from datetime import datetime
    from app.models.finance import Transaction

    user_id = "calculation-user"
    db_session.add_all([
        Transaction(user_id=user_id, date=datetime.utcnow(), description="Income", category="Income", amount=45000, transaction_type="credit", balance=45000),
        Transaction(user_id=user_id, date=datetime.utcnow(), description="Expense", category="Food", amount=-20000, transaction_type="debit", balance=25000),
    ])
    db_session.flush()

    assert get_monthly_income(db_session, user_id) == 45000
    assert get_monthly_expenses(db_session, user_id) == 20000


def test_risk_level_from_score():
    assert risk_level_from_score(20) == "LOW"
    assert risk_level_from_score(45) == "MEDIUM"
    assert risk_level_from_score(75) == "HIGH"
    assert risk_level_from_score(95) == "CRITICAL"


def test_score_risk_healthy():
    indicators = {
        "dti": 15.0,
        "credit_utilization": 20.0,
        "payment_delay_frequency": 0.0,
        "balance_trend": "INCREASING",
        "debt_growth": 0.0,
        "expense_trend": -5.0,
        "overdraft_frequency": 0,
        "repayment_consistency": 1.0,
        "total_debt": 50000,
        "upcoming_emi": 5000,
        "account_balance": 120000,
        "monthly_income": 60000,
    }
    result = score_risk(indicators)
    assert 0 <= result["risk_score"] <= 100
    assert result["risk_level"] in ["LOW", "MEDIUM"]
    assert result["financial_health_score"] >= 60
    assert "probability" in result


def test_score_risk_distressed():
    indicators = {
        "dti": 65.0,
        "credit_utilization": 85.0,
        "payment_delay_frequency": 0.35,
        "balance_trend": "DECLINING",
        "debt_growth": 25.0,
        "expense_trend": 30.0,
        "overdraft_frequency": 3,
        "repayment_consistency": 0.65,
        "total_debt": 800000,
        "upcoming_emi": 35000,
        "account_balance": 15000,
        "monthly_income": 40000,
    }
    result = score_risk(indicators)
    assert result["risk_score"] > 50
    assert result["risk_level"] in ["HIGH", "CRITICAL"]
    assert len(result["risk_factors"]) > 0


def test_evaluate_intervention():
    # Combination scenario: declining balance + high utilization + upcoming EMI
    indicators = {
        "balance_trend": "DECLINING",
        "credit_utilization": 65.0,
        "upcoming_emi": 15000,
        "account_balance": 25000,
        "payment_delay_frequency": 0.1,
        "expense_trend": 20.0,
        "debt_growth": 10.0,
    }
    alerts = evaluate_intervention(indicators)
    assert len(alerts) > 0
    titles = [a["title"] for a in alerts]
    assert "Possible Financial Pressure" in titles
    assert "High Credit Utilization" in titles


def test_build_recommendations():
    indicators = {
        "credit_utilization": 70.0,
        "upcoming_emi": 20000,
        "account_balance": 25000,
        "expense_trend": 15.0,
        "payment_delay_frequency": 0.15,
    }
    recs = build_recommendations(indicators)
    assert len(recs) >= 3
    titles = [r["title"] for r in recs]
    assert "Reduce Credit Utilization" in titles
    assert "Plan Your Upcoming EMI" in titles
