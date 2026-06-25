import time
import random
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NGINX_URL = "http://localhost:8080"

ENDPOINTS = [
    {"method": "GET", "path": "/api/v1/payment", "weight": 20},
    {"method": "POST", "path": "/api/v1/payment", "weight": 10},
    {"method": "GET", "path": "/api/v1/user/profile", "weight": 30},
    {"method": "POST", "path": "/api/v1/auth/login", "weight": 25},
    {"method": "GET", "path": "/api/v1/limits", "weight": 10},
    {"method": "GET", "path": "/internal/v1/legacy/customer-dump", "weight": 5} # The "Rogue" endpoint
]

def choose_endpoint():
    total_weight = sum(ep["weight"] for ep in ENDPOINTS)
    r = random.uniform(0, total_weight)
    upto = 0
    for ep in ENDPOINTS:
        if upto + ep["weight"] >= r:
            return ep
        upto += ep["weight"]
    return ENDPOINTS[0]

def run_loop():
    print(f"Starting traffic loop targeting {NGINX_URL}...")
    while True:
        ep = choose_endpoint()
        url = f"{NGINX_URL}{ep['path']}"
        headers = {}
        if random.random() > 0.3:
            headers["Authorization"] = "Bearer token123"

        try:
            if ep["method"] == "GET":
                requests.get(url, headers=headers, timeout=2)
            else:
                requests.post(url, headers=headers, json={}, timeout=2)
            
            print(f"Sent {ep['method']} {ep['path']}")
        except Exception as e:
            print(f"Failed to hit {url}: {e}")
        
        # Sleep for a random interval to simulate real traffic
        time.sleep(random.uniform(0.1, 0.8))

if __name__ == "__main__":
    run_loop()
