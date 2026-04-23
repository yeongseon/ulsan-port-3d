# Ulsan Port 3D Monitoring System

## Overview

Ulsan Port 3D Monitoring System is a production-oriented monorepo for operational monitoring of Ulsan Port through a real-time web dashboard, backend APIs, and ETL pipelines.

The platform combines public port data, berth and vessel activity, weather and tide conditions, cargo statistics, and ontology-driven graph exploration into a single operator-facing experience. The frontend renders a 3D operational view of the port, while the backend and ETL layers normalize and expose domain data for dashboards, alerts, scenario playback, and analytics.

This repository follows the working conventions defined in `AGENTS.md`, including English-only code and documentation, UTC timestamps, WGS84 geographic storage, and ontology-first domain modeling.

## Architecture

This project is organized as a pnpm workspace monorepo.

### Monorepo Structure

- `apps/frontend` — React + Vite + TypeScript + Tailwind + THREE.js application for the 3D monitoring UI.
- `apps/backend` — FastAPI application exposing operational, graph, document, scenario, alert, and health endpoints.
- `etl/` — Python ETL pipeline for collecting and persisting upstream port, weather, facility, and statistical data.
- `packages/ontology` — shared ontology classes and relationships used across the platform.
- `packages/shared-types` — shared TypeScript types for cross-package contracts.
- `packages/ui` — shared UI package for frontend primitives and future reusable components.

### Runtime Topology

The default local runtime is defined in `docker-compose.yml` and includes:

- PostgreSQL with PostGIS for spatial and operational persistence
- Redis for event distribution and pub/sub
- FastAPI backend on port `8000`
- Frontend application on port `3000`

The architecture is designed to keep static 3D assets separate from dynamic operational overlays such as vessel movement, berth state, weather indicators, and alerts.

## Prerequisites

Install the following tooling before starting local development:

- Node.js `20+`
- Python `3.10+` (repository configs currently target Python 3.11)
- Docker and Docker Compose
- `pnpm`

Recommended:

- `corepack enable`
- PostgreSQL client tools for local troubleshooting
- `virtualenv` or `uv` for Python environment isolation

## Quick Start

The fastest way to start the full local stack is through Docker Compose.

```bash
docker compose up --build
```

Expected local services:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Backend OpenAPI: `http://localhost:8000/docs`
- PostgreSQL/PostGIS: `localhost:5432`
- Redis: `localhost:6379`

The compose configuration in `docker-compose.yml` wires the backend to PostgreSQL and Redis automatically.

## Development

### 1. Install workspace dependencies

```bash
pnpm install
```

### 2. Frontend development

```bash
pnpm --filter frontend dev
```

Useful frontend commands:

```bash
pnpm --filter frontend build
pnpm --filter frontend lint
pnpm --filter frontend type-check
```

### 3. Backend development

Create and activate a Python environment inside `apps/backend`, then install the package with development dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ./apps/backend[dev]
uvicorn app.main:app --reload --app-dir apps/backend
```

Useful backend commands:

```bash
python -m pytest apps/backend/tests/
```

### 4. ETL development

Install the ETL package with development dependencies and run tests as needed.

```bash
pip install -e ./etl[dev]
python -m pytest etl/tests/
```

### 5. Workspace validation

The repository conventions in `AGENTS.md` expect the following validation flow before delivery:

```bash
pnpm build
pnpm lint
pnpm type-check
python -m pytest apps/backend/tests/
python -m pytest etl/tests/
docker compose build
```

## API Documentation

Additional project documentation lives in `docs/`:

- Product requirements: [`docs/prd.md`](docs/prd.md)
- Ontology reference: [`docs/ontology.md`](docs/ontology.md)
- API specification: [`docs/api-spec.md`](docs/api-spec.md)

During local runtime, interactive backend API docs are also available from FastAPI at `/docs`.

## Project Structure

```text
ulsan-port-3d/
├── AGENTS.md
├── docker-compose.yml
├── apps/
│   ├── frontend/
│   │   ├── src/
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   └── tailwind.config.js
│   └── backend/
│       ├── app/
│       │   ├── core/
│       │   ├── models/
│       │   ├── routers/
│       │   ├── schemas/
│       │   └── services/
│       ├── tests/
│       └── pyproject.toml
├── etl/
│   ├── collectors/
│   ├── jobs/
│   ├── normalizers/
│   ├── tests/
│   ├── common.py
│   └── pyproject.toml
├── packages/
│   ├── ontology/
│   │   └── src/
│   ├── shared-types/
│   │   └── src/
│   └── ui/
│       └── src/
└── docs/
    ├── api-spec.md
    ├── ontology.md
    └── prd.md
```

## Data and Domain Notes

- Geographic data is expected to be stored in WGS84 and transformed for 3D rendering in the frontend.
- Timestamps are stored in UTC and rendered in Asia/Seoul for operators.
- Vessel identity follows the repository convention: `call_sign + arrival_year + voyage_no`.
- Berths are identified by `facility_code`.
- New entities and relationships should be defined in `packages/ontology` before downstream modeling changes are introduced.

## Configuration

Repository-level configuration is split by responsibility:

- `package.json` and `pnpm-workspace.yaml` manage the JavaScript workspace.
- `apps/backend/pyproject.toml` manages backend Python dependencies and pytest settings.
- `etl/pyproject.toml` manages ETL Python dependencies.
- `docker-compose.yml` provides the baseline local orchestration topology.

Environment variables are prefixed by component:

- Backend: `ULSAN_*`
- ETL: `ETL_*`

Refer to `.env.example` and component-specific settings modules for defaults.

## Delivery and Operations

- Use issue-based planning and Conventional Commits as documented in `AGENTS.md`.
- Treat `main` as protected and submit changes through pull requests.
- Keep docs synchronized with API, ontology, and frontend/backend behavior.
- Do not mix simulated and real operational data without explicit labeling.

## License

This project is released under the MIT License.
