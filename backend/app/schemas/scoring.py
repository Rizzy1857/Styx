"""
Pydantic schemas for API responses.
"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class APIResponse(BaseModel):
    """Basic API information."""

    id: str
    endpoint: str
    method: str
    host: str
    current_status: str
    zombie_score: Optional[float] = None
    last_traffic_seen: Optional[str] = None
    dormant_duration_days: Optional[int] = None
    owner: Optional[str] = None
    has_documentation: bool = False

    class Config:
        from_attributes = True


class LifecycleScoreResponse(BaseModel):
    """Lifecycle score and factors."""

    zombie_score: float
    factors: Dict[str, float]
    classification: str


class SecurityFinding(BaseModel):
    """Single security finding."""

    category: str
    cvss_score: float
    severity: str
    description: str


class SecurityAnalysisResponse(BaseModel):
    """Security analysis results."""

    findings: List[SecurityFinding]
    security_risk_score: float
    highest_severity: str


class ScoreResponse(BaseModel):
    """Combined lifecycle and security scores."""

    api_id: str
    lifecycle: LifecycleScoreResponse
    security: SecurityAnalysisResponse


class ImpactScore(BaseModel):
    """Impact score for an API."""

    dependent_services: int
    traffic_percentage: float
    impact_score: float
    impact_severity: str


class DependencyNode(BaseModel):
    """Node in dependency graph."""

    id: str
    type: str  # "service" or "api"
    status: Optional[str] = None  # For APIs


class DependencyEdge(BaseModel):
    """Edge in dependency graph."""

    source: str
    target: str
    weight: int


class DependencyGraphResponse(BaseModel):
    """Dependency graph data."""

    nodes: List[DependencyNode]
    edges: List[DependencyEdge]
    impact: ImpactScore


class BlastRadiusResponse(BaseModel):
    """Blast radius simulation results."""

    dependent_services: int
    traffic_percentage: float
    impact_score: float
    severity: str
    affected_apis: List[str]
    recommendation: str
