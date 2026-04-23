from fastapi import APIRouter

router = APIRouter(tags=["graph"])


@router.get("/graph/{entity_type}/{entity_id}")
async def get_entity_graph(entity_type: str, entity_id: str, depth: int = 1) -> dict:
    return {
        "center": {"type": entity_type, "id": entity_id, "label": ""},
        "relations": [],
    }


@router.get("/graph/explore")
async def explore_graph(
    entity_type: str | None = None,
    entity_id: str | None = None,
    depth: int = 1,
    direction: str = "both",
) -> dict:
    return {"nodes": [], "edges": []}
