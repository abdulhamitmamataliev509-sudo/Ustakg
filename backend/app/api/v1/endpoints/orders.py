"""Order endpoints: creation, listing, details, and status changes."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.analytics import track_event
from app.core.database import get_db
from app.models.category import Category
from app.models.enums import OrderStatus, UserRole
from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderCreate, OrderDetail, OrderOut, OrderStatusUpdate

router = APIRouter()


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Order:
    """Create a new order (any authenticated user)."""
    if db.get(Category, payload.category_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    order = Order(customer_id=current_user.id, **payload.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)

    track_event(
        "order.created",
        {
            "order_id": str(order.id),
            "customer_id": str(order.customer_id),
            "category_id": str(order.category_id),
            "status": order.status.value,
        },
    )
    return order


@router.get("/", response_model=list[OrderOut])
def list_orders(
    status_filter: OrderStatus | None = None,
    category_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
) -> list[Order]:
    """List orders. Defaults to open orders; filterable by status/category."""
    query = db.query(Order)
    target_status = status_filter if status_filter is not None else OrderStatus.OPEN
    query = query.filter(Order.status == target_status)
    if category_id is not None:
        query = query.filter(Order.category_id == category_id)
    return query.order_by(Order.created_at.desc()).all()


@router.get("/{order_id}", response_model=OrderDetail)
def get_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Order:
    """Fetch order details including offers (owner/admin for non-open orders)."""
    order = (
        db.query(Order)
        .options(selectinload(Order.offers))
        .filter(Order.id == order_id)
        .first()
    )
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    if (
        order.status != OrderStatus.OPEN
        and order.customer_id != current_user.id
        and current_user.role != UserRole.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Order details are visible only to its customer or an admin",
        )
    return order


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: uuid.UUID,
    payload: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Order:
    """Change an order's status (order owner customer or admin)."""
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    if order.customer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the order owner or an admin can change its status",
        )
    order.status = payload.status
    db.commit()
    db.refresh(order)
    return order
