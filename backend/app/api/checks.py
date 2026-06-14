from fastapi import APIRouter
from backend.app.services.release_checker import execute_spotify_check

router = APIRouter(prefix="/api", tags=["checks"])

@router.post("/check")
def run_check():
    result_message = execute_spotify_check()
    return {"status": "success",
            "message": result_message}