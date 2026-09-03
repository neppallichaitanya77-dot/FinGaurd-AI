from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.risk import Recommendation
from app.models.user import User

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("", summary="List personalized recommendations")
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == current_user.id)
        .order_by(Recommendation.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "priority": r.priority,
            "category": r.category,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in recs
    ]


@router.post("/{rec_id}/accept", summary="Accept / review a recommendation")
def accept_recommendation(
    rec_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rec = (
        db.query(Recommendation)
        .filter(Recommendation.id == rec_id, Recommendation.user_id == current_user.id)
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    rec.status = "accepted"
    db.commit()
    return {"success": True, "status": "accepted"}


@router.post("/{rec_id}/dismiss", summary="Dismiss a recommendation")
def dismiss_recommendation(
    rec_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rec = (
        db.query(Recommendation)
        .filter(Recommendation.id == rec_id, Recommendation.user_id == current_user.id)
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    rec.status = "dismissed"
    db.commit()
    return {"success": True, "status": "dismissed"}
