from fastapi import APIRouter
from app.core.cache import get_cache_stats, clear_threats_cache

router = APIRouter(prefix="/api/cache", tags=["Cache"])


@router.get("/stats")
def cache_stats():
    return get_cache_stats()


@router.delete("/clear")
def clear_cache():
    clear_threats_cache()
    return {"message": "Threat cache cleared successfully"}