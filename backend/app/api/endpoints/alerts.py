"""
GET /api/v1/alerts - List all alerts
PATCH /api/v1/alerts/{id}/acknowledge - Acknowledge an alert
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.models import Alert
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["alerts"])


class AlertResponse(BaseModel):
    """Alert response model."""

    id: str
    api_id: str
    alert_type: str
    severity: str
    trigger_metadata: dict
    acknowledged: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/alerts", response_model=list[AlertResponse])
def get_alerts(db: Session = Depends(get_db), limit: int = 50):
    """
    Get recent alerts.

    Sorted by creation date (newest first).
    """
    alerts = (
        db.query(Alert)
        .order_by(Alert.created_at.desc())
        .limit(limit)
        .all()
    )
    return alerts


@router.patch("/alerts/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(alert_id: str, db: Session = Depends(get_db)):
    """Acknowledge an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.acknowledged = True
    db.commit()
    return alert
