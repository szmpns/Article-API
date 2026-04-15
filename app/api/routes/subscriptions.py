from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.subscription import Subscription
from app.models.users import User
from app.schemas.subscription import SubscriptionResponse

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("/me", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def subscribe_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Subscription:
    existing_subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == current_user.id)
        .first()
    )

    if existing_subscription is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already subscribed",
        )

    subscription = Subscription(user_id=current_user.id)

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def unsubscribe_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == current_user.id)
        .first()
    )

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )

    db.delete(subscription)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)