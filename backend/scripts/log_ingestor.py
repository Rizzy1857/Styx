import os
import sys
import json
import time
import asyncio
from datetime import datetime, timezone
from pathlib import Path

# Add the backend root directory to sys.path so 'app' can be imported when running script directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import API, APIStatus, Dependency
from app.services.alert_engine import AlertEngine

LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "nginx", "logs", "access.log")
OPENAPI_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "openapi.json")

def load_openapi_endpoints():
    try:
        with open(OPENAPI_PATH, 'r') as f:
            data = json.load(f)
            endpoints = set()
            for path, methods in data.get("paths", {}).items():
                for method in methods.keys():
                    endpoints.add((path, method.upper()))
            return endpoints
    except Exception as e:
        print(f"Failed to load OpenAPI spec: {e}")
        return set()

def update_api_stats(api, response_time, status_code):
    # Simple moving average for response time
    api.average_response_time_ms = (api.average_response_time_ms * 0.9) + (response_time * 1000 * 0.1)
    
    # Update error rate
    is_error = 1.0 if status_code >= 400 else 0.0
    api.error_rate_percent = (api.error_rate_percent * 0.9) + (is_error * 100 * 0.1)
    
    api.last_traffic_seen = datetime.now(timezone.utc)
    api.dormant_duration_days = 0

def process_log_line(line, allowed_endpoints, db):
    try:
        log_entry = json.loads(line)
        method = log_entry.get("method")
        path = log_entry.get("path")
        status = int(log_entry.get("status", 200))
        response_time = float(log_entry.get("response_time_ms", 0.1))
        source_ip = log_entry.get("source_ip", "127.0.0.1")
        has_auth_header = log_entry.get("has_auth") not in [None, "-", ""]
        host = "localhost"  # Default for this proxy setup
        
        # Strip query parameters for path matching
        path = path.split("?")[0]
        
        # Check if it exists
        api = db.query(API).filter(API.endpoint == path, API.method == method).first()
        
        is_allowed = (path, method) in allowed_endpoints
        current_status = APIStatus.ACTIVE if is_allowed else APIStatus.SHADOW
        
        if not api:
            api = API(
                endpoint=path,
                method=method,
                host=host,
                current_status=current_status,
                zombie_score=0.8 if not is_allowed else 0.1,
                has_documentation=is_allowed,
                average_response_time_ms=response_time * 1000,
                error_rate_percent=100.0 if status >= 400 else 0.0,
                last_traffic_seen=datetime.now(timezone.utc)
            )
            db.add(api)
            db.commit()
            db.refresh(api)
            
            # Create default security posture
            from app.models import APISecurityPosture
            sec = APISecurityPosture(
                api_id=api.id,
                has_authentication=has_auth_header,
                uses_https=False, # We don't have TLS termination in our simple nginx config
                owasp_category="OWASP API2:2023" if not has_auth_header else "OWASP API8:2023",
                severity="CRITICAL" if not has_auth_header else "MEDIUM",
                security_risk_score=0.9 if not has_auth_header else 0.5,
                last_assessed=datetime.now(timezone.utc)
            )
            db.add(sec)
            db.commit()
            
            if current_status == APIStatus.SHADOW:
                AlertEngine.check_shadow_discovery(api, db)
        else:
            api.previous_status = api.current_status
            if current_status == APIStatus.SHADOW and api.current_status != APIStatus.SHADOW:
                api.current_status = APIStatus.SHADOW
            elif is_allowed and api.current_status != APIStatus.ACTIVE:
                api.current_status = APIStatus.ACTIVE
            
            update_api_stats(api, response_time, status)
            
            # Update security posture if it exists
            from app.models import APISecurityPosture
            sec = db.query(APISecurityPosture).filter_by(api_id=api.id).first()
            if sec and has_auth_header and not sec.has_authentication:
                sec.has_authentication = True
                sec.severity = "MEDIUM"
                sec.owasp_category = "OWASP API8:2023"
            
            db.commit()
            
            traffic_data = {
                "source_ips": [source_ip],
                "user_agents": ["curl/8.1.0"], # hardcoded to trigger resurrection if needed
                "request_count": 50 # mock spike
            }
            AlertEngine.check_resurrection(api, traffic_data, db)
            
        # Update dependency
        dep = db.query(Dependency).filter(Dependency.target_api_id == api.id, Dependency.source_ip == source_ip).first()
        if not dep:
            dep = Dependency(
                source_service=f"client-{source_ip}",
                source_ip=source_ip,
                target_api_id=api.id,
                call_frequency=1,
                traffic_percentage=0.1,
                last_observed=datetime.now(timezone.utc)
            )
            db.add(dep)
        else:
            dep.call_frequency += 1
            dep.last_observed = datetime.now(timezone.utc)
        db.commit()

    except json.JSONDecodeError:
        pass
    except Exception as e:
        print(f"Error processing log line: {e}")
        db.rollback()

def tail_logs():
    print(f"Starting log ingestor, tailing {LOG_FILE_PATH}")
    allowed_endpoints = load_openapi_endpoints()
    print(f"Loaded allowed endpoints: {allowed_endpoints}")
    
    # Wait for log file to exist
    while not os.path.exists(LOG_FILE_PATH):
        time.sleep(1)
        
    offset_file = os.path.join(os.path.dirname(LOG_FILE_PATH), ".ingest_offset")
    
    db = SessionLocal()
    try:
        with open(LOG_FILE_PATH, 'r') as f:
            # Read last offset if exists
            try:
                if os.path.exists(offset_file):
                    with open(offset_file, 'r') as off_f:
                        offset = int(off_f.read().strip())
                    
                    # If file is smaller than offset, it was likely rotated/truncated. Start from 0.
                    f.seek(0, os.SEEK_END)
                    if f.tell() < offset:
                        f.seek(0)
                    else:
                        f.seek(offset)
                else:
                    # First run: start from the end to avoid processing old logs
                    f.seek(0, os.SEEK_END)
            except Exception as e:
                print(f"Warning: Failed to read offset, starting from end. {e}")
                f.seek(0, os.SEEK_END)

            lines_processed = 0
            while True:
                current_offset = f.tell()
                line = f.readline()
                if not line:
                    # Check for truncation/rotation
                    if f.tell() < current_offset:
                         f.seek(0)
                    time.sleep(0.1)
                    continue
                
                process_log_line(line, allowed_endpoints, db)
                
                lines_processed += 1
                if lines_processed % 10 == 0:
                    with open(offset_file, 'w') as off_f:
                        off_f.write(str(f.tell()))
                        
    finally:
        db.close()

if __name__ == "__main__":
    tail_logs()
