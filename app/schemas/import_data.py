from pydantic import BaseModel, Field, HttpUrl


class ImportArticlesRequest(BaseModel):
    source_url: HttpUrl


class ImportedArticleItem(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    content: str = Field(..., min_length=1)


class ImportArticlesResponse(BaseModel):
    imported_count: int
    skipped_count: int
    total_received: int