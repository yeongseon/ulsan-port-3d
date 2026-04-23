from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import health, port, vessels, berths, weather, stats, docs, scenarios, graph

app = FastAPI(
    title="Ulsan Port 3D Monitoring API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(port.router, prefix="/api/v1")
app.include_router(vessels.router, prefix="/api/v1")
app.include_router(berths.router, prefix="/api/v1")
app.include_router(weather.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
app.include_router(docs.router, prefix="/api/v1")
app.include_router(scenarios.router, prefix="/api/v1")
app.include_router(graph.router, prefix="/api/v1")
