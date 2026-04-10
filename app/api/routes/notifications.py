from fastapi import APIRouter

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/ping")
def notifications_ping() -> dict[str, str]:
    return {"message": "notifications route ready"}