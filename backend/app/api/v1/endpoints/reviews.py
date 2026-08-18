"""Review endpoints: submit a review for a completed order."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.enums import OfferStatus, OrderStatus, UserRole
from app.models.master import MasterProfile
from app.models.order import Order, OrderOffer
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewOut

router = APIRouter()


@router.post("/", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Review:
    """Submit a review for a completed order (order customer or admin)."""
    order = db.get(Order, payload.order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    if order.customer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the customer who placed the order can review it",
        )
    if order.status != OrderStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only completed orders can be reviewed",
        )
    already_reviewed = (
        db.query(Review).filter(Review.order_id == order.id).first()
    )
    if already_reviewed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This order has already been reviewed",
        )

    accepted_offer = (
        db.query(OrderOffer)
        .filter(
            OrderOffer.order_id == order.id,
            OrderOffer.status == OfferStatus.ACCEPTED,
        )
        .first()
    )
    if accepted_offer is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order has no accepted master offer",
        )

    review = Review(
        order_id=order.id,
        customer_id=current_user.id,
        master_id=accepted_offer.master_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    master = db.get(MasterProfile, accepted_offer.master_id)
    total_score = master.rating * master.reviews_count + payload.rating
    master.reviews_count += 1
    master.rating = round(total_score / master.reviews_count, 2)

    db.add(review)
    db.commit()
    db.refresh(review)
    return review
