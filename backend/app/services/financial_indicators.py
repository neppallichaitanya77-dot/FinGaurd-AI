"""Financial indicator calculations.

All indicator computations are deliberately kept in the backend so the
frontend never performs business-logic / ML calculations.
"""
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.finance import Loan, LoanPayment, Transaction
from app.models.profile import CustomerProfile


def compute_dti(monthly_debt_payments: float, monthly_income: float) -> float:
    """Debt-to-Income ratio = monthly debt payments / monthly income."""
    if monthly_income <= 0:
        return 0.0
    return (monthly_debt_payments / monthly_income) * 100


def compute_credit_utilization(credit_used: float, credit_limit: float) -> float:
    """Credit utilization = used credit / available credit * 100."""
    if credit_limit <= 0:
        return 0.0
    return (credit_used / credit_limit) * 100


def compute_payment_delay_frequency(delayed: int, total: int) -> float:
    """Fraction of delayed payments."""
    if total <= 0:
        return 0.0
    return delayed / total


def classify_balance_trend(balances: List[float]) -> str:
    """Classify a series of balances as INCREASING / STABLE / DECLINING."""
    if not balances or len(balances) < 2:
        return "STABLE"
    first = balances[0]
    last = balances[-1]
    change = (last - first) / abs(first) if first else 0.0
    if change > 0.05:
        return "INCREASING"
    if change < -0.05:
        return "DECLINING"
    return "STABLE"


def compute_expense_trend(current_expenses: float, historical_expenses: float) -> float:
    """Percentage expense change vs. historical baseline (positive = higher)."""
    if historical_expenses <= 0:
        return 0.0
    return ((current_expenses - historical_expenses) / historical_expenses) * 100


def get_profile(db: Session, user_id: str) -> Optional[CustomerProfile]:
    return (
        db.query(CustomerProfile)
        .filter(CustomerProfile.user_id == user_id)
        .first()
    )


def get_total_debt(db: Session, user_id: str) -> float:
    loans = db.query(Loan).filter(Loan.user_id == user_id).all()
    return sum(l.outstanding_amount for l in loans)


def get_upcoming_emi(db: Session, user_id: str) -> float:
    loans = db.query(Loan).filter(Loan.user_id == user_id).all()
    return sum(l.monthly_emi for l in loans)


def get_credit_utilization(db: Session, user_id: str) -> float:
    profile = get_profile(db, user_id)
    if not profile:
        return 0.0
    return compute_credit_utilization(profile.credit_used, profile.credit_limit)


def get_balance(db: Session, user_id: str) -> float:
    profile = get_profile(db, user_id)
    return profile.account_balance if profile else 0.0


def get_monthly_income(db: Session, user_id: str) -> float:
    profile = get_profile(db, user_id)
    return profile.monthly_income if profile else 0.0


def get_balance_series(db: Session, user_id: str, days: int = 90) -> List[float]:
    """Return recent monthly balance snapshots for trend analysis."""
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.date.asc())
        .all()
    )
    if not transactions:
        return [get_balance(db, user_id)]
    monthly = {}
    for t in transactions:
        key = t.date.strftime("%Y-%m")
        if key not in monthly:
            monthly[key] = t.balance
    snapshots = [v for _, v in sorted(monthly.items())]
    return snapshots or [get_balance(db, user_id)]


def get_expense_trend(db: Session, user_id: str) -> float:
    """Compare current month debits vs average of previous 3 months."""
    from datetime import datetime, timedelta

    now = datetime.utcnow()
    current_start = now.replace(day=1)
    txns = db.query(Transaction).filter(Transaction.user_id == user_id).all()

    current_expenses = sum(
        abs(t.amount)
        for t in txns
        if t.transaction_type == "debit" and t.date >= current_start
    )
    historical_entries = []
    for t in txns:
        if t.transaction_type == "debit" and t.date < current_start and t.date >= current_start - timedelta(days=90):
            historical_entries.append(abs(t.amount))
    historical_avg = sum(historical_entries) / len(historical_entries) if historical_entries else current_expenses
    return compute_expense_trend(current_expenses, historical_avg)


def compute_all_indicators(db: Session, user_id: str) -> Dict:
    """Compute the full set of financial indicators for a user."""
    profile = get_profile(db, user_id)
    income = profile.monthly_income if profile else 0.0
    balance = profile.account_balance if profile else 0.0
    delays = profile.payment_delays if profile else 0
    used = profile.credit_used if profile else 0
    limit = profile.credit_limit if profile else 0

    total_debt = get_total_debt(db, user_id)
    upcoming_emi = get_upcoming_emi(db, user_id)
    utilization = compute_credit_utilization(used, limit)
    dti = compute_dti(upcoming_emi, income)
    balance_series = get_balance_series(db, user_id)
    balance_trend = classify_balance_trend(balance_series)
    expense_trend = get_expense_trend(db, user_id)
    loans = db.query(Loan).filter(Loan.user_id == user_id).all()
    loan_ids = [l.id for l in loans]
    total_payments = (
        db.query(LoanPayment).filter(LoanPayment.loan_id.in_(loan_ids)).count()
        if loan_ids
        else 0
    )
    total_cycles = max(total_payments + delays, 12)
    delay_freq = compute_payment_delay_frequency(delays, total_cycles)
    consistency = max(1.0 - delay_freq, 0.0)

    return {
        "dti": dti,
        "credit_utilization": utilization,
        "payment_delay_frequency": delay_freq,
        "balance_trend": balance_trend,
        "debt_growth": 0.0,
        "expense_trend": expense_trend,
        "overdraft_frequency": delays,
        "repayment_consistency": consistency,
        "total_debt": total_debt,
        "upcoming_emi": upcoming_emi,
        "account_balance": balance,
        "monthly_income": income,
    }
