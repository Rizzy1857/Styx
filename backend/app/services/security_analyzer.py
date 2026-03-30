"""
Security Posture Analyzer

Analyzes APIs against OWASP API Security Top 10 2023 and assigns
CVSS scores and severity levels based on security configuration.
"""

from typing import Dict, List, Any
from app.models import API, APISecurityPosture, SeverityLevel


class SecurityAnalyzer:
    """Analyze API security posture against OWASP standards."""

    OWASP_MAPPINGS = {
        "no_auth": {
            "category": "OWASP API2:2023 - Broken Authentication",
            "cvss_score": 9.1,
            "severity": SeverityLevel.CRITICAL,
        },
        "http_only": {
            "category": "OWASP API8:2023 - Security Misconfiguration",
            "cvss_score": 7.5,
            "severity": SeverityLevel.HIGH,
        },
        "no_rate_limit": {
            "category": "OWASP API4:2023 - Unrestricted Resource Consumption",
            "cvss_score": 6.5,
            "severity": SeverityLevel.MEDIUM,
        },
        "pii_exposure": {
            "category": "OWASP API3:2023 - Excessive Data Exposure",
            "cvss_score": 8.0,
            "severity": SeverityLevel.HIGH,
        },
        "zombie_no_docs": {
            "category": "OWASP API5:2023 - Broken Object Level Authorization",
            "cvss_score": 6.8,
            "severity": SeverityLevel.MEDIUM,
        },
    }

    @staticmethod
    def analyze_security(api: API, security: APISecurityPosture) -> Dict[str, Any]:
        """
        Perform security analysis on an API.

        Returns:
            {
                "findings": [
                    {
                        "category": "OWASP API2:2023",
                        "cvss_score": 9.1,
                        "severity": "CRITICAL",
                        "description": "..."
                    }
                ],
                "security_risk_score": float (0-1),
                "highest_severity": str
            }
        """
        findings = []

        # Check for missing authentication
        if not security.has_authentication:
            findings.append({
                "category": SecurityAnalyzer.OWASP_MAPPINGS["no_auth"]["category"],
                "cvss_score": SecurityAnalyzer.OWASP_MAPPINGS["no_auth"]["cvss_score"],
                "severity": SecurityAnalyzer.OWASP_MAPPINGS["no_auth"]["severity"].value,
                "description": "API lacks authentication mechanism. Any caller can access endpoints.",
            })

        # Check for HTTP-only
        if not security.uses_https:
            findings.append({
                "category": SecurityAnalyzer.OWASP_MAPPINGS["http_only"]["category"],
                "cvss_score": SecurityAnalyzer.OWASP_MAPPINGS["http_only"]["cvss_score"],
                "severity": SecurityAnalyzer.OWASP_MAPPINGS["http_only"]["severity"].value,
                "description": "API uses HTTP without encryption. Traffic is exposed in transit.",
            })

        # Check for rate limiting
        if not security.has_rate_limiting:
            findings.append({
                "category": SecurityAnalyzer.OWASP_MAPPINGS["no_rate_limit"]["category"],
                "cvss_score": SecurityAnalyzer.OWASP_MAPPINGS["no_rate_limit"]["cvss_score"],
                "severity": SecurityAnalyzer.OWASP_MAPPINGS["no_rate_limit"]["severity"].value,
                "description": "API lacks rate limiting. Vulnerable to DoS and brute force attacks.",
            })

        # Check for PII exposure
        if security.exposes_sensitive_data:
            findings.append({
                "category": SecurityAnalyzer.OWASP_MAPPINGS["pii_exposure"]["category"],
                "cvss_score": SecurityAnalyzer.OWASP_MAPPINGS["pii_exposure"]["cvss_score"],
                "severity": SecurityAnalyzer.OWASP_MAPPINGS["pii_exposure"]["severity"].value,
                "description": "API returns sensitive PII without proper field-level encryption.",
            })

        # Check for zombie without documentation
        if api.current_status == "ZOMBIE" and not api.has_documentation:
            findings.append({
                "category": SecurityAnalyzer.OWASP_MAPPINGS["zombie_no_docs"]["category"],
                "cvss_score": SecurityAnalyzer.OWASP_MAPPINGS["zombie_no_docs"]["cvss_score"],
                "severity": SecurityAnalyzer.OWASP_MAPPINGS["zombie_no_docs"]["severity"].value,
                "description": "Zombie API with no documentation increases risk of unauthorized access.",
            })

        # Calculate risk score as max CVSS / 10.0
        if findings:
            max_cvss = max(f["cvss_score"] for f in findings)
            security_risk_score = min(max_cvss / 10.0, 1.0)
            highest_severity = findings[0]["severity"]
            for f in findings:
                sev_order = {
                    "CRITICAL": 4,
                    "HIGH": 3,
                    "MEDIUM": 2,
                    "LOW": 1,
                }
                if sev_order.get(f["severity"], 0) > sev_order.get(highest_severity, 0):
                    highest_severity = f["severity"]
        else:
            security_risk_score = 0.0
            highest_severity = "LOW"

        return {
            "findings": findings,
            "security_risk_score": round(security_risk_score, 3),
            "highest_severity": highest_severity,
        }
