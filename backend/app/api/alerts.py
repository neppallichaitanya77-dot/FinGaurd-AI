from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.risk import Alert
from app.models.user import User

router = APIRouter(prefix="/alerts", tags=["Alerts"])


def _apply_optional_filters(query, current_user_id: str):
    return query.filter(Alert.user_id == current_user_id)


@router.get("", summary="List early-warning alerts")
def get_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    severity: Optional[str] = None,
):
    query = db.query(Alert).filter(Alert.user_id == current_user.id)
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
    alerts = query.order_by(Alert.created_at.desc()).all()

    return [
        {
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "severity": a.severity,
            "status": a.status,
            "recommended_action": a.recommended_action,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alerts
    ]


@router.put("/{alert_id}/read", summary="Mark an alert as read")
def mark_alerts_read(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id, Alert.user_id == current_user.id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "read"
    db.commit()
    return {"success": True}


@router.delete("/{alert_id}", summary="Dismiss (delete) an alert")
def dismiss_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id, Alert.user_id == current_user.id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
    return {"success": True}
