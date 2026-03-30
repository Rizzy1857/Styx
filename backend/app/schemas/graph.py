"""Graph and simulator response schemas."""

from pydantic import BaseModel
from typing import Optional, List


class GraphNode(BaseModel):
    id: str
    type: str
    status: Optional[str] = None


class GraphEdge(BaseModel):
    source: str
    target: str
    weight: int


class ImpactPayload(BaseModel):
    dependent_services: int
    traffic_percentage: float
    impact_score: float
    impact_severity: str


class DependencyGraphPayload(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    impact: ImpactPayload


class BlastRadiusRequest(BaseModel):
    api_ids: List[str]


class BlastRadiusPayload(BaseModel):
    dependent_services: int
    traffic_percentage: float
    impact_score: float
    severity: str
    affected_apis: List[str]
    recommendation: str
