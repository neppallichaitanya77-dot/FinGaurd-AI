import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.database.connection import Base


def gen_id() -> str:
    return str(uuid.uuid4())


class FinancialIndicator(Base):
    __tablename__ = "financial_indicators"

    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    dti = Column(Float, default=0)
    credit_utilization = Column(Float, default=0)
    payment_delay_frequency = Column(Float, default=0)
    balance_trend = Column(String(20), default="STABLE")
    debt_growth = Column(Float, default=0)
    expense_trend = Column(Float, default=0)
    overdraft_frequency = Column(Integer, default=0)
    repayment_consistency = Column(Float, default=1.0)
    recorded_at = Column(DateTime, default=datetime.utcnow)


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    risk_score = Column(Integer, default=0)
    risk_level = Column(String(20), default="LOW")
    probability = Column(Float, default=0.0)
    financial_health_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class RiskFactor(Base):
    __tablename__ = "risk_factors"

    id = Column(String(36), primary_key=True, default=gen_id)
    risk_score_id = Column(String(36), ForeignKey("risk_scores.id"), index=True, nullable=False)
    name = Column(String(120), nullable=False)
    value = Column(String(100), nullable=True)
    impact = Column(String(20), default="MEDIUM")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="low")
    status = Column(String(20), default="unread")
    recommended_action = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")
    category = Column(String(100), default="General")
    status = Column(String(20), default="pending")  # pending | accepted | dismissed
    created_at = Column(DateTime, default=datetime.utcnow)


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # user | assistant
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ScenarioPrediction(Base):
    __tablename__ = "scenario_predictions"

    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    input_json = Column(Text, nullable=False)
    risk_score = Column(Integer, default=0)
    risk_level = Column(String(20), default="LOW")
    financial_health_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=gen_id)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=True)
    action = Column(String(120), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
