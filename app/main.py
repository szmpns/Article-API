from fastapi import FastAPI

from app.api.routes import articles, auth, imports, notifications, subscriptions
from app.core.config import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(subscriptions.router)
app.include_router(notifications.router)
app.include_router(imports.router)