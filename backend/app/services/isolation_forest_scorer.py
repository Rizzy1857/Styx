"""
Isolation Forest-based API lifecycle scorer.
Replaces heuristic scoring with ML model trained on historical API patterns.
"""

import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.models.api import API
from app.models.dependency import Dependency
from app.models.security import APISecurityPosture


class IsolationForestScorer:
    """ML-based zombie API scorer using Isolation Forest anomaly detection."""

    def __init__(self):
        """Initialize the scorer with pre-trained model."""
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            "days_since_last_call",
            "documentation_score",
            "auth_mechanism_score",
            "orphan_dependency_ratio",
            "security_violations_count",
            "response_time_ms",
            "error_rate_percent",
            "dependent_api_count"
        ]
        self.is_trained = False

    def _extract_features(self, api: API, session: Session) -> np.ndarray:
        """
        Extract ML features from an API.

        Features:
        1. days_since_last_call: Time since last traffic (0-365 normalized)
        2. documentation_score: 0-1 (has OpenAPI spec)
        3. auth_mechanism_score: 0-1 (OAuth/mTLS/API key present)
        4. orphan_dependency_ratio: 0-1 (% of dependencies that don't depend on this API)
        5. security_violations_count: 0-N (OWASP findings)
        6. response_time_ms: API response time in milliseconds (normalized)
        7. error_rate_percent: 0-100 (% of failed requests)
        8. dependent_api_count: N (how many APIs depend on this one)
        """
        # Days since last call
        now = datetime.now(timezone.utc)
        last_call = api.last_traffic_seen or api.created_at
        days_since = max(0, (now - last_call).days)
        days_since_norm = min(days_since / 365.0, 1.0)  # Cap at 1 year

        # Documentation score (1 if OpenAPI spec present)
        doc_score = 1.0 if api.has_documentation else 0.0

        # Auth mechanism score (1 if auth present)
        security = session.query(APISecurityPosture).filter_by(api_id=api.id).first()
        auth_score = 1.0 if (security and security.has_authentication) else 0.0

        # Orphan dependency ratio
        dependents = session.query(Dependency).filter_by(target_api_id=api.id).count()
        total_deps = 0
        orphan_ratio = 0.0 if total_deps == 0 else 1.0 - (dependents / (total_deps + 1))

        # Security violations
        violations = 0
        if security:
            if not security.has_authentication:
                violations += 1
            if not security.uses_https:
                violations += 1
            if not security.has_rate_limiting:
                violations += 1
            if security.exposes_sensitive_data:
                violations += 1

        # Response time
        response_time = api.average_response_time_ms
        response_time_norm = min(response_time / 1000.0, 1.0)

        # Error rate
        error_rate = api.error_rate_percent

        # Dependent API count
        dependent_count = dependents

        return np.array([
            days_since_norm,
            doc_score,
            auth_score,
            orphan_ratio,
            float(violations),
            response_time_norm,
            error_rate / 100.0,
            float(dependent_count) / 25.0  # Normalize by expected API count
        ])

    def train(self, session: Session) -> None:
        """
        Train the Isolation Forest model on all APIs in database.

        Training data: feature vectors from all APIs
        Contamination: 0.3 (expect ~30% "anomalous" APIs that are zombie/deprecated)
        """
        apis = session.query(API).all()
        if len(apis) < 5:
            # Not enough data, use heuristic fallback
            self.is_trained = False
            return

        features_list = [self._extract_features(api, session) for api in apis]
        X = np.array(features_list)

        # Normalize features
        X_scaled = self.scaler.fit_transform(X)

        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=0.3,  # Expect 30% anomalies (zombie/deprecated APIs)
            random_state=42,
            n_estimators=100,
            max_samples="auto"
        )
        self.model.fit(X_scaled)
        self.is_trained = True

    def calculate_zombie_score(self, api: API, session: Session) -> Tuple[float, Dict]:
        """
        Calculate zombie score (0-1) using ML model.

        Returns:
            - score: 0-1 (higher = more likely zombie)
            - metadata: dict with feature importance and anomaly flags
        """
        if not self.is_trained:
            # Fallback to heuristic if model not trained
            return self._heuristic_score(api, session)

        features = self._extract_features(api, session)
        features_scaled = self.scaler.transform([features])[0]

        # Get anomaly score (-1 to 1, where 1 = strong anomaly)
        anomaly_score = self.model.score_samples([features_scaled])[0]
        # Convert to 0-1 zombie probability
        zombie_score = (1.0 - anomaly_score) / 2.0
        zombie_score = max(0.0, min(1.0, zombie_score))

        # Extract feature contributions
        feature_dict = {
            name: float(val) for name, val in zip(self.feature_names, features)
        }

        metadata = {
            "features": feature_dict,
            "anomaly_score": float(anomaly_score),
            "model_type": "isolation_forest",
            "is_anomaly": anomaly_score > -0.5
        }

        return zombie_score, metadata

    def _heuristic_score(self, api: API, session: Session) -> Tuple[float, Dict]:
        """
        Fallback heuristic scoring (original Day 3.1 logic).
        Used when ML model not trained.
        """
        now = datetime.now(timezone.utc)
        last_call = api.last_traffic_seen or api.created_at
        days_since = (now - last_call).days

        # Traffic decay: 90%+ if >180 days
        traffic_decay = min(days_since / 180.0, 1.0)

        # Documentation: 0 if no spec
        documentation = 1.0 if api.has_documentation else 0.0

        # Auth weakness
        security = session.query(APISecurityPosture).filter_by(api_id=api.id).first()
        auth_weakness = 1.0 if (not security or not security.has_authentication) else 0.0

        # Orphan dependency
        dependents = session.query(Dependency).filter_by(target_api_id=api.id).count()
        total_deps = 0
        orphan = 1.0 if (total_deps > 0 and dependents == 0) else 0.0

        # Weighted formula
        score = (
            0.35 * traffic_decay +
            0.25 * documentation +
            0.20 * auth_weakness +
            0.20 * orphan
        )

        return score, {
            "model_type": "heuristic_fallback",
            "traffic_decay": float(traffic_decay),
            "documentation": float(documentation),
            "auth_weakness": float(auth_weakness),
            "orphan": float(orphan)
        }

    def classify_api(self, zombie_score: float) -> str:
        """Classify API based on zombie score."""
        if zombie_score < 0.3:
            return "ACTIVE"
        elif zombie_score < 0.6:
            return "DEPRECATED"
        else:
            return "ZOMBIE"


# Global scorer instance
_scorer = IsolationForestScorer()


def get_scorer() -> IsolationForestScorer:
    """Get global scorer instance."""
    return _scorer


def train_model(session: Session) -> None:
    """Train the ML model on current database."""
    _scorer.train(session)
