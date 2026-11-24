import llm_gateway
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "llm_gateway": "loaded" if llm_gateway else "missing"}
