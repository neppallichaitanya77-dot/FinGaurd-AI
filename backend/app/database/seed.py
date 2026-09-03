"""Seed demo data so the application is immediately demonstrable.

Creates a demo customer with realistic (clearly simulated/anonymized) financial
data including loans, transactions, and enough variety to exercise the ML risk
engine, alerts, and recommendations.
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.database.connection import SessionLocal
from app.models.finance import Loan, LoanPayment, Transaction
from app.models.profile import CustomerProfile
from app.models.user import User

settings = get_settings()


def _compute_running_balance(base: float, txns):
    """Compute account balance after applying transactions chronologically."""
    running = base
    for t in txns:
        running += t["amount"]
        t["_balance"] = running
    return running


def seed_demo_data(db: Session = None) -> User | None:
    own_session = db is None
    session = db or SessionLocal()

    try:
        email = settings.DEMO_USER_EMAIL
        existing = session.query(User).filter(User.email == email).first()
        if existing:
            return existing

        user = User(
            name="Demo Customer",
            email=email,
            hashed_password=hash_password(settings.DEMO_USER_PASSWORD),
            role="CUSTOMER",
        )
        session.add(user)
        session.flush()

        profile = CustomerProfile(
            user_id=user.id,
            monthly_income=45000,
            account_balance=85400,
            credit_limit=80000,
            credit_used=51200,
            payment_delays=1,
        )
        session.add(profile)

        now = datetime.utcnow()

        # --- Loans ---
        home_loan = Loan(
            user_id=user.id,
            name="Home Loan",
            outstanding_amount=850000,
            interest_rate=8.5,
            monthly_emi=8500,
            next_payment_date=now + timedelta(days=12),
            remaining_tenure=120,
            total_tenure=240,
        )
        session.add(home_loan)
        session.flush()

        for i in range(12):
            amount = 8500
            session.add(
                LoanPayment(
                    loan_id=home_loan.id,
                    payment_date=now - timedelta(days=(i + 1) * 30),
                    amount=amount,
                    principal=3200 + i * 50,
                    interest=5300 - i * 30,
                )
            )

        personal_loan = Loan(
            user_id=user.id,
            name="Personal Loan",
            outstanding_amount=125000,
            interest_rate=12.0,
            monthly_emi=4200,
            next_payment_date=now + timedelta(days=17),
            remaining_tenure=32,
            total_tenure=48,
        )
        session.add(personal_loan)
        session.flush()

        for i in range(12):
            session.add(
                LoanPayment(
                    loan_id=personal_loan.id,
                    payment_date=now - timedelta(days=(i + 1) * 30),
                    amount=4200,
                    principal=2800 + i * 40,
                    interest=1400 - i * 35,
                )
            )

        car_loan = Loan(
            user_id=user.id,
            name="Car Loan",
            outstanding_amount=275000,
            interest_rate=9.0,
            monthly_emi=6800,
            next_payment_date=now + timedelta(days=7),
            remaining_tenure=48,
            total_tenure=60,
        )
        session.add(car_loan)
        session.flush()

        for i in range(12):
            session.add(
                LoanPayment(
                    loan_id=car_loan.id,
                    payment_date=now - timedelta(days=(i + 1) * 30),
                    amount=6800,
                    principal=4100 + i * 30,
                    interest=2700 - i * 40,
                )
            )

        # --- Transactions (past 90 days) ---
        txn_specs = [
            ("Salary Credit", "Income", 45000, "credit"),
            ("Grocery Store", "Groceries", -3200, "debit"),
            ("Electricity Bill", "Utilities", -1800, "debit"),
            ("Restaurant", "Food & Dining", -2400, "debit"),
            ("Freelance Payment", "Income", 12000, "credit"),
            ("Online Shopping", "Shopping", -4500, "debit"),
            ("Netflix Subscription", "Entertainment", -649, "debit"),
            ("Petrol", "Transport", -2200, "debit"),
            ("Medical Expense", "Healthcare", -1500, "debit"),
            ("ATM Withdrawal", "Cash", -5000, "debit"),
            ("Insurance Premium", "Insurance", -3500, "debit"),
            ("Mobile Recharge", "Utilities", -599, "debit"),
        ]

        # Spread over ~10 weeks so the balance series looks realistic.
        balance = 40000.0
        weekly_sequence = []
        base_specs = txn_specs[4:]  # recurring smaller ones
        base_specs += txn_specs  # repeat
        weeks = 10
        day_counter = 0
        for week in range(weeks):
            for spec in base_specs[week * 3: week * 3 + 4]:
                desc, cat, amount, ttype = spec
                balance += amount
                weekly_sequence.append(
                    {
                        "date": now - timedelta(days=(week * 7 + day_counter)),
                        "description": desc,
                        "category": cat,
                        "amount": amount,
                        "type": ttype,
                        "balance": balance,
                    }
                )
                day_counter += 1

        # Ensure the first entry (latest) shows the current balance ~85,400
        for seq in weekly_sequence:
            session.add(
                Transaction(
                    user_id=user.id,
                    date=seq["date"],
                    description=seq["description"],
                    category=seq["category"],
                    amount=seq["amount"],
                    transaction_type=seq["type"],
                    balance=seq["balance"],
                )
            )

        session.commit()
        return user
    finally:
        if own_session:
            session.close()


if __name__ == "__main__":
    u = seed_demo_data()
    print(f"Seeded demo user: {u.email} / {settings.DEMO_USER_PASSWORD}")
