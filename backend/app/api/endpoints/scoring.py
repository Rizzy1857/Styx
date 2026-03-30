"""
GET /api/v1/apis/{id}/score - Lifecycle and security scores
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import API, APISecurityPosture
from app.services.lifecycle_scorer import LifecycleScorer
from app.services.security_analyzer import SecurityAnalyzer
from app.schemas.scoring import ScoreResponse, LifecycleScoreResponse, SecurityAnalysisResponse

router = APIRouter(prefix="/api/v1", tags=["scoring"])


@router.get("/apis/{api_id}/score", response_model=ScoreResponse)
def get_api_score(api_id: str, db: Session = Depends(get_db)):
    """
    Get lifecycle and security scores for an API.

    Returns combined zombie score and security analysis.
    """
    api = db.query(API).filter(API.id == api_id).first()
    if not api:
        raise HTTPException(status_code=404, detail="API not found")

    security = db.query(APISecurityPosture).filter(APISecurityPosture.api_id == api_id).first()
    if not security:
        raise HTTPException(status_code=404, detail="Security posture not found")

    # Calculate scores
    lifecycle_score = LifecycleScorer.calculate_zombie_score(api, db)
    security_analysis = SecurityAnalyzer.analyze_security(api, security)

    # Update zombie_score in database
    api.zombie_score = lifecycle_score["zombie_score"]
    db.commit()

    return ScoreResponse(
        api_id=api_id,
        lifecycle=LifecycleScoreResponse(**lifecycle_score),
        security=SecurityAnalysisResponse(**security_analysis),
    )
