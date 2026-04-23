# API Specification

## Overview

This document describes the backend API exposed by `apps/backend/app/main.py` and the router modules under `apps/backend/app/routers/`.

- API title: `Ulsan Port 3D Monitoring API`
- Current version: `0.1.0`
- REST base path: `/api/v1`
- Health path: `/health`
- WebSocket path: `/api/v1/ws/events`

Unless otherwise noted, endpoints return JSON.

## Common Conventions

### Error Model

Several routers explicitly document `ProblemDetail` for error responses.

```json
{
  "type": "about:blank",
  "title": "Error title",
  "status": 500,
  "detail": "Human-readable detail",
  "instance": "/api/v1/example"
}
```

### Validation Behavior

- Missing required path parameters result in framework-level validation failure.
- Query parameter constraints are enforced where declared.
- Endpoints with path or query validation may return `422 Unprocessable Entity`.

### Authentication

No authentication or authorization layer is defined in the current router set.

---

## Port

### `GET /api/v1/port/overview`

Returns top-level port summary metrics.

- Query params: none
- Request body: none

#### Response `200 OK`

```json
{
  "name": "string",
  "zone_count": 0,
  "berth_count": 0,
  "active_vessel_count": 0,
  "alert_count": 0,
  "last_updated": "2026-04-23T00:00:00Z"
}
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` (`ProblemDetail`)

### `GET /api/v1/zones`

Returns the list of port zones.

- Query params: none
- Request body: none

#### Response `200 OK`

Array of zone objects:

```json
[
  {
    "zone_id": "string",
    "name": "string",
    "zone_type": "string",
    "description": "string",
    "berth_count": 0,
    "buoy_count": 0,
    "created_at": "2026-04-23T00:00:00Z"
  }
]
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` (`ProblemDetail`)

---

## Vessels

### `GET /api/v1/vessels`

Returns all known vessels (same schema as `/vessels/live`).

- Query params:
  - `zone: string | null`
  - `ship_type: string | null`
- Request body: none

#### Response `200 OK`

Same response format as `GET /api/v1/vessels/live`.

#### Status Codes

- `200 OK`
- `500 Internal Server Error` (`ProblemDetail`)

### `GET /api/v1/vessels/live`

Returns the latest live vessel positions.

- Query params:
  - `zone: string | null`
  - `ship_type: string | null`
- Request body: none

#### Response `200 OK`

```json
[
  {
    "vessel_id": "string",
    "name": "string",
    "call_sign": "string",
    "imo": "string",
    "ship_type": "string",
    "gross_tonnage": 0,
    "lat": 0,
    "lon": 0,
    "speed": 0,
    "course": 0,
    "heading": 0,
    "draft": 0,
    "observed_at": "2026-04-23T00:00:00Z",
    "updated_at": "2026-04-23T00:00:00Z"
  }
]
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` (`ProblemDetail`)

### `GET /api/v1/vessels/{vessel_id}`

Returns a vessel detail payload with latest position and event history.

- Path params:
  - `vessel_id: string` — canonical vessel identifier
- Query params: none
- Request body: none

#### Response `200 OK`

```json
{
  "vessel_id": "string",
  "latest_position": {
    "vessel_id": "string",
    "name": "string",
    "call_sign": "string",
    "imo": "string",
    "ship_type": "string",
    "gross_tonnage": 0,
    "lat": 0,
    "lon": 0,
    "speed": 0,
    "course": 0,
    "heading": 0,
    "draft": 0,
    "observed_at": "2026-04-23T00:00:00Z",
    "updated_at": "2026-04-23T00:00:00Z"
  },
  "events": [
    {
      "event_id": "string",
      "vessel_id": "string",
      "call_sign": "string",
      "event_type": "string",
      "berth_facility_code": "string",
      "event_time": "2026-04-23T00:00:00Z",
      "detail": "string",
      "raw_data": "string",
      "created_at": "2026-04-23T00:00:00Z"
    }
  ]
}
```

#### Status Codes

