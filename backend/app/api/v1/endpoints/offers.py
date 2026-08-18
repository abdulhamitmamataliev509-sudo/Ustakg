"""Order-offer endpoints: create offers, list order offers, accept offers."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_master, get_current_user
from app.core.database import get_db
from app.models.enums import OfferStatus, OrderStatus, UserRole
from app.models.master import MasterProfile
from app.models.order import Order, OrderOffer
from app.models.user import User
from app.models.chat import Chat
from app.schemas.offer import OfferCreate, OfferOut

router = APIRouter()


@router.post("/", response_model=OfferOut, status_code=status.HTTP_201_CREATED)
def create_offer(
    payload: OfferCreate,
    profile: MasterProfile = Depends(get_current_active_master),
    db: Session = Depends(get_db),
) -> OrderOffer:
    """Submit an offer for an open order (masters only)."""
    order = db.get(Order, payload.order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    if order.status != OrderStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Order is not open for offers"
        )
    existing = (
        db.query(OrderOffer)
        .filter(
            OrderOffer.order_id == order.id,
            OrderOffer.master_id == profile.id,
            OrderOffer.status == OfferStatus.PENDING,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a pending offer for this order",
        )
    offer = OrderOffer(
        order_id=order.id,
        master_id=profile.id,
        proposed_price=payload.proposed_price,
        comment=payload.comment,
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer


@router.get("/order/{order_id}", response_model=list[OfferOut])
def list_order_offers(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[OrderOffer]:
    """List all offers for a customer's order (customer or admin only)."""
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    if order.customer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the order owner can view its offers",
        )
    return (
        db.query(OrderOffer)
        .filter(OrderOffer.order_id == order_id)
        .order_by(OrderOffer.created_at.asc())
        .all()
    )


@router.post("/{offer_id}/accept", response_model=OfferOut)
def accept_offer(
    offer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderOffer:
    """Accept an offer (order customer or admin). Moves order to IN_PROGRESS."""
    offer = db.get(OrderOffer, offer_id)
    if offer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found"
        )
    order = db.get(Order, offer.order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    if order.customer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the order owner can accept an offer",
        )
    if offer.status != OfferStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending offers can be accepted",
        )
    offer.status = OfferStatus.ACCEPTED
    order.status = OrderStatus.IN_PROGRESS
    db.query(OrderOffer).filter(
        OrderOffer.order_id == order.id,
        OrderOffer.id != offer.id,
        OrderOffer.status == OfferStatus.PENDING,
    ).update({OrderOffer.status: OfferStatus.REJECTED}, synchronize_session=False)
    db.commit()
    db.refresh(offer)
    # ensure a Chat exists for this order between customer and master
    existing_chat = (
        db.query(Chat)
        .filter(Chat.order_id == order.id, Chat.customer_id == order.customer_id, Chat.master_id == offer.master_id)
        .first()
    )
    if existing_chat is None:
        chat = Chat(order_id=order.id, customer_id=order.customer_id, master_id=offer.master_id)
        db.add(chat)
        db.commit()
    return offer
