from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.article import Article
from app.models.users import User
from app.schemas.article import ArticleCreate, ArticleResponse

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(
    article_data: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Article:
    article = Article(
        title=article_data.title,
        content=article_data.content,
        author_id=current_user.id,
    )

    db.add(article)
    db.commit()
    db.refresh(article)

    return article


@router.get("", response_model=list[ArticleResponse])
def list_articles(db: Session = Depends(get_db)) -> list[Article]:
    articles = db.query(Article).order_by(Article.created_at.desc()).all()
    return articles


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)) -> Article:
    article = db.query(Article).filter(Article.id == article_id).first()

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return article


@router.get("/ping")
def articles_ping() -> dict[str, str]:
    return {"message": "articles route ready"}