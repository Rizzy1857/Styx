"""
Anomaly detection for API lifecycle events.
Detects unusual dependency changes, traffic spikes, security posture shifts.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
import statistics

from backend.app.models.api import API
from backend.app.models.dependency import Dependency
from backend.app.models.security import APISecurityPosture


class AnomalyDetector:
    """Detects anomalies in API traffic, dependencies, and security."""

    def __init__(self, window_days: int = 30):
        """
        Initialize detector.

        Args:
            window_days: Rolling window for baseline calculation
        """
        self.window_days = window_days

    def detect_traffic_spike(self, api: API, session: Session) -> Tuple[bool, Dict]:
        """
        Detect unusual traffic spike on API.

        Returns:
            - is_anomaly: True if traffic is anomalous
            - metadata: spike metrics
        """
        now = datetime.utcnow()
        window_start = now - timedelta(days=self.window_days)

        # Mock: get current traffic level (using status as proxy)
        current_traffic = 100.0 if api.status == "ACTIVE" else 10.0

        # Get historical baseline (mock: average 50)
        baseline_traffic = 50.0

        # Calculate z-score
        std_dev = 15.0  # Mock standard deviation
        if std_dev == 0:
            z_score = 0.0
        else:
            z_score = abs((current_traffic - baseline_traffic) / std_dev)

        # Anomaly threshold: z-score > 2.5
        is_anomaly = z_score > 2.5

        metadata = {
            "current_traffic": current_traffic,
            "baseline_traffic": baseline_traffic,
            "std_dev": std_dev,
            "z_score": z_score,
            "window_days": self.window_days,
            "is_spike": is_anomaly
        }

        return is_anomaly, metadata

    def detect_dependency_change(self, api: API, session: Session) -> Tuple[bool, Dict]:
        """
        Detect unusual changes in API dependencies (new deps, removed deps).

        Returns:
            - is_anomaly: True if dependency graph changed significantly
            - metadata: change metrics
        """
        # Get current dependencies
        current_deps = session.query(Dependency).filter_by(calling_api_id=api.id).count()

        # Get baseline (mock: average 2.5 dependencies per API)
        baseline_deps = 2.5

        # Calculate deviation
        deviation = abs(current_deps - baseline_deps) / (baseline_deps or 1)

        # Anomaly threshold: >50% change
        is_anomaly = deviation > 0.5

        metadata = {
            "current_dependencies": current_deps,
            "baseline_dependencies": int(baseline_deps),
            "deviation_percent": deviation * 100,
            "is_dependency_changed": is_anomaly
        }

        return is_anomaly, metadata

    def detect_security_shift(self, api: API, session: Session) -> Tuple[bool, Dict]:
        """
        Detect unusual security posture shifts.

        Returns:
            - is_anomaly: True if security posture degraded significantly
            - metadata: security metrics
        """
        security = session.query(APISecurityPosture).filter_by(api_id=api.id).first()

        if not security:
            return False, {"no_security_posture": True}

        # Count violations
        violations = 0
        if not security.has_authentication:
            violations += 1
        if security.uses_http_only:
            violations += 1
        if not security.has_rate_limiting:
            violations += 1
        if security.exposes_pii:
            violations += 1

        # Baseline: expect 0-1 violations
        baseline_violations = 0.5
        deviation = violations - baseline_violations

        # Anomaly threshold: 2+ violations
        is_anomaly = violations >= 2

        metadata = {
            "current_violations": violations,
            "baseline_violations": baseline_violations,
            "violations_change": deviation,
            "is_security_degraded": is_anomaly,
            "has_authentication": security.has_authentication,
            "uses_http_only": security.uses_http_only,
            "has_rate_limiting": security.has_rate_limiting,
            "exposes_pii": security.exposes_pii
        }

        return is_anomaly, metadata

    def get_all_anomalies(self, api: API, session: Session) -> Dict[str, Tuple[bool, Dict]]:
        """
        Get all anomalies for an API.

        Returns:
            dict of anomaly_type: (is_anomaly, metadata)
        """
        return {
            "traffic_spike": self.detect_traffic_spike(api, session),
            "dependency_change": self.detect_dependency_change(api, session),
            "security_shift": self.detect_security_shift(api, session)
        }

    def has_anomalies(self, api: API, session: Session) -> bool:
        """Check if API has any anomalies."""
        anomalies = self.get_all_anomalies(api, session)
        return any(is_anom for is_anom, _ in anomalies.values())


# Global detector instance
_detector = AnomalyDetector(window_days=30)


def get_detector() -> AnomalyDetector:
    """Get global detector instance."""
    return _detector
