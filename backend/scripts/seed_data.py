import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.core.database import SessionLocal
from app.models import (
    API,
    APISecurityPosture,
    APIStatus,
    Alert,
    AlertType,
    Dependency,
    SeverityLevel,
    TrafficSource,
    TrafficSourceType,
)

random.seed(42)


def iso_now() -> datetime:
    return datetime.now(timezone.utc)


def random_last_seen(min_days: int, max_days: int) -> tuple[datetime, int]:
    dormant_days = random.randint(min_days, max_days)
    seen_at = iso_now() - timedelta(days=dormant_days, hours=random.randint(0, 23))
    return seen_at, dormant_days


def seed_apis() -> list[API]:
    endpoint_pool = [
        "/api/v1/payment",
        "/api/v1/loan/application",
        "/api/v2/credit-score",
        "/api/v1/kyc/verify",
        "/api/v1/customer/profile",
        "/api/v1/card/tokenize",
        "/api/v2/fraud/check",
        "/api/v1/limits",
        "/api/v1/transactions",
        "/api/v2/underwriting/risk",
        "/api/v1/notifications/sms",
        "/api/v1/notifications/email",
        "/api/v2/rewards/points",
        "/api/v1/accounts/balance",
        "/api/v1/accounts/statement",
        "/api/v1/insurance/quote",
        "/api/v2/investments/eligibility",
        "/api/v1/mortgage/precheck",
        "/api/v1/collections/case",
        "/api/v1/disputes/raise",
        "/api/v2/merchant/onboarding",
        "/api/v1/wallet/topup",
        "/api/v2/identity/score",
        "/api/v1/payouts/initiate",
        "/internal/v1/legacy/customer-dump",
    ]

    methods = ["GET", "POST", "PUT"]
    apis: list[API] = []

    status_distribution = ([APIStatus.ACTIVE] * 15) + ([APIStatus.DEPRECATED] * 5) + ([APIStatus.ZOMBIE] * 3) + ([APIStatus.SHADOW] * 2)

    for index, status in enumerate(status_distribution):
        endpoint = endpoint_pool[index]
        method = random.choice(methods)
        host = random.choice(["core.styx.local", "edge.styx.local", "risk.styx.local"])

        if status == APIStatus.ACTIVE:
            last_seen, dormant_days = random_last_seen(0, 7)
            has_docs = True
            owner = random.choice(["payments-team", "risk-team", "platform-team"])
            zombie_score = round(random.uniform(0.05, 0.32), 2)
        elif status == APIStatus.DEPRECATED:
            last_seen, dormant_days = random_last_seen(30, 80)
            has_docs = True
            owner = random.choice(["legacy-team", "platform-team"])
            zombie_score = round(random.uniform(0.42, 0.68), 2)
        elif status == APIStatus.ZOMBIE:
            last_seen, dormant_days = random_last_seen(90, 120)
            has_docs = False
            owner = None
            zombie_score = round(random.uniform(0.74, 0.94), 2)
        else:
            last_seen, dormant_days = random_last_seen(10, 45)
            has_docs = False
            owner = None
            zombie_score = round(random.uniform(0.61, 0.79), 2)

        apis.append(
            API(
                endpoint=endpoint,
                method=method,
                host=host,
                current_status=status,
                previous_status="ZOMBIE" if status == APIStatus.ACTIVE and index < 3 else None,
                status_changed_at=iso_now() - timedelta(days=random.randint(1, 30)),
                zombie_score=zombie_score,
                last_traffic_seen=last_seen,
                dormant_duration_days=dormant_days,
                has_documentation=has_docs,
                owner=owner,
            )
        )

    return apis


