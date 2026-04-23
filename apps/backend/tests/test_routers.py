from fastapi.routing import APIRoute
from starlette.routing import WebSocketRoute

from app.main import app


EXPECTED_HTTP_ROUTES = {
    ("GET", "/health"),
    ("GET", "/api/v1/port/overview"),
    ("GET", "/api/v1/zones"),
    ("GET", "/api/v1/vessels"),
    ("GET", "/api/v1/vessels/live"),
    ("GET", "/api/v1/vessels/{vessel_id}"),
    ("GET", "/api/v1/berths"),
    ("GET", "/api/v1/berths/{berth_id}"),
    ("GET", "/api/v1/berth-status/live"),
    ("GET", "/api/v1/weather/current"),
    ("GET", "/api/v1/weather/forecast"),
    ("GET", "/api/v1/stats/arrivals"),
    ("GET", "/api/v1/stats/liquid-cargo"),
    ("GET", "/api/v1/stats/congestion"),
    ("GET", "/api/v1/docs/hazard"),
    ("GET", "/api/v1/docs/msds"),
    ("GET", "/api/v1/scenarios"),
    ("GET", "/api/v1/scenarios/{scenario_id}/frames"),
    ("GET", "/api/v1/graph/{entity_type}/{entity_id}"),
    ("GET", "/api/v1/graph/explore"),
    ("GET", "/api/v1/insights/current"),
    ("GET", "/api/v1/alerts"),
    ("POST", "/api/v1/alerts/evaluate"),
}

EXPECTED_WEBSOCKET_ROUTES = {"/api/v1/ws/events"}


def test_expected_http_routes_are_registered() -> None:
    registered = {
        (method, route.path)
        for route in app.routes
        if isinstance(route, APIRoute)
        for method in route.methods
        if method not in {"HEAD", "OPTIONS"}
    }

    assert EXPECTED_HTTP_ROUTES.issubset(registered)


def test_expected_websocket_routes_are_registered() -> None:
    registered = {route.path for route in app.routes if isinstance(route, WebSocketRoute)}

    assert EXPECTED_WEBSOCKET_ROUTES.issubset(registered)
