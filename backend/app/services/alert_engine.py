"""
Alert Engine

Detects resurrection events when zombie/shadow APIs receive traffic,
identifies security anomalies, and creates actionable alerts.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.models import API, Alert, AlertType


class AlertEngine:
    """Detect and create alerts for API lifecycle events."""

    @staticmethod
    def check_resurrection(
        api: API, traffic_data: Dict[str, Any], session: Session
    ) -> Optional[Alert]:
        """
        Detect resurrection when zombie/shadow API receives traffic.

        Creates alert if:
        - API was previously ZOMBIE/SHADOW
        - Traffic spike detected (> 3x historical mean in 1hr)
        - New source IPs observed
        - Suspicious user agents detected

        Returns:
            Alert object or None
        """
        # Only trigger on status transition from ZOMBIE/SHADOW
        if api.previous_status not in ["ZOMBIE", "SHADOW", None]:
            return None

        triggers = []
        metadata = {
            "source_ips": traffic_data.get("source_ips", []),
            "user_agents": traffic_data.get("user_agents", []),
            "triggers": [],
        }

        # Check for traffic spike
        if traffic_data.get("request_count", 0) > 30:  # Threshold for 1-hour window
            triggers.append("traffic_spike")

        # Check for new source IPs
        if len(set(traffic_data.get("source_ips", []))) >= 5:
            triggers.append("new_caller_ips")

        # Check for suspicious user agents
        suspicious_patterns = ["<?php", "curl", "python-requests", "bot", "scraper"]
        user_agents = traffic_data.get("user_agents", [])
        for ua in user_agents:
            if any(pattern.lower() in ua.lower() for pattern in suspicious_patterns):
                triggers.append("malicious_ua")
                break

        if not triggers:
            return None

        metadata["triggers"] = triggers

        alert = Alert(
            api_id=api.id,
            alert_type=AlertType.ZOMBIE_RESURRECTION,
            trigger_metadata=metadata,
            previous_dormant_days=api.dormant_duration_days,
            severity="CRITICAL" if "malicious_ua" in triggers else "HIGH",
            acknowledged=False,
        )

        session.add(alert)
        return alert

    @staticmethod
    def check_shadow_discovery(api: API, session: Session) -> Optional[Alert]:
        """
        Create alert when shadow API is discovered via VPC flow.

        Returns:
            Alert object or None
        """
        if api.current_status != "SHADOW":
            return None

        # Check if already alerted for this API recently
        existing = (
            session.query(Alert)
            .filter_by(api_id=api.id, alert_type=AlertType.SHADOW_DISCOVERED)
            .first()
        )
        if existing:
            return None

        alert = Alert(
            api_id=api.id,
            alert_type=AlertType.SHADOW_DISCOVERED,
            trigger_metadata={
                "discovery_method": "vpc_flow",
                "reason": "Endpoint discovered in VPC flow logs but not in gateway logs",
            },
            severity="MEDIUM",
            acknowledged=False,
        )

        session.add(alert)
        return alert

    @staticmethod
    def check_security_violation(
        api: API, security_finding: Dict[str, Any], session: Session
    ) -> Optional[Alert]:
        """
        Create alert for critical security findings.

        Returns:
            Alert object or None
        """
        # Only create alert for CRITICAL findings
        if security_finding.get("severity") != "CRITICAL":
            return None

        # Check if already alerted
        existing = (
            session.query(Alert)
            .filter_by(api_id=api.id, alert_type=AlertType.SECURITY_VIOLATION)
            .first()
        )
        if existing:
            return None

        alert = Alert(
            api_id=api.id,
            alert_type=AlertType.SECURITY_VIOLATION,
            trigger_metadata={
                "category": security_finding.get("category"),
                "cvss_score": security_finding.get("cvss_score"),
                "description": security_finding.get("description"),
            },
            severity="CRITICAL",
            acknowledged=False,
        )

        session.add(alert)
        return alert

    @staticmethod
    def traffic_spike_detected(
        current_traffic: int, historical_mean: Optional[int] = None
    ) -> bool:
        """
        Detect traffic spike: current > 3 * historical_mean.

        Args:
            current_traffic: Request count in current window
            historical_mean: Mean request count from last 30 days

        Returns:
            True if spike detected
        """
        if historical_mean is None or historical_mean == 0:
            return current_traffic > 30  # Absolute threshold

        return current_traffic > (3 * historical_mean)
