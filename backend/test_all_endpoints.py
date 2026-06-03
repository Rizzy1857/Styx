import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.api.endpoints import (
    analytics, apis, alerts, dependencies, health, scoring, simulator
)

db = SessionLocal()

print("Testing all endpoints:")
try:
    print("Testing /zombie-trend")
    analytics.get_zombie_trend(db)
    print("Testing /distribution")
    analytics.get_api_distribution(db)
    print("Testing /risk-heatmap")
    analytics.get_risk_heatmap(db)
    print("Testing /top-at-risk")
    analytics.get_top_at_risk(db=db)
    print("Testing /apis")
    apis_list = apis.list_apis(db)
    print("Testing /alerts")
    alerts_list = alerts.get_alerts(db=db)
    print("Testing /health")
    health.health_check(db=db)
    if apis_list:
        api_id = str(apis_list[0].id)
        print("Testing /apis/{api_id}")
        apis.get_api(api_id, db)
        print("Testing /apis/{api_id}/score")
        scoring.get_api_score(api_id, db)
        print("Testing /apis/{api_id}/dependencies")
        dependencies.get_dependencies(api_id, db)
    
    print("All tested functions OK")
except Exception as e:
    import traceback; traceback.print_exc()
