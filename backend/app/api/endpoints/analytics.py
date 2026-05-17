"""
Analytics endpoints for Phase 2.1.
Provides trending data, distributions, heatmaps, and top at-risk APIs.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict
from collections import defaultdict

from app.core.database import get_db
from app.models.api import API
from app.models.dependency import Dependency
from app.models.security import APISecurityPosture
from app.schemas.analytics import (
    ZombieTrendResponse, APITrendPoint, APIDistributionResponse,
    APIDistributionBucket, RiskHeatmapResponse, RiskCell,
    TopAtRiskResponse, TopAtRiskAPI, MLModelMetrics,
    AnalyticsOverviewResponse
)
from app.services.isolation_forest_scorer import get_scorer, train_model
from app.services.anomaly_detector import get_detector
from app.services.security_analyzer import SecurityAnalyzer

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])
security_analyzer = SecurityAnalyzer()


@router.get("/zombie-trend", response_model=ZombieTrendResponse)
def get_zombie_trend(db: Session = Depends(get_db)) -> ZombieTrendResponse:
    """
    Get zombie API trends over last 30 days.
    Mock data: generates daily counts based on seed data variations.
    """
    # Get all APIs and score them
    apis = db.query(API).all()
    scorer = get_scorer()

    # Score all APIs
    zombie_count = 0
    active_count = 0
    deprecated_count = 0
    shadow_count = 0

    for api in apis:
        score, _ = scorer.calculate_zombie_score(api, db)
        classification = scorer.classify_api(score)
        if classification == "ZOMBIE":
            zombie_count += 1
        elif classification == "ACTIVE":
            active_count += 1
        elif classification == "DEPRECATED":
            deprecated_count += 1
        else:
            shadow_count += 1

    # Generate 30-day trend (mock: slight variations)
    trend_data = []
    now = datetime.utcnow()
    for day_offset in range(30, 0, -1):
        date = now - timedelta(days=day_offset)
        # Mock trend: slight variation around current counts
        variation = (day_offset % 5) - 2
        trend_data.append(APITrendPoint(
            date=date.strftime("%Y-%m-%d"),
            zombie_count=max(0, zombie_count - variation),
            active_count=max(0, active_count + variation),
            deprecated_count=deprecated_count,
            shadow_count=shadow_count
        ))

    total = zombie_count + active_count + deprecated_count + shadow_count
    zombie_percent = (zombie_count / total * 100) if total > 0 else 0

    # Determine trend direction
    first_zombies = trend_data[0].zombie_count
    last_zombies = trend_data[-1].zombie_count
    if last_zombies > first_zombies * 1.1:
        trend_direction = "increasing"
    elif last_zombies < first_zombies * 0.9:
        trend_direction = "decreasing"
    else:
        trend_direction = "stable"

    return ZombieTrendResponse(
        trend_data=trend_data,
        current_zombie_count=zombie_count,
        zombie_percentage=zombie_percent,
        trend_direction=trend_direction
    )


@router.get("/distribution", response_model=APIDistributionResponse)
def get_api_distribution(db: Session = Depends(get_db)) -> APIDistributionResponse:
    """Get API distribution by status and risk levels."""
    apis = db.query(API).all()
    scorer = get_scorer()

    by_status = {"ACTIVE": 0, "DEPRECATED": 0, "ZOMBIE": 0, "SHADOW": 0}
    lifecycle_risks = []
    security_risks = []

    for api in apis:
        by_status[api.status] += 1

        # Get lifecycle risk
        score, _ = scorer.calculate_zombie_score(api, db)
        lifecycle_risks.append(score)

        # Get security risk
        findings = security_analyzer.analyze_security(api, db).findings
        max_cvss = max([f.cvss_score for f in findings], default=0.0)
        security_risks.append(max_cvss / 10.0)

    # Create lifecycle risk buckets
    lifecycle_buckets = [
        APIDistributionBucket(bucket_name="LOW (0-0.3)", count=0, percentage=0),
        APIDistributionBucket(bucket_name="MEDIUM (0.3-0.6)", count=0, percentage=0),
        APIDistributionBucket(bucket_name="HIGH (0.6-1.0)", count=0, percentage=0)
    ]
    for score in lifecycle_risks:
        if score < 0.3:
            lifecycle_buckets[0].count += 1
        elif score < 0.6:
            lifecycle_buckets[1].count += 1
        else:
            lifecycle_buckets[2].count += 1

    # Create security risk buckets
    security_buckets = [
        APIDistributionBucket(bucket_name="LOW (0-0.3)", count=0, percentage=0),
        APIDistributionBucket(bucket_name="MEDIUM (0.3-0.6)", count=0, percentage=0),
        APIDistributionBucket(bucket_name="HIGH (0.6-0.8)", count=0, percentage=0),
        APIDistributionBucket(bucket_name="CRITICAL (0.8-1.0)", count=0, percentage=0)
    ]
    for score in security_risks:
        if score < 0.3:
            security_buckets[0].count += 1
        elif score < 0.6:
            security_buckets[1].count += 1
        elif score < 0.8:
            security_buckets[2].count += 1
        else:
            security_buckets[3].count += 1

    total = len(apis)
    for bucket in lifecycle_buckets + security_buckets:
        bucket.percentage = (bucket.count / total * 100) if total > 0 else 0

    return APIDistributionResponse(
        by_status=by_status,
        by_lifecycle_risk=lifecycle_buckets,
        by_security_risk=security_buckets,
        total_apis=total
    )


@router.get("/risk-heatmap", response_model=RiskHeatmapResponse)
def get_risk_heatmap(db: Session = Depends(get_db)) -> RiskHeatmapResponse:
    """Get 2D heatmap of APIs by lifecycle vs security risk."""
    apis = db.query(API).all()
    scorer = get_scorer()

    # Create 3x3 heatmap
    heatmap_dict = {}
    for lifecycle_bin in ["0-33", "33-67", "67-100"]:
        for security_bin in ["0-33", "33-67", "67-100"]:
            heatmap_dict[(lifecycle_bin, security_bin)] = 0

    for api in apis:
        # Get lifecycle risk
        lifecycle_score, _ = scorer.calculate_zombie_score(api, db)
        lifecycle_percent = lifecycle_score * 100
        if lifecycle_percent < 33:
            lifecycle_bin = "0-33"
        elif lifecycle_percent < 67:
            lifecycle_bin = "33-67"
        else:
            lifecycle_bin = "67-100"

        # Get security risk
        findings = security_analyzer.analyze_security(api, db).findings
        max_cvss = max([f.cvss_score for f in findings], default=0.0)
        security_percent = (max_cvss / 10.0) * 100
        if security_percent < 33:
            security_bin = "0-33"
        elif security_percent < 67:
            security_bin = "33-67"
        else:
            security_bin = "67-100"

        heatmap_dict[(lifecycle_bin, security_bin)] += 1

    # Convert to heatmap cells
    heatmap = [
        RiskCell(lifecycle_bin=k[0], security_bin=k[1], api_count=v)
        for k, v in heatmap_dict.items()
    ]
    max_count = max([cell.api_count for cell in heatmap], default=1)
    min_count = min([cell.api_count for cell in heatmap], default=0)

    return RiskHeatmapResponse(
        heatmap=heatmap,
        max_count=max_count,
        min_count=min_count
    )


@router.get("/top-at-risk", response_model=TopAtRiskResponse)
def get_top_at_risk(limit: int = 10, db: Session = Depends(get_db)) -> TopAtRiskResponse:
    """Get top N APIs by combined risk score."""
    apis = db.query(API).all()
    scorer = get_scorer()
    detector = get_detector()

    api_risks = []
    for api in apis:
        # Get lifecycle risk
        lifecycle_score, _ = scorer.calculate_zombie_score(api, db)

        # Get security risk
        findings = security_analyzer.analyze_security(api, db).findings
        max_cvss = max([f.cvss_score for f in findings], default=0.0)
        security_score = max_cvss / 10.0

        # Get anomalies
        anomalies = detector.get_all_anomalies(api, db)
        anomaly_types = [k for k, (is_anom, _) in anomalies.items() if is_anom]

        # Combined risk (equal weights)
        combined_risk = (lifecycle_score + security_score) / 2.0

        api_risks.append(TopAtRiskAPI(
            api_id=str(api.id),
            endpoint=api.endpoint,
            zombie_score=lifecycle_score,
            security_risk=security_score,
            combined_risk=combined_risk,
            has_anomalies=len(anomaly_types) > 0,
            anomaly_types=anomaly_types
        ))

    # Sort by combined risk (descending)
    api_risks.sort(key=lambda x: x.combined_risk, reverse=True)

    # Count critical (combined_risk > 0.7)
    critical_count = sum(1 for api in api_risks if api.combined_risk > 0.7)

    return TopAtRiskResponse(
        top_apis=api_risks[:limit],
        total_at_risk=len(api_risks),
        critical_count=critical_count
    )


@router.post("/train-model")
def train_ml_model(db: Session = Depends(get_db)) -> Dict:
    """Train the Isolation Forest ML model on current database."""
    train_model(db)
    scorer = get_scorer()
    return {
        "status": "success",
        "message": "ML model trained successfully",
        "is_trained": scorer.is_trained
    }


@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(db: Session = Depends(get_db)) -> AnalyticsOverviewResponse:
    """Get complete analytics dashboard overview."""
    scorer = get_scorer()

    # Train model if not already trained
    if not scorer.is_trained:
        train_model(db)

    zombie_trend = get_zombie_trend(db)
    distribution = get_api_distribution(db)
    risk_heatmap = get_risk_heatmap(db)
    top_at_risk = get_top_at_risk(db=db)

    ml_metrics = MLModelMetrics(
        model_type="isolation_forest",
        is_trained=scorer.is_trained,
        training_samples=len(db.query(API).all()),
        contamination_threshold=0.3,
        features_count=8,
        last_trained_at=datetime.utcnow() if scorer.is_trained else None
    )

    return AnalyticsOverviewResponse(
        zombie_trend=zombie_trend,
        distribution=distribution,
        risk_heatmap=risk_heatmap,
        top_at_risk=top_at_risk,
        ml_model_metrics=ml_metrics
    )
