# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-03-13

### Added

- `CHANGELOG.md` to track project history.
- `.gitignore` for Python, venv, generated data files, and `.env`.
- `backend/requirements.txt` with pinned dependencies: FastAPI, Uvicorn, SQLAlchemy, Alembic, psycopg2-binary, Pydantic, NetworkX, Faker.
- `backend/main.py` — FastAPI application with CORS middleware (allowing `localhost:5173`), lifespan startup DB check, and router inclusion.
- `backend/app/core/config.py` — Pydantic `Settings` class reading `DATABASE_URL`, `DEBUG`, and `SECRET_KEY` from `.env`.
- `backend/app/core/database.py` — SQLAlchemy engine, `SessionLocal` factory, and `get_db()` dependency.
- `backend/app/api/endpoints/health.py` — `GET /health` endpoint returning `{"status": "healthy", "database": "connected"}`.
- `backend/app/api/router.py` — top-level API router wiring health endpoint.
- `backend/app/models/base.py` — SQLAlchemy `DeclarativeBase`.
- `backend/app/models/api.py` — `API` and `TrafficSource` models with enums `APIStatus` (ACTIVE, DEPRECATED, ZOMBIE, SHADOW) and `TrafficSourceType`.
- `backend/app/models/security.py` — `APISecurityPosture` model with `SeverityLevel` enum (CRITICAL, HIGH, MEDIUM, LOW).
- `backend/app/models/dependency.py` — `Dependency` model tracking service → API call edges.
- `backend/app/models/alert.py` — `Alert` model with `AlertType` enum (ZOMBIE_RESURRECTION, SHADOW_DISCOVERED, SECURITY_VIOLATION) and JSONB `trigger_metadata`.
- `backend/alembic/versions/001_initial_schema.py` — initial Alembic migration creating all five tables (`apis`, `api_security_posture`, `traffic_sources`, `dependencies`, `alerts`) with indexes and enum types.
- `backend/alembic/env.py` and `backend/alembic.ini` — Alembic configuration wired to `Settings.DATABASE_URL`.
- `backend/scripts/seed_data.py` — seeds 25 APIs (15 ACTIVE, 5 DEPRECATED, 3 ZOMBIE, 2 SHADOW) with security posture, traffic sources, 40 dependency edges, and 3 pre-seeded resurrection alerts.
- `backend/scripts/mock_logs.py` — generates 1000 gateway log entries and 200 VPC flow entries to `backend/data/`.
- `backend/.env.example` — template environment file.
- `backend/README.md` — quick-start guide for backend setup.
