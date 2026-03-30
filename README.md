# Styx - API Lifecycle Intelligence Platform

## Core Value Proposition

Help banks safely decommission risky APIs by showing what will break before you kill anything.

## System Architecture

```plaintext
┌─────────────────────────────────────────────────────────┐
│  Data Ingestion Layer                                   │
│  - API Gateway Logs (JSON)                              │
│  - VPC Flow Logs (Simulated)                            │
│  - OpenAPI Specs                                         │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  PostgreSQL Database                                     │
│  - apis, api_security_posture, traffic_sources          │
│  - dependencies, alerts, state_transitions              │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  Analysis Engines (FastAPI Backend)                     │
│  - Lifecycle Scoring (Heuristic)                        │
│  - Security Posture (OWASP/CVSS)                        │
│  - Dependency Graph (NetworkX)                          │
│  - Resurrection Detection (State-Tracking)              │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  Frontend Dashboard (React + D3.js)                     │
│  - Inventory Table                                       │
│  - Security Matrix                                       │
│  - Interactive Dependency Graph                          │
│  - Blast Radius Simulator                               │
│  - Alerts Feed                                           │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

**Backend:**

- Python 3.13
- FastAPI 0.104.1 (REST API)
- PostgreSQL 15
- SQLAlchemy 2.0.37 (ORM)
- NetworkX (Graph analysis)
- Pydantic (Data validation)
- Faker (Mock data generation)

**Frontend:**

- React 18.2.0
- Vite 5.0.0
- Tailwind CSS 3.3.5
- D3.js 7.8.5 (Dependency graph visualization)
- Recharts 2.10.3 (Timeline charts)
- Axios 1.6.2 (HTTP client)

## Quick Start

### Prerequisites

```bash
- Docker & Docker Compose (optional)
- Node.js 18+
- Python 3.13+
- PostgreSQL 15+
```

### Installation

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Running the Application

```bash
# Apply database migrations
cd backend
alembic upgrade head

# Seed mock data
python scripts/seed_data.py

# Start backend
uvicorn main:app --reload --port 8000

