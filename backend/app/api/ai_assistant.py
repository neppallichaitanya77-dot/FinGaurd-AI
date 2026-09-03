from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.risk import AIConversation
from app.models.user import User
from app.schemas.ai import ChatRequest, ChatResponse
from app.services import llm_service, user_finance_service

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


def _build_ai_context(db: Session, user_id: str) -> dict:
    indicators = user_finance_service.get_indicators(db, user_id)
    risk = user_finance_service.score_risk(indicators)
    return {
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "risk_factors": risk["risk_factors"],
        "health_score": risk["financial_health_score"],
        "credit_utilization": round(indicators["credit_utilization"], 1),
        "balance_trend": indicators["balance_trend"],
        "dti": round(indicators["dti"], 1),
        "upcoming_emi": indicators["upcoming_emi"],
        "account_balance": indicators["account_balance"],
        "monthly_income": indicators["monthly_income"],
    }


@router.post("/chat", response_model=ChatResponse, summary="Chat with the AI assistant")
def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    context = _build_ai_context(db, current_user.id)

    db.add(
        AIConversation(user_id=current_user.id, role="user", message=payload.message)
    )
    db.commit()

    response = llm_service.generate_response(payload.message, context)

    db.add(
        AIConversation(user_id=current_user.id, role="assistant", message=response)
    )
    db.commit()

    return {"response": response}


@router.get("/history", summary="Get AI conversation history")
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    history = (
        db.query(AIConversation)
        .filter(AIConversation.user_id == current_user.id)
        .order_by(AIConversation.created_at.asc())
        .all()
    )
    return [
        {"role": c.role, "content": c.message, "created_at": c.created_at.isoformat() if c.created_at else None}
        for c in history
    ]
