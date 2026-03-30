"""GET /api/v1/apis/{id}/dependencies - Dependency graph data."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import API
from app.services.graph_builder import GraphBuilder
from app.schemas.graph import DependencyGraphPayload

router = APIRouter(prefix="/api/v1", tags=["graph"])


@router.get("/apis/{api_id}/dependencies", response_model=DependencyGraphPayload)
def get_dependencies(api_id: str, db: Session = Depends(get_db)):
    """
    Get dependency graph for an API.

    Returns nodes, edges, and impact score formatted for D3.js.
    """
    api = db.query(API).filter(API.id == api_id).first()
    if not api:
        raise HTTPException(status_code=404, detail="API not found")

    graph_data = GraphBuilder.get_graph_data(api_id, db)
    return DependencyGraphPayload(**graph_data)
