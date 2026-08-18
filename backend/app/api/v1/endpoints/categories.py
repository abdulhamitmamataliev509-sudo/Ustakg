"""Service category endpoints: public listing + admin creation."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryOut

router = APIRouter()


@router.get("/", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)) -> list[Category]:
    """List all root categories with nested subcategories."""
    return (
        db.query(Category)
        .options(selectinload(Category.children))
        .filter(Category.parent_id.is_(None))
        .order_by(Category.title.asc())
        .all()
    )


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Category:
    """Create a category (admin only)."""
    if payload.parent_id is not None:
        parent = db.get(Category, payload.parent_id)
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )
    slug_exists = db.query(Category).filter(Category.slug == payload.slug).first()
    if slug_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Slug already in use"
        )
    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
