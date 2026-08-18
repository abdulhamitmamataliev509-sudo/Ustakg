"""Service-master (usta) endpoints: listing, public profile, profile update."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_active_master
from app.core.database import get_db
from app.models.category import Category, MasterCategory
from app.models.master import MasterProfile
from app.schemas.master import MasterProfileOut, MasterProfileUpdate

router = APIRouter()


@router.get("/", response_model=list[MasterProfileOut])
def list_masters(
    rating: float | None = None,
    category_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
) -> list[MasterProfile]:
    """List masters, optionally filtered by minimum rating and category."""
    query = db.query(MasterProfile).options(selectinload(MasterProfile.categories))
    if rating is not None:
        query = query.filter(MasterProfile.rating >= rating)
    if category_id is not None:
        query = query.join(
            MasterCategory, MasterCategory.master_id == MasterProfile.id
        ).filter(MasterCategory.category_id == category_id)
    return query.order_by(MasterProfile.rating.desc()).all()


@router.put("/profile", response_model=MasterProfileOut)
def update_my_profile(
    payload: MasterProfileUpdate,
    profile: MasterProfile = Depends(get_current_active_master),
    db: Session = Depends(get_db),
) -> MasterProfile:
    """Update the current master's own profile."""
    for field in ("bio", "experience_years", "avatar_url"):
        value = getattr(payload, field)
        if value is not None:
            setattr(profile, field, value)
    if payload.category_ids is not None:
        categories = (
            db.query(Category)
            .filter(Category.id.in_(payload.category_ids))
            .all()
        )
        if len(categories) != len(set(payload.category_ids)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more categories not found",
            )
        profile.categories = categories
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{master_id}", response_model=MasterProfileOut)
def get_master(
    master_id: uuid.UUID, db: Session = Depends(get_db)
) -> MasterProfile:
    """Fetch a master's public profile."""
    profile = (
        db.query(MasterProfile)
        .options(selectinload(MasterProfile.categories))
        .filter(MasterProfile.id == master_id)
        .first()
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Master not found"
        )
    return profile
