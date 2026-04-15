from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import articles, auth, notifications, subscriptions
from app.core.config import settings
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.testing:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(subscriptions.router)
app.include_router(notifications.router)