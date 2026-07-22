from fastapi import APIRouter, Depends

from backend.app.auth import verify_api_key
from backend.app.services.release_checker import execute_spotify_check

router = APIRouter(prefix="/api", tags=["checks"], dependencies=[Depends(verify_api_key)])

@router.post("/check")
def run_check():
    result_message = execute_spotify_check()
    return {"status": "success",
            "message": result_message}