"""
GET /api/v1/apis - List all APIs
GET /api/v1/apis/{id} - Get API details
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import API
from app.schemas.scoring import APIResponse

router = APIRouter(prefix="/api/v1", tags=["apis"])


@router.get("/apis", response_model=list[APIResponse])
def list_apis(db: Session = Depends(get_db)):
    """List all APIs."""
    apis = db.query(API).all()
    return apis


@router.get("/apis/{api_id}", response_model=APIResponse)
def get_api(api_id: str, db: Session = Depends(get_db)):
    """Get API details."""
    api = db.query(API).filter(API.id == api_id).first()
    if not api:
        raise HTTPException(status_code=404, detail="API not found")
    return api