- `200 OK`
- `404 Not Found` (`ProblemDetail`)
- `500 Internal Server Error` (`ProblemDetail`)

---

## Berths

### `GET /api/v1/berths`

Returns berth inventory and latest berth state.

- Query params:
  - `zone: string | null`
  - `status: string | null`
  - `operator: string | null`
- Request body: none

#### Response `200 OK`

```json
[
  {
    "berth_id": "string",
    "facility_code": "string",
    "name": "string",
    "zone_id": "string",
    "zone_name": "string",
    "operator_id": "string",
    "operator_name": "string",
    "length": 0,
    "depth": 0,
    "latitude": 0,
    "longitude": 0,
    "latest_status": "string",
    "latest_status_detail": "string",
    "latest_status_updated_at": "2026-04-23T00:00:00Z",
    "created_at": "2026-04-23T00:00:00Z"
  }
]
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` (`ProblemDetail`)

### `GET /api/v1/berths/{berth_id}`

Returns a single berth detail (same schema as items in `GET /api/v1/berths`).

- Path params:
  - `berth_id: string` — UUID or facility code
- Query params: none
- Request body: none

#### Response `200 OK`

Same object shape as a single item in the `GET /api/v1/berths` array response.

#### Status Codes

- `200 OK`
- `404 Not Found` (`ProblemDetail`)
- `500 Internal Server Error` (`ProblemDetail`)

### `GET /api/v1/berth-status/live`

Returns live berth status records.

- Query params: none
- Request body: none

#### Response `200 OK`

```json
[
  {
    "berth_facility_code": "string",
    "berth_name": "string",
    "zone_name": "string",
    "status": "string",
    "status_detail": "string",
    "updated_at": "2026-04-23T00:00:00Z"
  }
]
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` (`ProblemDetail`)

---

## Weather

### `GET /api/v1/weather/current`

Returns the latest weather observation and latest tide observation.

- Query params: none
- Request body: none

#### Response `200 OK`

```json
{
  "observation": {
    "zone_name": "string",
    "wind_speed": 0,
    "wind_dir": 0,
    "temperature": 0,
    "humidity": 0,
    "pressure": 0,
    "precipitation": 0,
    "visibility": 0,
    "wave_height": 0,
    "observed_at": "2026-04-23T00:00:00Z"
  },
  "tide": {
    "station_name": "string",
    "tide_level": 0,
    "observed_at": "2026-04-23T00:00:00Z"
  }
}
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` (`ProblemDetail`)

### `GET /api/v1/weather/forecast`

Returns weather forecast series, optionally scoped to a zone.

- Query params:
  - `zone: string | null`
- Request body: none

#### Response `200 OK`

```json
[
  {
    "zone_name": "string",
    "observations": [
      {
        "zone_name": "string",
        "wind_speed": 0,
        "wind_dir": 0,
        "temperature": 0,
        "humidity": 0,
        "pressure": 0,
        "precipitation": 0,
        "visibility": 0,
        "wave_height": 0,
        "observed_at": "2026-04-23T00:00:00Z"
      }
    ]
  }
]
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` (`ProblemDetail`)

---

## Statistics

### `GET /api/v1/stats/arrivals`

Returns monthly arrival statistics.

- Query params:
  - `from_date: string | null`
  - `to_date: string | null`
  - `zone: string | null`
- Request body: none

#### Response `200 OK`

```json
[
  {
    "year_month": "2026-04",
    "zone_name": "string",
    "berth_name": "string",
    "vessel_count": 0,
    "created_at": "2026-04-23T00:00:00Z"
  }
]
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` (`ProblemDetail`)

### `GET /api/v1/stats/liquid-cargo`

Returns monthly liquid cargo statistics.

- Query params:
  - `from_date: string | null`
  - `to_date: string | null`
  - `zone: string | null`
- Request body: none

#### Response `200 OK`

```json
[
  {
    "year_month": "2026-04",
    "zone_name": "string",
    "berth_name": "string",
    "cargo_type": "string",
    "volume_ton": 0,
    "created_at": "2026-04-23T00:00:00Z"
  }
]
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` (`ProblemDetail`)

