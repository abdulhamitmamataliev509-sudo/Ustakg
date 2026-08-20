"""Admin/user-management endpoints (ADMIN only)."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models.master import MasterProfile
from app.models.user import User
from app.schemas.admin import UserActionOut
from app.schemas.user import UserOut

router = APIRouter()


@router.get("/", response_model=list[UserOut])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> list[User]:
    """List users, paginated (admin only)."""
    return (
        db.query(User)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/{user_id}/verify", response_model=UserActionOut)
def verify_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> UserActionOut:
    """Mark a master profile as verified (admin only)."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    profile = (
        db.query(MasterProfile).filter(MasterProfile.user_id == user.id).first()
    )
    is_verified: bool | None = None
    if profile is not None:
        profile.is_verified = True
        is_verified = True
    db.commit()
    return UserActionOut(status="ok", user_id=user.id, is_verified=is_verified)


@router.post("/{user_id}/block", response_model=UserActionOut)
def toggle_block_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
) -> UserActionOut:
    """Toggle a user's active/blocked state (admin only)."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = not user.is_active
    db.commit()
    return UserActionOut(status="ok", user_id=user.id, is_active=user.is_active)
