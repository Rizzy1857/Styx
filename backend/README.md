# Styx Backend (Day 1)

This folder contains the Day 1 MVP foundation:

- SQLAlchemy models + Alembic migration
- FastAPI skeleton with `/health`
- Data seed and mock log generation scripts

## Quick Start

1. Create and activate a virtual environment.
1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Configure environment:

```bash
cp .env.example .env
```

1. Run migration:

```bash
alembic upgrade head
```

1. Seed demo data and generate logs:

```bash
python scripts/seed_data.py
python scripts/mock_logs.py
```

1. Start API server:

```bash
uvicorn main:app --reload
```

## Endpoints

- `GET /health`
