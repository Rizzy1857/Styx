# Styx Backend

This directory contains the FastAPI application, Postgres database models, and the live log ingestion pipeline.

## Architecture (Hackathon Demo State)

Styx currently operates using a **Gateway Log Tailing** architecture to simulate a live traffic environment for demonstration purposes:
- **Nginx Reverse Proxy:** Fronts mock API services and logs all traffic as structured JSON.
- **Log Ingestor (`scripts/log_ingestor.py`):** A daemon that tails the Nginx logs, calculates latency/error metrics, and upserts APIs into Postgres.
- **Traffic Loop (`scripts/traffic_loop.py`):** Generates synthetic HTTP load against the Nginx gateway, including rogue/shadow API calls to trigger alerts.
- **FastAPI Core:** Serves this data via REST and Server-Sent Events (SSE) to the frontend.

## Quick Start (Live Pipeline)

1. **Start the Infrastructure (Nginx, Mock Services, Postgres):**
   ```bash
   # From the project root
   docker-compose up -d
   ```

2. **Setup Python Environment:**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run Database Migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start the Live Pipeline (Requires 3 Terminals):**

   **Terminal 1 (FastAPI Server):**
   ```bash
   source .venv/bin/activate
   uvicorn app.main:app --reload --port 8000
   ```

   **Terminal 2 (Log Ingestor):**
   ```bash
   source .venv/bin/activate
   python scripts/log_ingestor.py
   ```

   **Terminal 3 (Traffic Generator):**
   ```bash
   source .venv/bin/activate
   python scripts/traffic_loop.py
   ```

The backend API will now be running on `http://localhost:8000`, continuously processing simulated live traffic from Nginx.
