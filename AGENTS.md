# AGENTS.md

## Purpose

`ulsan-port-3d` is a monorepo for a web-based 3D port monitoring system for Ulsan Port. It integrates vessel, berth, weather, cargo statistics, and ontology-based relationship exploration into a unified real-time dashboard. The frontend uses React + TypeScript + THREE.js (with optional Spark 2.0 for photorealistic backgrounds), and the backend uses FastAPI + PostgreSQL/PostGIS.

## Read First

- `README.md`
- `docs/prd.md`
- `docs/ontology.md`
- `docs/api-spec.md`

## Working Rules

- Preserve the existing domain vocabulary: port, zone, berth, buoy, vessel, voyage call, operator, terminal, cargo type.
- Keep frontend behavior, docs, and any domain model changes synchronized.
- Treat `apps/frontend` as the primary production surface unless the task explicitly targets `apps/backend` or `etl/`.
- Avoid incidental refactors in areas that already have unrelated user changes.
- **Korean data, English code**: All code, comments, commit messages, PR titles, and documentation are written in English. Korean text appears only in UI display strings (port names, status labels, user-facing tooltips) and raw data values from Korean public APIs.
- **Coordinate convention (INVIOLABLE)**: All geographic data is stored in WGS84 (EPSG:4326) using PostGIS geometry columns. The frontend converts to a local coordinate system centered on Ulsan Port for 3D rendering. Any change that stores coordinates in a non-WGS84 format without an explicit conversion layer is a blocking defect.
- **Time convention (INVIOLABLE)**: All timestamps are stored in UTC. API responses use ISO-8601 format. The frontend displays in Asia/Seoul timezone. Any code that stores local time in the database is a blocking defect.
- **Identifier convention**: Vessels are identified by `call_sign + arrival_year + voyage_no`. Berths by `facility_code`. Operators by `operator_id`. Documents by `source_page + title + published_date`.
- **3D layer separation (INVIOLABLE)**: Static background scenes (Spark 2.0 or baked THREE.js) and dynamic real-time overlays (vessel markers, berth status colors, weather indicators) are rendered in separate layers. Never embed real-time data into the static scene pipeline. Never embed static background geometry into the dynamic overlay pipeline.
- **Ontology-first data modeling**: Before adding a new entity or relationship to the database, it must be defined in `packages/ontology/`. The DB schema must reflect the ontology class hierarchy and relationships defined in §8 of the PRD.
- **Test expectations**: New features should include tests. Do not delete or skip failing tests to make CI pass — fix the root cause instead.
- **Historical documents are immutable**: Do NOT edit documents marked "Historical" or "Superseded". ADRs (`docs/adr/`) are immutable once merged; create a new ADR to supersede an old one.

## Store Boundaries

Three primary data contexts exist:

| Context | Scope | Examples |
|---------|-------|---------|
| `mapStore` | 3D scene state | Camera position, active layers, selected entity, zoom level |
| `dataStore` | Domain data | Vessels, berths, weather, statistics, ontology graph |
| `uiStore` | UI state | Panel visibility, filter selections, timeline position, theme |

Add new state to the store that owns the domain. Do not create new stores without discussion.

## Git Conventions

### Branch Naming

Use the pattern `{type}/{issue#}-{short-desc}` or `{type}/{short-desc}`:

- `feat/15-rest-api-vessels`
- `fix/22-berth-status-color`
- `data/6-vessel-position-collector`
- `chore/docker-compose-fix`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/). Format: `{type}({scope}): {description}`.

| Prefix     | When to use                             |
|------------|-----------------------------------------|
| `feat`     | New feature or capability               |
| `fix`      | Bug fix                                 |
| `docs`     | Documentation only                      |
| `test`     | Adding or updating tests                |
| `refactor` | Code change that neither fixes nor adds |
| `style`    | Formatting, CSS, whitespace             |
| `chore`    | Build, tooling, release management      |
| `perf`     | Performance improvement                 |
| `ci`       | CI/CD pipeline changes                  |
| `data`     | ETL, data pipeline, schema migration    |

