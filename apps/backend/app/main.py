from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import async_session
from app.core.errors import (
    ProblemHTTPException,
    http_exception_handler,
    problem_exception_handler,
    validation_exception_handler,
)
from app.routers import (
    berths,
    docs,
    graph,
    health,
    insights,
    port,
    scenarios,
    stats,
    vessels,
    weather,
    websocket,
)
from app.services.seed import seed_reference_data


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with async_session() as session:
        await seed_reference_data(session)
    yield


app = FastAPI(
    title="Ulsan Port 3D Monitoring API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(ProblemHTTPException, cast(Any, problem_exception_handler))
app.add_exception_handler(StarletteHTTPException, cast(Any, http_exception_handler))
app.add_exception_handler(RequestValidationError, cast(Any, validation_exception_handler))

app.include_router(health.router)
app.include_router(port.router, prefix="/api/v1")
app.include_router(vessels.router, prefix="/api/v1")
app.include_router(berths.router, prefix="/api/v1")
app.include_router(weather.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
app.include_router(docs.router, prefix="/api/v1")
app.include_router(scenarios.router, prefix="/api/v1")
app.include_router(graph.router, prefix="/api/v1")
app.include_router(websocket.router, prefix="/api/v1")
app.include_router(insights.router, prefix="/api/v1")
