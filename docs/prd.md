# Product Requirements Document

## Product

Ulsan Port 3D Monitoring System

## Document Status

- Owner: Product / Platform Engineering
- Scope: Operator-facing monitoring platform for Ulsan Port
- Repository: `ulsan-port-3d`
- Tracking model: Issue-based delivery tracking in place of milestone tables

## §1 Background

Ulsan Port is a large industrial and logistics hub with operational complexity spanning vessel movements, berth usage, hazardous cargo handling, weather conditions, and port congestion.

Public data from the Ulsan Port Authority and adjacent maritime/weather sources provides valuable operational signals, but that information is typically fragmented across raw feeds, tabular data, and static websites. Operators and downstream logistics stakeholders need a unified way to understand what is happening across the port in near real time.

The Ulsan Port 3D Monitoring System addresses this need by combining:

- Ulsan Port public operational data
- facility and berth information
- vessel movement and event streams
- weather and tide conditions
- cargo and congestion statistics
- ontology-based relationship exploration
- scenario playback for review and communication

The product visualizes this information in a 3D web interface so users can move from static monitoring to spatially aware, context-rich decision support.

The solution is intended to support both day-to-day monitoring and operational analysis, while preserving clear domain vocabulary and a strict ontology-first architecture across the monorepo.

## §2 Goals

### Primary Goals

1. Provide near-real-time vessel and berth monitoring for Ulsan Port.
2. Integrate weather and tide context directly into operational views.
3. Enable ontology exploration across port entities and relationships.
4. Surface statistics, alerts, and scenario history in a single operator workflow.
5. Support a scalable data pipeline that can absorb public data updates continuously.

### Secondary Goals

1. Improve situational awareness for berth allocation and congestion handling.
2. Reduce operational friction caused by fragmented data sources.
3. Create a foundation for future analytics, automation, and AI-assisted summarization.
4. Provide a repository structure that supports shared packages and disciplined domain modeling.

### Out of Scope

- Direct vessel control or dispatch automation
- Billing, invoicing, or customs workflows
- Public consumer-facing tourism or marketing experiences
- Manual editing of historical records that should remain immutable

## §3 User Stories

### Port Operator

- As a port operator, I want to see the current location of active vessels in a 3D scene so that I can quickly assess traffic around key zones and berths.
- As a port operator, I want to inspect berth status and weather conditions together so that I can understand whether an issue is caused by facility availability or environmental conditions.
- As a port operator, I want to receive alerts when wind, wave height, visibility, or berth availability cross risk thresholds so that I can act before conditions worsen.
- As a port operator, I want to replay scenario frames so that I can review incidents and explain operational changes to other teams.
- As a port operator, I want to open ontology graph views from an entity so that I can trace relationships among vessels, berths, operators, cargo types, and documents.

### Logistics Manager

- As a logistics manager, I want to review vessel arrivals, congestion statistics, and berth occupancy trends so that I can anticipate delays.
- As a logistics manager, I want to understand which terminal or berth is associated with a vessel call so that I can coordinate downstream operations.
- As a logistics manager, I want access to hazard and MSDS documents connected to cargo context so that compliance and safety information is easy to locate.
- As a logistics manager, I want a summarized current-state view so that I can brief stakeholders without manually reading multiple systems.

## §4 Functional Requirements

### FR-1 Vessel Tracking

The system shall ingest and display live vessel positions.

- Show current vessel markers with vessel metadata.
- Support filtering by zone and ship type.
- Provide detail views for an individual vessel.
- Expose vessel events and voyage context where available.
- Maintain a current snapshot and historical observations.

### FR-2 Berth Status Monitoring

The system shall display berth inventory and current berth status.

- Show berth list by zone, operator, and status.
- Surface the latest berth operational state.
- Display berth detail fields relevant to planning and monitoring.
- Support operational grouping by zone.

### FR-3 Weather and Tide Display

The system shall display current weather and forecast context.

- Show latest weather observation data.
- Show forecast data scoped to a zone where applicable.
- Show tide observation data alongside weather.
- Make weather context available to alerts and summaries.

### FR-4 Statistics Dashboard

The system shall expose port statistics for trend analysis.

- Monthly vessel arrival statistics
- Monthly liquid cargo statistics
- Congestion statistics such as waiting vessel count and average wait time
- Date range filtering where supported by APIs

