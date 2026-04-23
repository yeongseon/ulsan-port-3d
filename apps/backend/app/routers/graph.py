from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import ProblemDetail
from app.schemas.graph import EntityGraphResponse, GraphExploreResponse
from app.services import graph as graph_service

router = APIRouter(tags=["graph"])


@router.get(
    "/graph/{entity_type}/{entity_id}",
    response_model=EntityGraphResponse,
    responses={404: {"model": ProblemDetail}, 500: {"model": ProblemDetail}},
)
async def get_entity_graph(
    entity_type: str,
    entity_id: str,
    depth: Annotated[int, Query(ge=1, le=3)] = 1,
    *,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EntityGraphResponse:
    _ = depth
    return await graph_service.get_entity_graph(db, entity_type=entity_type, entity_id=entity_id)


@router.get(
    "/graph/explore",
    response_model=GraphExploreResponse,
    responses={404: {"model": ProblemDetail}, 500: {"model": ProblemDetail}},
)
async def explore_graph(
    entity_type: str | None = None,
    entity_id: str | None = None,
    depth: Annotated[int, Query(ge=1, le=3)] = 1,
    direction: Annotated[str, Query(pattern="^(incoming|outgoing|both)$")] = "both",
    *,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GraphExploreResponse:
    return await graph_service.explore_graph(
        db,
        entity_type=entity_type,
        entity_id=entity_id,
        depth=depth,
        direction=direction,
    )
