from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
import httpx

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.article import Article
from app.models.notification import Notification
from app.models.subscription import Subscription
from app.models.users import User
from app.schemas.article import ArticleCreate, ArticleResponse, ArticleUpdate
from app.schemas.import_data import (
    ImportArticlesRequest,
    ImportArticlesResponse,
    ImportedArticleItem,
)

router = APIRouter(prefix="/articles", tags=["articles"])


def create_notifications_for_new_article(
    db: Session,
    article: Article,
    author_id: int,
) -> None:
    subscriptions = db.query(Subscription).all()

    notifications = []
    for subscription in subscriptions:
        if subscription.user_id == author_id:
            continue

        notifications.append(
            Notification(
                user_id=subscription.user_id,
                article_id=article.id,
                message=f"New article published: {article.title}",
            )
        )

    if notifications:
        db.add_all(notifications)
        db.commit()


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

    create_notifications_for_new_article(
        db=db,
        article=article,
        author_id=current_user.id,
    )

    return article


@router.post("/import", response_model=ImportArticlesResponse)
def import_articles(
    import_request: ImportArticlesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ImportArticlesResponse:
    try:
        response = httpx.get(str(import_request.source_url), timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not fetch external data: {exc}",
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="External source did not return valid JSON",
        ) from exc

    if not isinstance(payload, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="External source must return a JSON array of articles",
        )

    imported_count = 0
    skipped_count = 0

    for raw_item in payload:
        try:
            item = ImportedArticleItem.model_validate(raw_item)
        except Exception:
            skipped_count += 1
            continue

        existing_article = (
            db.query(Article)
            .filter(
                Article.author_id == current_user.id,
                Article.title == item.title,
                Article.content == item.content,
            )
            .first()
        )

        if existing_article is not None:
            skipped_count += 1
            continue

        article = Article(
            title=item.title,
            content=item.content,
            author_id=current_user.id,
        )

        db.add(article)
        db.commit()
        db.refresh(article)

        create_notifications_for_new_article(
            db=db,
            article=article,
            author_id=current_user.id,
        )

        imported_count += 1

    return ImportArticlesResponse(
        imported_count=imported_count,
        skipped_count=skipped_count,
        total_received=len(payload),
    )


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


@router.patch("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Article:
    article = db.query(Article).filter(Article.id == article_id).first()

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    if article.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to modify this article",
        )

    update_data = article_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(article, field, value)

    db.commit()
    db.refresh(article)

    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    article = db.query(Article).filter(Article.id == article_id).first()

    if article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    if article.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this article",
        )

    db.delete(article)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)