### FR-5 Alerts and Insights

The system shall provide operational alerts and current insights.

- Evaluate threshold-based weather alerts.
- Evaluate berth unavailability alerts.
- Evaluate congestion alerts.
- Support compound alerting where multiple risk types occur together.
- Return rule-based insights and optional AI-generated summaries.

### FR-6 Document Access

The system shall provide access to operational safety documents.

- Hazard documents by operator or source
- MSDS documents linked to cargo context
- Future support for safety manuals where modeled

### FR-7 Ontology Exploration

The system shall expose graph traversal and entity graph APIs.

- Retrieve graph context centered on a selected entity.
- Explore graph neighborhoods by direction and depth.
- Preserve ontology predicates from the shared package.

### FR-8 Scenario Playback

The system shall support scenario history and playback.

- List available scenarios
- Retrieve ordered frames for a scenario
- Present vessel positions, berth statuses, weather, and alert context by frame

### FR-9 Documentation and Discoverability

The system shall maintain current operator-facing documentation.

- README for setup and architecture
- PRD for product scope and expectations
- Ontology reference for entity and relationship semantics
- API specification for backend consumers

## §5 Non-Functional Requirements

### Performance

- Real-time operational data should be available with target end-to-end latency below 5 seconds for active monitoring views.
- The frontend should remain responsive during common interactions such as camera movement, filtering, and panel switching.
- API responses for standard list and summary endpoints should be sized for practical dashboard use.

### Scalability

- The system should support monitoring capacity for `1000+` vessels without degrading the basic interaction model.
- ETL collection should handle periodic updates and upstream retry behavior without manual intervention.
- The ontology and API design should support future class and relationship expansion.

### Reliability

- Collector failures should be logged and retried using exponential backoff.
- The backend should degrade gracefully when non-critical services are unavailable.
- Raw upstream snapshots should be persisted before transformation.

### Maintainability

- The repository must preserve monorepo boundaries and shared package contracts.
- Domain additions must be reflected in `packages/ontology` first.
- Tests must cover added operational behavior and basic import health.

### Security and Compliance

- Hazard and safety documents must be traceable to source metadata.
- Credentials must remain externalized through environment variables.
- Historical documents and records marked immutable must remain unedited.

### Data Standards

- Geographic data is stored in WGS84.
- Timestamps are stored in UTC and emitted as ISO-8601.
- Domain identifiers follow repository conventions for vessels, berths, operators, and documents.

## §6 Data Sources

Primary external data sources include Ulsan Port public data and related maritime/weather sources.

### Primary Source

- 울산항만공사 API / Ulsan Port Authority public APIs for vessel, facility, berth status, route, terminal, and port statistics data

### Supporting Sources

- Port weather observations and forecasts exposed through configured API sources
- Tide observations for operational context
- Port safety and hazard document pages

### Data Handling Requirements

- Raw snapshots must be stored before normalization.
- Simulated data must be labeled explicitly.
- Real and simulated datasets must not be mixed silently.

## §7 Architecture

The product is implemented as a monorepo with shared packages and clear runtime boundaries.

### Application Components

- **Frontend**: React + TypeScript + Vite + Tailwind + THREE.js
- **Backend API**: FastAPI
- **Database**: PostgreSQL + PostGIS
- **Realtime/Eventing**: Redis pub/sub
- **Data Pipeline**: Python ETL collectors and schedulers
- **Shared Domain**: TypeScript ontology and shared package modules

### Architectural Principles

- Ontology-first domain modeling
- Separation of static 3D environment and dynamic overlays
- UTC timestamps across persistence and API layers
- WGS84 storage for spatial data
- Issue-based planning and delivery workflow

### Core Repositories and Paths

- `apps/frontend`
- `apps/backend`
- `etl/`
- `packages/ontology`
- `packages/shared-types`
- `packages/ui`

### Data Flow Summary

1. Public APIs and source pages are collected by ETL jobs.
2. Raw snapshots are persisted under `data/raw/...`.
3. Normalized data is inserted into relational/spatial storage.
4. Backend services expose the latest domain views through FastAPI.
5. Frontend stores combine API and WebSocket data into the monitoring UI.
6. Ontology graph services expose relationship exploration based on shared predicates.

## §8 Ontology

