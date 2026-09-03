import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.database.connection import Base


def gen_id() -> str:
    return str(uuid.uuid4())


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    monthly_income = Column(Float, default=0)
    account_balance = Column(Float, default=0)
    credit_limit = Column(Float, default=0)
    credit_used = Column(Float, default=0)
    payment_delays = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    balance = Column(Float, default=0)
    account_type = Column(String(50), default="savings")
    created_at = Column(DateTime, default=datetime.utcnow)
