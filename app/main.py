from fastapi import FastAPI

from app.api.routes import articles, auth, imports, notifications, subscriptions
from app.core.config import settings
from app.core.database import Base, engine
from app.models import article, notification, subscription, users

app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(subscriptions.router)
app.include_router(notifications.router)
app.include_router(imports.router)