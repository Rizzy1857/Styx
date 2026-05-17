"""
Pydantic schemas for analytics responses.
"""

from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime


class APITrendPoint(BaseModel):
    """Single point in a time-series trend."""
    date: str
    zombie_count: int
    active_count: int
    deprecated_count: int
    shadow_count: int


class ZombieTrendResponse(BaseModel):
    """Historical zombie API trends."""
    trend_data: List[APITrendPoint]
    current_zombie_count: int
    zombie_percentage: float
    trend_direction: str  # "increasing", "decreasing", "stable"


class APIDistributionBucket(BaseModel):
    """Bucket for API distribution histogram."""
    bucket_name: str
    count: int
    percentage: float


class APIDistributionResponse(BaseModel):
    """Distribution of APIs by various dimensions."""
    by_status: Dict[str, int]
    by_lifecycle_risk: List[APIDistributionBucket]  # ACTIVE, DEPRECATED, ZOMBIE
    by_security_risk: List[APIDistributionBucket]  # LOW, MEDIUM, HIGH, CRITICAL
    total_apis: int


class RiskCell(BaseModel):
    """Single cell in risk heatmap."""
    lifecycle_bin: str  # "0-20", "20-40", etc.
    security_bin: str
    api_count: int


class RiskHeatmapResponse(BaseModel):
    """2D heatmap of APIs by lifecycle vs security risk."""
    heatmap: List[RiskCell]
    max_count: int
    min_count: int


class TopAtRiskAPI(BaseModel):
    """API ranked by risk score."""
    api_id: str
    endpoint: str
    zombie_score: float
    security_risk: float
    combined_risk: float  # weighted average
    has_anomalies: bool
    anomaly_types: List[str]


class TopAtRiskResponse(BaseModel):
    """Top N APIs sorted by combined risk."""
    top_apis: List[TopAtRiskAPI]
    total_at_risk: int
    critical_count: int


class MLModelMetrics(BaseModel):
    """ML model performance metrics."""
    model_type: str
    is_trained: bool
    training_samples: int
    contamination_threshold: float
    features_count: int
    last_trained_at: datetime = None


class AnalyticsOverviewResponse(BaseModel):
    """Dashboard overview combining all analytics."""
    zombie_trend: ZombieTrendResponse
    distribution: APIDistributionResponse
    risk_heatmap: RiskHeatmapResponse
    top_at_risk: TopAtRiskResponse
    ml_model_metrics: MLModelMetrics
