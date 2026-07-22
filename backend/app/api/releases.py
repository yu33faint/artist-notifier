from fastapi import APIRouter, Depends

from backend.app.auth import verify_api_key
from backend.app.repositories.releases import get_all_releases

router = APIRouter(prefix="/api", tags=["releases"], dependencies=[Depends(verify_api_key)])


@router.get("/releases")
def get_releases():
    return {
        "status": "success",
        "releases": get_all_releases(),
    }
