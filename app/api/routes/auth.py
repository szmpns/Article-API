from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/ping")
def auth_ping() -> dict[str, str]:
    return {"message": "auth route ready"}