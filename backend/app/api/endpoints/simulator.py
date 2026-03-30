"""Blast radius simulator endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import API
from app.services.graph_builder import GraphBuilder
from app.schemas.graph import BlastRadiusRequest, BlastRadiusPayload

router = APIRouter(prefix="/api/v1", tags=["simulator"])


@router.post("/simulator/blast-radius", response_model=BlastRadiusPayload)
def simulate_blast_radius(request: BlastRadiusRequest, db: Session = Depends(get_db)):
    for api_id in request.api_ids:
        api = db.query(API).filter(API.id == api_id).first()
        if not api:
            raise HTTPException(status_code=404, detail=f"API {api_id} not found")

    result = GraphBuilder.calculate_blast_radius(request.api_ids, db)
    return BlastRadiusPayload(**result)