### `GET /api/v1/stats/congestion`

Returns congestion statistics.

- Query params:
  - `from_date: string | null`
  - `to_date: string | null`
- Request body: none

#### Response `200 OK`

```json
[
  {
    "stat_date": "2026-04-23",
    "waiting_count": 0,
    "avg_wait_hours": 0,
    "created_at": "2026-04-23T00:00:00Z"
  }
]
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` (`ProblemDetail`)

---

## Documents

### `GET /api/v1/docs/hazard`

Returns hazard document records.

- Query params: none
- Request body: none

#### Response `200 OK`

```json
[
  {
    "doc_id": "string",
    "title": "string",
    "source_page": "string",
    "published_date": "2026-04-23",
    "file_url": "string",
    "related_cargo_type": "string",
    "created_at": "2026-04-23T00:00:00Z"
  }
]
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` (`ProblemDetail`)

### `GET /api/v1/docs/msds`

Returns MSDS document records.

- Query params: none
- Request body: none

#### Response `200 OK`

```json
[
  {
    "doc_id": "string",
    "title": "string",
    "cargo_type": "string",
    "source_page": "string",
    "file_url": "string",
    "created_at": "2026-04-23T00:00:00Z"
  }
]
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` (`ProblemDetail`)

---

## Scenarios

### `GET /api/v1/scenarios`

Returns available scenario summaries.

- Query params: none
- Request body: none

#### Response `200 OK`

```json
[
  {
    "scenario_id": "string",
    "frame_count": 0,
    "first_frame_index": 0,
    "last_frame_index": 0,
    "first_timestamp": "2026-04-23T00:00:00Z",
    "last_timestamp": "2026-04-23T00:00:00Z",
    "is_simulated": false
  }
]
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` (`ProblemDetail`)

### `GET /api/v1/scenarios/{scenario_id}/frames`

Returns the ordered frames for a scenario.

- Path params:
  - `scenario_id: string`
- Query params: none
- Request body: none

#### Response `200 OK`

```json
[
  {
    "frame_id": "string",
    "scenario_id": "string",
    "frame_index": 0,
    "timestamp": "2026-04-23T00:00:00Z",
    "vessel_positions": {},
    "berth_statuses": {},
    "weather": {},
    "alerts": {},
    "ai_summary": "string",
    "is_simulated": false,
    "created_at": "2026-04-23T00:00:00Z"
  }
]
```

#### Status Codes

- `200 OK`
- `404 Not Found` (`ProblemDetail`)
- `500 Internal Server Error` (`ProblemDetail`)

---

## Graph

### `GET /api/v1/graph/{entity_type}/{entity_id}`

Returns graph context centered on one entity.

- Path params:
  - `entity_type: string`
  - `entity_id: string`
- Query params:
  - `depth: integer` — allowed range `1..3`, default `1`
- Request body: none

#### Response `200 OK`

```json
{
  "center": {
    "type": "string",
    "id": "string",
    "label": "string",
    "data": {}
  },
  "relations": [
    {
      "predicate": "string",
      "direction": "incoming",
      "node": {
        "type": "string",
        "id": "string",
        "label": "string",
        "data": {}
      }
    }
  ]
}
```

#### Status Codes

- `200 OK`
- `404 Not Found` (`ProblemDetail`)
- `422 Unprocessable Entity` for invalid `depth`
- `500 Internal Server Error` (`ProblemDetail`)

### `GET /api/v1/graph/explore`

Explores graph neighborhoods around an optional entity anchor.

- Query params:
  - `entity_type: string | null`
  - `entity_id: string | null`
  - `depth: integer` — allowed range `1..3`, default `1`
  - `direction: string` — allowed values `incoming`, `outgoing`, `both`; default `both`
- Request body: none

#### Response `200 OK`