Scope is optional but recommended: `feat(frontend):`, `fix(api):`, `data(etl):`.

### Pull Request Rules

- `main` is a protected branch — all changes go through PR + CI.
- Squash-merge every PR with `--delete-branch`: `gh pr merge <number> --squash --delete-branch`.
- PR title should follow the same Conventional Commits format as commit messages.
- Each PR should reference and close its issue (e.g., `Fixes #123`).
- **Post-PR review gate**: After creating or updating a PR, always check CI results before merging:
  1. Wait for CI checks to complete: `gh pr checks <number> --watch`
  2. Review any automated review comments.
  3. Fix flagged issues before merging.
  4. Only proceed with merge when all checks pass and no unresolved review comments remain.

## Implementation Principles

### Use Proven Libraries First

**Don't reinvent the wheel.** Before implementing any feature from scratch, search for well-maintained libraries.

| Need | Prefer | Avoid |
|------|--------|-------|
| 3D rendering | THREE.js, @react-three/fiber | Custom WebGL from scratch |
| 3D backgrounds | Spark 2.0 (if licensed) | Building photorealistic pipeline |
| Maps/GIS overlay | deck.gl, Mapbox GL | Custom tile rendering |
| Charts | Recharts, Apache ECharts | Custom SVG chart logic |
| State management | Zustand | Redux for new code |
| HTTP client | axios, ky | Raw fetch for complex flows |
| WebSocket | Socket.IO client | Custom WS reconnection logic |
| Date handling | date-fns, dayjs | Raw Date manipulation |
| ORM (Python) | SQLAlchemy 2.0 | Raw SQL for complex queries |
| Migration | Alembic | Manual DDL scripts |
| Scheduling | APScheduler | Custom cron wrappers |
| Validation (Python) | Pydantic v2 | Manual validation |
| Validation (TS) | Zod | Manual validation |

### When to Build Custom

- No library exists for the specific domain need (e.g., Ulsan Port local coordinate transform)
- Existing libraries have critical security issues
- Bundle size impact is unacceptable (>100kb for minor feature)
- Library API conflicts with existing architecture patterns

## Planning Workflow

- Use two planning paths:
  - Feature implementation: `Epic -> Sub-issue -> Branch -> PR`
  - Small fixes, docs, and maintenance: `Issue -> Branch -> PR`
- Before starting work on any issue, always check the assignee first. If already assigned, do not pick it up.
- Before starting work on any issue, always sync local `main` first:
  ```bash
  git checkout main
  git pull --ff-only origin main
  ```
- Create one Epic issue per major feature area. Epic titles use the format `[Epic] <feature area>`.
- Epic issues must include: `## Overview`, `## Sub-Issues`, `## Dependencies`, `## Constraints`.
- Decompose each Epic into focused sub-issues. Each sub-issue must include `Part of #<epic-number>` at the top.
- Labeling rules:
  - Epic issues use `epic` plus domain labels.
  - Implementation issues use one type label: `enhancement`, `bug`, or `testing`.
  - Domain labels: `frontend`, `backend`, `data`, `ontology`, `infra`, `ai`, `design`.
  - Size labels: `size/S`, `size/M`, `size/L`, `size/XL` — assigned at creation time.
  - Priority labels: `priority:high`, `priority:medium`, `priority:low`.
  - **Mandatory labels on creation**: Every issue must have all applicable labels in `gh issue create --label`.

## Data Pipeline Rules

- Every ETL collector must save raw API responses to `data/raw/{source}/{date}/` before any transformation.
- Normalized data goes through `etl/normalizers/` before database insertion.
- All collectors must handle: rate limiting, retries (3x with exponential backoff), timeout (30s default), and error logging.
- Simulated/demo data must be clearly marked with `is_simulated: true` flag in the database.
- Never mix real and simulated data in the same query result without explicit filtering.

## Validation

- Frontend: `pnpm build && pnpm lint && pnpm type-check`
- Backend: `python -m pytest apps/backend/tests/`
- ETL: `python -m pytest etl/tests/`
- Docker: `docker compose build`
