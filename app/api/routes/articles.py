from fastapi import APIRouter

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/ping")
def articles_ping() -> dict[str, str]:
    return {"message": "articles route ready"}