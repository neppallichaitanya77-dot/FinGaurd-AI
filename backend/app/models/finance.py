import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.database.connection import Base


def gen_id() -> str:
    return str(uuid.uuid4())


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    description = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)  # positive = credit, negative = debit
    transaction_type = Column(String(20), nullable=False)  # 'credit' | 'debit'
    balance = Column(Float, default=0)


class Loan(Base):
    __tablename__ = "loans"

    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String(120), nullable=False)
    outstanding_amount = Column(Float, default=0)
    interest_rate = Column(Float, default=0)
    monthly_emi = Column(Float, default=0)
    next_payment_date = Column(DateTime, nullable=True)
    remaining_tenure = Column(Integer, default=0)
    total_tenure = Column(Integer, default=0)


class LoanPayment(Base):
    __tablename__ = "loan_payments"

    id = Column(String(36), primary_key=True, default=gen_id)
    loan_id = Column(String(36), ForeignKey("loans.id"), index=True, nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    amount = Column(Float, default=0)
    principal = Column(Float, default=0)
    interest = Column(Float, default=0)
