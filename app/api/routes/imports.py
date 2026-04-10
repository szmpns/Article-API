from fastapi import APIRouter

router = APIRouter(prefix="/imports", tags=["imports"])


@router.get("/ping")
def imports_ping() -> dict[str, str]:
    return {"message": "imports route ready"}