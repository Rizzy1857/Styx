from fastapi import FastAPI, Response
import random
import asyncio

app = FastAPI(title="Styx Mock Upstream Services")

async def simulate_processing():
    """Simulate variable processing time to make metrics look realistic."""
    delay = random.uniform(0.01, 0.15)
    await asyncio.sleep(delay)

@app.get("/api/v1/payment")
async def get_payment():
    await simulate_processing()
    return {"status": "success", "data": "payment details"}

@app.post("/api/v1/payment")
async def create_payment():
    await simulate_processing()
    if random.random() < 0.05:  # 5% error rate
        return Response(status_code=500, content='{"error": "Internal Server Error"}', media_type="application/json")
    return {"status": "created"}

@app.get("/api/v1/user/profile")
async def get_profile():
    await simulate_processing()
    return {"id": "usr_123", "name": "Test User"}

@app.post("/api/v1/auth/login")
async def login():
    await simulate_processing()
    if random.random() < 0.1: # 10% error rate
        return Response(status_code=401, content='{"error": "Unauthorized"}', media_type="application/json")
    return {"token": "mock_jwt_token"}

@app.get("/api/v1/limits")
async def get_limits():
    await simulate_processing()
    return {"limit": 50000}

@app.get("/internal/v1/legacy/customer-dump")
async def legacy_customer_dump():
    # Simulate a slow, heavy legacy endpoint
    await asyncio.sleep(random.uniform(0.5, 1.2))
    return {"data": ["customer1", "customer2", "customer3"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
