"""
Generate realistic attack traffic for zombie API resurrection demo.

Creates 50 malicious requests with:
- Random TOR exit node IPs and internal IPs
- Malicious user agents
- Irregular timing
- Mixed authentication states
"""

import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models import API, APIStatus
from app.services.alert_engine import AlertEngine

fake = Faker()
Faker.seed(42)
random.seed(42)

# Configuration
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "attack_traffic.json"
OUTPUT_FILE.parent.mkdir(exist_ok=True)

# Realistic attack patterns
ATTACKER_IPS = [
    "185.220.101.1",
    "185.220.101.45",
    "185.220.101.87",
    "185.220.102.12",
    "10.0.3.14",
    "10.0.3.92",
    "172.16.5.8",
    "192.168.1.100",
]

MALICIOUS_USER_AGENTS = [
    "<?php system($_GET['cmd']); ?>",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit (compatible; sqlmap/1.3.8)",
    "curl/7.68.0",
    "python-requests/2.25.1",
    "nmap-ncat",
    "wget/1.20.3",
    "",  # Empty UA
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
]

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

RESPONSE_CODES = [200, 400, 401, 403, 429, 500]

TARGET_ENDPOINT = "/api/v2/credit-score"
TARGET_SERVICE = "zombie-api-test"


def generate_attack_traffic(num_requests: int = 50) -> list:
    """Generate realistic attack traffic."""
    now = datetime.utcnow()
    traffic = []

    for i in range(num_requests):
        # Random timing (concentrated burst - attack pattern)
        offset = timedelta(seconds=random.randint(-3600, 0))
        timestamp = (now + offset).isoformat() + "Z"

        request = {
            "timestamp": timestamp,
            "source_ip": random.choice(ATTACKER_IPS),
            "source_service": f"attacker-{random.randint(1, 5)}",
            "endpoint": TARGET_ENDPOINT,
            "method": random.choice(HTTP_METHODS),
            "response_code": random.choice(RESPONSE_CODES),
            "user_agent": random.choice(MALICIOUS_USER_AGENTS),
            "has_auth": random.choice([True, False]),
            "auth_token": f"bearer_{fake.sha1()}" if random.random() > 0.5 else None,
            "protocol": "https" if random.random() > 0.3 else "http",
            "request_size": random.randint(100, 5000),
            "response_time_ms": random.randint(50, 3000),
        }

        traffic.append(request)

    return traffic


def main():
    """Generate and save attack traffic."""
    print("Generating attack traffic...")
    traffic = generate_attack_traffic()

    # Save to JSON
    OUTPUT_FILE.write_text(json.dumps(traffic, indent=2))
    print(f"✓ Generated {len(traffic)} attack requests")
    print(f"✓ Saved to {OUTPUT_FILE}")

    # Print summary
    ips = set(t["source_ip"] for t in traffic)
    uas = set(t["user_agent"] for t in traffic)
    print(f"\n📊 Attack Profile:")
    print(f"   Unique IPs: {len(ips)}")
    print(f"   Unique User Agents: {len(uas)}")
    print(f"   Target: {TARGET_ENDPOINT}")

    # Trigger resurrection alert in DB
    source_ips = [entry["source_ip"] for entry in traffic]
    user_agents = [entry["user_agent"] for entry in traffic]
    traffic_payload = {
        "request_count": len(traffic),
        "source_ips": source_ips,
        "user_agents": user_agents,
    }

    db = SessionLocal()
    try:
        target_api = (
            db.query(API)
            .filter(API.endpoint == TARGET_ENDPOINT)
            .order_by(API.created_at.desc())
            .first()
        )
        if target_api is None:
            print("\n⚠️  No matching API in DB; attack file generated only.")
            return

        target_api.previous_status = target_api.current_status.value if hasattr(target_api.current_status, "value") else str(target_api.current_status)
        target_api.current_status = APIStatus.ACTIVE
        target_api.status_changed_at = datetime.utcnow()

        alert = AlertEngine.check_resurrection(target_api, traffic_payload, db)
        db.commit()
        if alert:
            print(f"\n🚨 Resurrection alert created: {alert.id}")
        else:
            print("\nℹ️  Attack generated, but no alert trigger conditions matched.")
    except Exception as e:
        print(f"\n⚠️  Alert creation error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
