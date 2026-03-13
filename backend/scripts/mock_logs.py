import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

random.seed(42)


def random_timestamp_within(days: int) -> str:
    age_days = random.triangular(0, days, 8)
    age_seconds = age_days * 24 * 60 * 60
    ts = datetime.now(timezone.utc) - timedelta(seconds=age_seconds)
    return ts.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_gateway_logs(count: int) -> list[dict]:
    endpoints = [
        "/api/v1/payment",
        "/api/v2/credit-score",
        "/api/v1/kyc/verify",
        "/api/v1/accounts/balance",
        "/api/v1/transactions",
        "/api/v1/notifications/sms",
        "/api/v1/payouts/initiate",
    ]
    services = [
        "loan-processor",
        "fraud-engine",
        "mobile-app",
        "web-portal",
        "partner-gateway",
    ]
    methods = ["GET", "POST", "PUT"]

    rows: list[dict] = []
    for _ in range(count):
        endpoint = random.choice(endpoints)
        method = random.choice(methods)
        response_code = random.choices([200, 201, 204, 400, 401, 404, 429, 500], weights=[45, 8, 10, 8, 8, 5, 10, 6], k=1)[0]
        rows.append(
            {
                "timestamp": random_timestamp_within(90),
                "source_service": random.choice(services),
                "endpoint": endpoint,
                "method": method,
                "response_code": response_code,
                "has_auth": random.random() > 0.15,
                "protocol": "https" if random.random() > 0.1 else "http",
            }
        )
    return rows


def generate_vpc_flows(count: int) -> list[dict]:
    destinations = ["10.20.1.10", "10.20.1.11", "10.20.2.9", "10.20.3.44"]
    protocols = ["TCP", "UDP"]
    rows: list[dict] = []

    for _ in range(count):
        rows.append(
            {
                "timestamp": random_timestamp_within(90),
                "source_ip": f"10.0.{random.randint(1, 25)}.{random.randint(2, 254)}",
                "destination_ip": random.choice(destinations),
                "destination_port": random.choice([80, 443, 8080, 8443]),
                "protocol": random.choice(protocols),
                "bytes": random.randint(200, 250000),
                "packets": random.randint(2, 2000),
                "inferred_endpoint": random.choice([
                    "/api/v2/credit-score",
                    "/api/v1/payment",
                    "/api/v1/transactions",
                    "/internal/v1/legacy/customer-dump",
                ]),
            }
        )

    return rows


def write_json(path: Path, payload: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    gateway_path = root / "data" / "gateway_logs.json"
    vpc_path = root / "data" / "vpc_flows.json"

    gateway_logs = generate_gateway_logs(1000)
    vpc_flows = generate_vpc_flows(200)

    write_json(gateway_path, gateway_logs)
    write_json(vpc_path, vpc_flows)

    print(f"Generated {len(gateway_logs)} gateway logs -> {gateway_path}")
    print(f"Generated {len(vpc_flows)} VPC flow logs -> {vpc_path}")


if __name__ == "__main__":
    main()
