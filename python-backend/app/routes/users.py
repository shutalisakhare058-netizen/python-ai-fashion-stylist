from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import ProfileIn, ProfileOut
from app.utils.helpers import get_or_create_profile

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
def get_profile(db: Session = Depends(get_db)):
    return get_or_create_profile(db)


@router.put("", response_model=ProfileOut)
def update_profile(data: ProfileIn, db: Session = Depends(get_db)):
    user = get_or_create_profile(db)
    user.name = data.name or "Guest"
    user.style_preferences = data.style_preferences
    user.favorite_colors = data.favorite_colors
    user.disliked_colors = data.disliked_colors
    user.preferred_occasions = data.preferred_occasions
    user.clothing_items = data.clothing_items
    db.commit()
    db.refresh(user)
    return user
