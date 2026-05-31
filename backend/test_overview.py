import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.api.endpoints.analytics import get_analytics_overview

db = SessionLocal()

print("Testing analytics overview:")
try:
    overview = get_analytics_overview(db)
    print("Overview OK")
except Exception as e:
    import traceback; traceback.print_exc()
