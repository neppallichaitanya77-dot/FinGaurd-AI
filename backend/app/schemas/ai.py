from typing import List, Optional
from pydantic import BaseModel, Field


class ScenarioInput(BaseModel):
    monthly_income: float = Field(gt=0)
    monthly_expenses: float = Field(gt=0)
    outstanding_debt: float = Field(ge=0)
    credit_utilization: float = Field(ge=0, le=100)
    upcoming_emi: float = Field(ge=0)
    payment_delays: int = Field(ge=0)


class RiskFactorOut(BaseModel):
    name: str
    value: Optional[str] = None
    impact: str


class ScenarioOutput(BaseModel):
    risk_score: int
    risk_level: str
    financial_health_score: int
    risk_factors: List[RiskFactorOut] = []
    recommendations: List[str] = []


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    response: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict
