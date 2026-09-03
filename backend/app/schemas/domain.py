from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel


class RiskFactorOut(BaseModel):
    name: str
    value: Optional[str] = None
    impact: str


class FinancialHealthOut(BaseModel):
    financial_health_score: int
    financial_health_status: str
    health_score: int
    health_status: str
    key_positive_factors: List[str] = []
    positive_factors: List[str] = []
    key_concerns: List[str] = []
    concerns: List[str] = []
    balance: float = 0.0
    income: float = 0.0
    expenses: float = 0.0
    debt: float = 0.0
    credit_utilization: float = 0.0
    upcoming_emi: float = 0.0
    balance_chart: List[dict] = []
    expense_chart: List[dict] = []
    debt_chart: List[dict] = []


class RiskScoreOut(BaseModel):
    risk_score: int
    risk_level: str
    probability: float
    risk_factors: List[RiskFactorOut] = []
    financial_health_score: Optional[int] = None


class AlertOut(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    status: str
    recommended_action: Optional[str] = None
    created_at: Optional[Union[datetime, str]] = None

    model_config = {"from_attributes": True}


class RecommendationOut(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    category: str
    status: str
    created_at: Optional[Union[datetime, str]] = None

    model_config = {"from_attributes": True}


class TransactionOut(BaseModel):
    id: str
    date: Optional[Union[datetime, str]] = None
    description: str
    category: str
    amount: float
    type: str
    balance: float

    model_config = {"from_attributes": True}


class LoanOut(BaseModel):
    id: str
    name: str
    outstanding_amount: float
    outstanding: Optional[float] = None
    interest_rate: float
    monthly_emi: float
    emi: Optional[float] = None
    next_payment_date: Optional[Union[datetime, str]] = None
    next_payment: Optional[Union[datetime, str]] = None
    remaining_tenure: int
    total_tenure: int
    payments: List[dict] = []

    model_config = {"from_attributes": True}


class ChatMessageOut(BaseModel):
    role: str
    content: str


class DashboardOut(BaseModel):
    health_score: int
    health_status: str
    risk_score: int
    risk_level: str
    risk_factors: List[RiskFactorOut] = []
    balance: float
    income: float
    expenses: float
    debt: float
    credit_utilization: float
    upcoming_emi: float
    alerts: List[AlertOut] = []
    recommendations: List[RecommendationOut] = []
    balance_chart: List[dict] = []
    expense_chart: List[dict] = []
    debt_chart: List[dict] = []