def main() -> None:
    db = SessionLocal()

    db.execute(delete(Alert))
    db.execute(delete(Dependency))
    db.execute(delete(TrafficSource))
    db.execute(delete(APISecurityPosture))
    db.execute(delete(API))

    apis = seed_apis()
    db.add_all(apis)
    db.flush()

    for api in apis:
        insecure = api.current_status in {APIStatus.ZOMBIE, APIStatus.SHADOW}
        uses_https = not insecure or random.random() > 0.4
        has_auth = not insecure or random.random() > 0.5
        has_rate_limit = not insecure or random.random() > 0.6
        exposes_sensitive_data = insecure and random.random() > 0.4

        severity = (
            SeverityLevel.CRITICAL
            if not has_auth
            else SeverityLevel.HIGH if not uses_https or exposes_sensitive_data else SeverityLevel.MEDIUM
        )
        cvss = 9.1 if severity == SeverityLevel.CRITICAL else 7.5 if severity == SeverityLevel.HIGH else 5.9

        db.add(
            APISecurityPosture(
                api_id=api.id,
                owasp_category="OWASP API2:2023" if not has_auth else "OWASP API8:2023",
                cvss_score=cvss,
                severity=severity,
                has_authentication=has_auth,
                uses_https=uses_https,
                tls_version="TLS1.3" if uses_https else None,
                has_rate_limiting=has_rate_limit,
                exposes_sensitive_data=exposes_sensitive_data,
                security_risk_score=round(cvss / 10.0, 2),
                last_assessed=iso_now() - timedelta(days=random.randint(0, 15)),
            )
        )

        if api.current_status == APIStatus.SHADOW:
            source_types = [TrafficSourceType.VPC_FLOW]
        elif api.current_status == APIStatus.ZOMBIE:
            source_types = [TrafficSourceType.GATEWAY, TrafficSourceType.VPC_FLOW]
        else:
            source_types = [random.choice([TrafficSourceType.GATEWAY, TrafficSourceType.LOAD_BALANCER, TrafficSourceType.OPENAPI_SPEC])]

        for source_type in source_types:
            db.add(
                TrafficSource(
                    api_id=api.id,
                    source_type=source_type,
                    discovered_at=iso_now() - timedelta(days=random.randint(0, 90)),
                )
            )

    services = [
        "loan-processor",
        "fraud-engine",
        "kyc-service",
        "mobile-app",
        "web-portal",
        "statement-worker",
        "collections-bot",
        "crm-sync",
        "underwriting-orchestrator",
        "notification-hub",
        "etl-warehouse",
        "risk-proxy",
        "merchant-onboarding",
        "partner-gateway",
    ]

    for _ in range(40):
        target = random.choice(apis)
        db.add(
            Dependency(
                source_service=random.choice(services),
                source_ip=f"10.0.{random.randint(1, 20)}.{random.randint(2, 254)}",
                target_api_id=target.id,
                call_frequency=random.randint(20, 1200),
                traffic_percentage=round(random.uniform(0.01, 0.2), 3),
                last_observed=iso_now() - timedelta(hours=random.randint(1, 240)),
            )
        )

    candidate_apis = [api for api in apis if api.current_status == APIStatus.ACTIVE][:3]
    for api in candidate_apis:
        db.add(
            Alert(
                api_id=api.id,
                alert_type=AlertType.ZOMBIE_RESURRECTION,
                trigger_metadata={
                    "ips": [f"185.220.101.{random.randint(1, 254)}" for _ in range(3)],
                    "user_agents": ["curl/8.1.0", "Mozilla/5.0", "python-requests/2.31.0"],
                    "geo_regions": ["IN", "SG", "DE"],
                    "triggers": ["traffic_spike", "new_caller_ips"],
                },
                previous_dormant_days=random.randint(91, 140),
                severity="HIGH",
            )
        )

    db.commit()

    counts = {
        "ACTIVE": sum(api.current_status == APIStatus.ACTIVE for api in apis),
        "DEPRECATED": sum(api.current_status == APIStatus.DEPRECATED for api in apis),
        "ZOMBIE": sum(api.current_status == APIStatus.ZOMBIE for api in apis),
        "SHADOW": sum(api.current_status == APIStatus.SHADOW for api in apis),
    }
    print("Seed complete")
    print(f"APIs: {len(apis)} -> {counts}")
    print("Dependencies: 40")
    print("Resurrection alerts: 3")


if __name__ == "__main__":
    main()
