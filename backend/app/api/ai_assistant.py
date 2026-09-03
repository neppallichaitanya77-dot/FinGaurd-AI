import uuid

from fastapi import APIRouter, Depends
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
        "total_debt": indicators["total_debt"],
        "payment_delays": indicators.get("overdraft_frequency", 0),
        "expense_trend": round(indicators.get("expense_trend", 0), 1),
    }


def _conversation_messages(db: Session, user_id: str, conversation_id: str):
    rows = (
        db.query(AIConversation)
        .filter(
            AIConversation.user_id == user_id,
            AIConversation.conversation_id == conversation_id,
        )
        .order_by(AIConversation.created_at.desc())
        .limit(12)
        .all()
    )
    return [{"role": row.role, "content": row.message} for row in reversed(rows)]


@router.post("/chat", response_model=ChatResponse, summary="Chat with the AI assistant")
def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation_id = payload.conversation_id or str(uuid.uuid4())
    context = _build_ai_context(db, current_user.id)
    context["conversation"] = _conversation_messages(db, current_user.id, conversation_id)

    db.add(
        AIConversation(
            user_id=current_user.id,
            conversation_id=conversation_id,
            role="user",
            message=payload.message,
        )
    )
    db.commit()

    response_details = llm_service.generate_response_details(payload.message, context)
    response = response_details["response"]
    suggested_questions = llm_service.generate_followup_questions(
        payload.message,
        response,
        context,
        payload.previous_suggested_questions,
    )

    db.add(
        AIConversation(
            user_id=current_user.id,
            conversation_id=conversation_id,
            role="assistant",
            message=response,
        )
    )
    db.commit()

    return {
        "response": response,
        "answer": response,
        "conversation_id": conversation_id,
        "suggested_questions": suggested_questions,
        "source": response_details["source"],
        "status": response_details["status"],
    }


@router.get("/history", summary="Get AI conversation history")
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    history = (
        db.query(AIConversation)
        .filter(AIConversation.user_id == current_user.id)
        .order_by(AIConversation.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "role": c.role,
            "content": c.message,
            "conversation_id": c.conversation_id,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in reversed(history)
    ]
