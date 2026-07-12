from fastapi import APIRouter

from backend.app.repositories.releases import get_all_releases

router = APIRouter(prefix="/api", tags=["releases"])


@router.get("/releases")
def get_releases():
    return {
        "status": "success",
        "releases": get_all_releases(),
    }