```json
{
  "nodes": [
    {
      "type": "string",
      "id": "string",
      "label": "string",
      "data": {}
    }
  ],
  "edges": [
    {
      "source_type": "string",
      "source_id": "string",
      "target_type": "string",
      "target_id": "string",
      "predicate": "string"
    }
  ]
}
```

#### Status Codes

- `200 OK`
- `404 Not Found` (`ProblemDetail`)
- `422 Unprocessable Entity` for invalid `depth` or `direction`
- `500 Internal Server Error` (`ProblemDetail`)

---

## WebSocket

### `WS /api/v1/ws/events`

Streams pub/sub event messages to connected clients.

- Handshake: WebSocket upgrade request
- Request body: not applicable
- Query params: none

#### Message Format

Server sends JSON messages forwarded from the Redis pub/sub channel:

```json
{
  "event": "string",
  "payload": {}
}
```

#### Behavior

- Connection is accepted immediately.
- Server subscribes to the configured Redis channel.
- Incoming pub/sub messages are forwarded as JSON.
- Client messages are read and discarded to keep the socket open.

#### Status / Close Codes

- `101 Switching Protocols` on successful handshake
- `1011 Internal Error` when pub/sub subscription fails during setup

---

## Insights

### `GET /api/v1/insights/current`

Returns current rule-based insights with optional LLM summary.

- Query params: none
- Request body: none

#### Response `200 OK`

```json
{
  "rule_based_insights": [
    {
      "insight_id": "string",
      "type": "string",
      "severity": "string",
      "message": "string",
      "related_entity_type": "string",
      "source_data": {}
    }
  ],
  "llm_summary": "string",
  "insight_count": 0
}
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` if insight generation fails

### `GET /api/v1/alerts`

Returns the latest active alerts.

- Query params: none
- Request body: none

#### Response `200 OK`

```json
{
  "alerts": [
    {
      "alert_id": "string",
      "type": "string",
      "severity": "string",
      "message": "string",
      "related_entity_type": "string",
      "related_entity_id": "string",
      "created_at": "2026-04-23T00:00:00Z"
    }
  ],
  "total": 0
}
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` if alert query fails

### `POST /api/v1/alerts/evaluate`

Triggers alert evaluation and persists any newly generated alerts.

- Query params: none
- Request body: none

#### Response `200 OK`

```json
{
  "new_alerts": [
    {
      "alert_type": "string",
      "severity": "string",
      "message": "string",
      "related_entity_type": "string",
      "related_entity_id": "string"
    }
  ],
  "count": 0
}
```

#### Status Codes

- `200 OK`
- `500 Internal Server Error` if evaluation fails

---

## Health

### `GET /health`

Simple service health probe.

- Query params: none
- Request body: none

#### Response `200 OK`

```json
{
  "status": "ok"
}
```

#### Status Codes

- `200 OK`

## Router Inventory Summary

The current router set defines the following backend entry points:

1. `GET /health`
2. `GET /api/v1/port/overview`
3. `GET /api/v1/zones`
4. `GET /api/v1/vessels`
5. `GET /api/v1/vessels/live`
6. `GET /api/v1/vessels/{vessel_id}`
7. `GET /api/v1/berths`
8. `GET /api/v1/berths/{berth_id}`
9. `GET /api/v1/berth-status/live`
10. `GET /api/v1/weather/current`
11. `GET /api/v1/weather/forecast`
12. `GET /api/v1/stats/arrivals`
13. `GET /api/v1/stats/liquid-cargo`
14. `GET /api/v1/stats/congestion`
15. `GET /api/v1/docs/hazard`
16. `GET /api/v1/docs/msds`
17. `GET /api/v1/scenarios`
18. `GET /api/v1/scenarios/{scenario_id}/frames`
19. `GET /api/v1/graph/{entity_type}/{entity_id}`
20. `GET /api/v1/graph/explore`
21. `WS /api/v1/ws/events`
22. `GET /api/v1/insights/current`
23. `GET /api/v1/alerts`
24. `POST /api/v1/alerts/evaluate`

This specification should be updated whenever router signatures, schema models, or version prefixes change.
