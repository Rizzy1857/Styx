"""
GET /api/v1/alerts - List all alerts
PATCH /api/v1/alerts/{id}/acknowledge - Acknowledge an alert
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.models import Alert
from datetime import datetime
import asyncio
from sse_starlette.sse import EventSourceResponse
from uuid import UUID
import json

router = APIRouter(prefix="/api/v1", tags=["alerts"])

class AlertResponse(BaseModel):
    """Alert response model."""

    id: UUID
    api_id: UUID
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

@router.get("/alerts/stream")
async def stream_alerts(request: Request, db: Session = Depends(get_db)):
    """SSE endpoint for real-time alerts."""
    async def event_generator():
        last_check = datetime.utcnow()
        while True:
            if await request.is_disconnected():
                break
                
            # Query for new alerts since last check
            new_alerts = db.query(Alert).filter(Alert.created_at > last_check).order_by(Alert.created_at.asc()).all()
            
            if new_alerts:
                last_check = new_alerts[-1].created_at
                alerts_data = [
                    AlertResponse.model_validate(a).model_dump(mode="json")
                    for a in new_alerts
                ]
                yield {
                    "event": "new_alerts",
                    "data": json.dumps(alerts_data)
                }
            
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
