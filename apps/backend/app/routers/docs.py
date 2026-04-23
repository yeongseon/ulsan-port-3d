from fastapi import APIRouter

router = APIRouter(tags=["docs"])


@router.get("/docs/hazard")
async def get_hazard_docs() -> list:
    return []


@router.get("/docs/msds")
async def get_msds_docs() -> list:
    return []
