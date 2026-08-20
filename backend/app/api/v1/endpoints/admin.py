"""Admin dashboard endpoints (ADMIN only)."""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models.enums import OrderStatus
from app.models.master import MasterProfile
from app.models.order import Order
from app.models.user import User
from app.schemas.admin import AdminStats

router = APIRouter()


@router.get("/stats", response_model=AdminStats)
def admin_stats(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> AdminStats:
    """Aggregate platform statistics for the admin dashboard."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_masters = db.query(func.count(MasterProfile.id)).scalar() or 0
    open_orders = (
        db.query(func.count(Order.id)).filter(Order.status == OrderStatus.OPEN).scalar() or 0
    )
    return AdminStats(
        total_users=total_users,
        total_masters=total_masters,
        open_orders=open_orders,
        system_status="ok",
    )