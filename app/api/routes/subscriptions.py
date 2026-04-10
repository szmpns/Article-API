from fastapi import APIRouter

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/ping")
def subscriptions_ping() -> dict[str, str]:
    return {"message": "subscriptions route ready"}