# Start frontend (new terminal)
cd frontend
npm run dev
```

### Access Points

- **Frontend Dashboard:** <http://localhost:5173>
- **Backend API:** <http://localhost:8000>
- **API Docs:** <http://localhost:8000/docs>
- **PostgreSQL:** localhost:5432 (user: postgres, password: postgres)

## Project Structure

```plaintext
styx/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── apis.py            # API inventory CRUD
│   │   │   │   ├── scoring.py          # Lifecycle & security scoring
│   │   │   │   ├── dependencies.py     # Graph analysis
│   │   │   │   ├── alerts.py           # Resurrection detection
│   │   │   │   └── simulator.py        # Blast radius simulation
│   │   │   └── router.py
│   │   ├── core/
│   │   │   ├── config.py               # Settings
│   │   │   └── database.py             # DB connection
│   │   ├── models/
│   │   │   ├── api.py                  # SQLAlchemy models
│   │   │   ├── security.py
│   │   │   ├── dependency.py
│   │   │   └── alert.py
│   │   ├── schemas/
│   │   │   ├── api.py                  # Pydantic schemas
│   │   │   ├── scoring.py
│   │   │   └── graph.py
│   │   └── services/
│   │       ├── lifecycle_scorer.py     # Heuristic scoring logic
│   │       ├── security_analyzer.py    # OWASP/CVSS mapping
│   │       ├── graph_builder.py        # NetworkX graph construction
│   │       └── alert_engine.py         # State-tracking alerts
│   ├── scripts/
│   │   ├── seed_data.py                # Generate mock APIs (25 + 40 dependencies)
│   │   ├── mock_logs.py                # Synthetic traffic patterns
│   │   └── generate_attack.py          # 50 malicious requests + alert trigger
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Inventory.jsx           # API list view
│   │   │   ├── APIDetail.jsx            # Single API drill-down
│   │   │   ├── Security.jsx             # 2D risk matrix
│   │   │   ├── Graph.jsx                # D3 dependency graph
│   │   │   ├── Simulator.jsx            # Blast radius calculator
│   │   │   └── Alerts.jsx               # Real-time alert feed
│   │   ├── components/
│   │   │   ├── InventoryTable.jsx      # Sortable API table
│   │   │   ├── SecurityMatrix.jsx      # 2D scatter plot
│   │   │   ├── ExplanationCard.jsx     # Score factor breakdown
│   │   │   ├── SecurityFindings.jsx    # OWASP findings
│   │   │   ├── DependencyGraph.jsx     # D3 force graph
│   │   │   ├── BlastRadiusSimulator.jsx # Multi-select impact
│   │   │   ├── AlertsFeed.jsx          # Alert polling
│   │   │   └── AlertDetail.jsx         # Alert metadata viewer
│   │   ├── services/api.js              # Axios HTTP client
│   │   └── utils/
│   │       ├── formatters.js            # Display helpers
│   │       └── d3-helpers.js            # D3 utilities
│   ├── vite.config.js
│   └── tailwind.config.js
├── CHANGELOG.md                         # Version history
├── ROADMAP.md                           # Feature roadmap
└── README.md                            # This file
```

## Key Features

### Day 1: Backend Foundation ✅

- FastAPI with OpenAPI/Swagger documentation
- PostgreSQL database with 5 core models
- Alembic migrations for schema versioning
- Seed scripts for demo data (25 APIs + 40 dependencies + synthetic traffic)

### Day 2: Frontend Scaffold ✅

- React + Vite + Tailwind CSS setup
- Sortable/filterable inventory table
- Navigation between pages

### Day 3: Scoring Services ✅

- **Lifecycle Scorer:** 4-factor weighted formula (traffic decay, documentation, auth weakness, dependency orphan)
- **Security Analyzer:** OWASP API Top 10 mapping with CVSS scores
- API classification: ACTIVE / DEPRECATED / ZOMBIE / SHADOW

### Day 4: Security Visualization ✅

- 2D Security Matrix (Lifecycle Risk vs Security Risk)
- Factor explanation cards with progress bars
- OWASP finding cards with severity badges

### Day 5: Dependency Graph ✅

- NetworkX-based graph builder
- Impact score calculation (0.6×traffic + 0.4×dependencies)
- Blast radius simulator for multi-API scenarios

### Day 6: Graph Visualization ✅

- D3.js force-directed graph with pan/zoom
- Interactive node selection and highlighting
- Simulator UI with severity recommendations

### Day 7: Real-Time Alerts ✅

- **Alert Engine:** Resurrection, shadow discovery, security violation detection
- **State Tracking:** Only fires on status transitions
- **Attack Generator:** 50 malicious requests with TOR IPs and suspicious payloads
- **Alerts UI:** Real-time polling with expandable metadata

## API Endpoints

### Core Endpoints

- `GET /api/v1/apis` — List all APIs with status and scores
- `GET /api/v1/apis/{id}` — Fetch single API with details
- `POST /api/v1/apis` — Create new API
- `PUT /api/v1/apis/{id}` — Update API
- `DELETE /api/v1/apis/{id}` — Delete API

### Scoring Endpoints

- `GET /api/v1/apis/{id}/score` — Lifecycle + security analysis

### Graph & Simulation

- `GET /api/v1/apis/{id}/dependencies` — D3.js-compatible graph
- `POST /api/v1/simulator/blast-radius` — Multi-API impact analysis

### Alerts

- `GET /api/v1/alerts` — List alerts (limit 50, newest first)
- `PATCH /api/v1/alerts/{id}/acknowledge` — Mark alert as acknowledged

## Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test

# Build validation
npm run build  # Frontend
python -m compileall backend  # Backend
```

## Deployment

See `DAYS_2-7_RUN_GUIDE.md` for comprehensive deployment and testing instructions.

## Performance Metrics

- **API Response Time:** <200ms (all endpoints)
- **Frontend Bundle:** 661KB → 196KB gzipped (with chunking)
- **D3 Graph Layout:** <3 seconds (1000+ nodes)
- **Alert Polling:** 5s interval (scalable to 1000+ alerts)

## Known Limitations

- Heuristic scoring (Phase 2: ML-based)
- In-memory graphs (Phase 2: Redis caching)
- 5s alert polling (Phase 2: WebSocket)
- No rate limiting (Phase 2: FastAPI middleware)

## Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Commit changes: `git commit -am 'feat: description'`
3. Push to branch: `git push origin feature/name`
4. Open Pull Request

## License

See LICENSE file.

## Contact

For questions or feedback:

- GitHub Issues: <https://github.com/Rizzy1857/Styx/issues>
- Email: <hrisheekeshpv@gmail.com>

---

**Status:** Days 1–7 Complete ✅  
**Last Updated:** March 30, 2026  
**Version:** 0.7.0
