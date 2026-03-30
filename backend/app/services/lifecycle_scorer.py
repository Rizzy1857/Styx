"""
Lifecycle Scoring Service

Calculates lifecycle risk scores for APIs based on multiple factors:
- Traffic decay (days since last seen)
- Documentation status
- Authentication strength
- Dependency orphan status
"""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import API, Dependency, APISecurityPosture


class LifecycleScorer:
    """Calculate API lifecycle risk scores."""

    @staticmethod
    def calculate_zombie_score(api: API, session: Session) -> Dict[str, Any]:
        """
        Calculate zombie score (0-1) and factors.

        Factors:
        - traffic_decay (35%): days since last seen / 90
        - documentation (25%): 1 if no owner/documentation else 0
        - auth_weakness (20%): 1 if no auth else 0
        - orphan (20%): 1 if no incoming dependencies else 0

        Returns:
            {
                "zombie_score": float (0-1),
                "factors": {
                    "traffic_decay": float,
                    "documentation": float,
                    "auth_weakness": float,
                    "dependency_orphan": float
                },
                "classification": str (ACTIVE/DEPRECATED/ZOMBIE)
            }
        """
        factors = {}

        # Factor 1: Traffic decay (35%)
        if api.last_traffic_seen:
            days_since = (datetime.utcnow() - api.last_traffic_seen.replace(tzinfo=None)).days
            factors["traffic_decay"] = min(days_since / 90.0, 1.0)
        else:
            factors["traffic_decay"] = 1.0

        # Factor 2: Documentation (25%)
        factors["documentation"] = 0.0 if (api.owner and api.has_documentation) else 1.0

        # Factor 3: Authentication weakness (20%)
        security = session.query(APISecurityPosture).filter_by(
            api_id=api.id
        ).first()
        factors["auth_weakness"] = 0.0 if (security and security.has_authentication) else 1.0

        # Factor 4: Dependency orphan (20%)
        incoming_deps = session.query(func.count(Dependency.id)).filter_by(
            target_api_id=api.id
        ).scalar()
        factors["dependency_orphan"] = 0.0 if incoming_deps > 0 else 1.0

        # Calculate weighted score
        zombie_score = (
            0.35 * factors["traffic_decay"]
            + 0.25 * factors["documentation"]
            + 0.20 * factors["auth_weakness"]
            + 0.20 * factors["dependency_orphan"]
        )

        # Classify
        if zombie_score < 0.4:
            classification = "ACTIVE"
        elif zombie_score < 0.7:
            classification = "DEPRECATED"
        else:
            classification = "ZOMBIE"

        return {
            "zombie_score": round(zombie_score, 3),
            "factors": {k: round(v, 3) for k, v in factors.items()},
            "classification": classification,
        }

    @staticmethod
    def calculate_impact_score(api: API, session: Session) -> Dict[str, Any]:
        """
        Calculate operational impact score based on dependents.

        Formula: 0.6 * traffic_percentage + 0.4 * normalized_dependent_count

        Returns:
            {
                "dependent_services": int,
                "traffic_percentage": float,
                "impact_score": float (0-1),
                "impact_severity": str (LOW/MEDIUM/HIGH)
            }
        """
        # Count dependent services
        dependencies = (
            session.query(Dependency)
            .filter_by(target_api_id=api.id)
            .all()
        )

        dependent_services = len(set(d.source_service for d in dependencies))
        traffic_percentage = sum(d.traffic_percentage for d in dependencies) if dependencies else 0.0

        # Normalize dependency count to 0-1 scale
        normalized_deps = min(dependent_services / 20.0, 1.0)

        # Weighted calculation
        impact_score = 0.6 * traffic_percentage + 0.4 * normalized_deps

        # Classify severity
        if impact_score >= 0.7:
            severity = "HIGH"
        elif impact_score >= 0.3:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        return {
            "dependent_services": dependent_services,
            "traffic_percentage": round(traffic_percentage, 3),
            "impact_score": round(impact_score, 3),
            "impact_severity": severity,
        }