The ontology expresses the operational model of the port as a set of classes and directional relationships.

### Primary Business Entity Types

1. Port
2. PortZone
3. Berth
4. Vessel
5. VoyageCall
6. Operator
7. Terminal
8. TankTerminal
9. Buoy
10. RouteSegment
11. CargoType
12. WeatherStation
13. TideStation
14. Document
15. Alert

### Implementation Classes Used in the Shared Ontology Package

The current shared package expands the business model into concrete classes used by services and graph APIs:

- Spatial: `Port`, `Zone`, `Berth`, `Buoy`, `RouteSegment`, `Terminal`, `TankTerminal`, `Operator`
- Operational: `Vessel`, `VoyageCall`, `VesselPosition`, `VesselEvent`, `BerthStatus`, `CongestionStat`
- Cargo: `CargoType`, `LiquidCargoStat`, `ArrivalStat`
- Environmental: `WeatherObservation`, `WeatherForecast`, `TideObservation`, `HazardDoc`, `MsdsDoc`, `SafetyManual`
- UI/Application: `Alert`, `Insight`, `ScenarioFrame`

### Conceptual Hierarchy

- Port contains PortZones.
- PortZones contain berths, buoys, route segments, and environmental observations.
- Berths support voyage calls and carry operational status.
- Vessels produce positions and events and participate in voyage calls.
- Operators manage physical assets and safety documentation.
- Tank terminals store cargo types and belong to zones.
- Weather and tide observations describe zone-level conditions.
- Documents carry safety and cargo handling context.
- Alerts and insights summarize operational risk at the application layer.

### Relationship Statements

The current implementation supports the following relationship statements aligned with the ontology package:

1. Port `hasZone` Zone
2. Zone `hasBerth` Berth
3. Zone `hasBuoy` Buoy
4. Zone `hasRouteSegment` RouteSegment
5. Operator `operates` Berth
6. Operator `operates` TankTerminal
7. TankTerminal `locatedIn` Zone
8. TankTerminal `stores` CargoType
9. Vessel `hasVoyageCall` VoyageCall
10. VoyageCall `usesFacility` Berth
11. VoyageCall `hasEvent` VesselEvent
12. Vessel `hasPosition` VesselPosition
13. Berth `hasStatus` BerthStatus
14. Berth `handlesCargo` CargoType
15. Zone `hasWeather` WeatherObservation
16. Zone `hasForecast` WeatherForecast
17. Zone `hasTide` TideObservation
18. Operator `hasHazardDoc` HazardDoc
19. CargoType `hasMsds` MsdsDoc
20. ScenarioFrame captures point-in-time snapshots for vessels, berths, weather, and alerts in the application layer

### Ontology Requirements

- Any new domain entity must be introduced in `packages/ontology` first.
- Backend graph responses must preserve predicate semantics exactly.
- Frontend graph and detail panels must use the same entity vocabulary.

## §9 API Overview

The backend exposes a FastAPI application with grouped domains for:

- health
- port and zones
- vessels
- berths
- weather
- statistics
- documents
- scenarios
- graph exploration
- WebSocket events
- insights and alerts

The REST API is primarily versioned under `/api/v1`, while the health endpoint is served at `/health`.

The API should support:

- dashboard summary retrieval
- filtered operational lists
- detail views for selected entities
- scenario playback retrieval
- graph-centric exploration
- machine-readable problem responses for known error cases

## §10 Tracking and Delivery Model

Traditional milestone tables are replaced by issue-based tracking.

### Delivery Rules

- Use issues for small fixes, testing, tooling, and documentation work.
- Use epics and sub-issues for major feature areas.
- Label all issues with type, domain, size, and priority.
- Keep pull requests scoped, reviewable, and linked to issues.

### Initial Delivery Themes

- Core 3D monitoring UI readiness
- Backend API completeness and schema stability
- ETL collector resilience and coverage
- Ontology and graph consistency
- Alerting and operational insight quality
- Documentation and test maturity

### Success Metrics

- Operators can load a unified current-state dashboard without switching systems.
- Vessel, berth, weather, and statistics data remain available through documented APIs.
- Graph exploration is understandable and aligned with shared ontology definitions.
- Tests cover basic service import and route availability.
- Documentation remains current enough for engineering onboarding and operational review.
