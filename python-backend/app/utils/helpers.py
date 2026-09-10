"""Shared helper utilities."""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


def get_or_create_profile(db: Session) -> User:
    """Single-profile app: always uses id=1, creating it if missing."""
    user = db.query(User).filter(User.id == 1).first()
    if user is None:
        user = User(id=1, name="Guest")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def profile_to_dict(user: Optional[User]) -> dict:
    if user is None:
        return {}
    return {
        "name": user.name,
        "style_preferences": user.style_preferences,
        "favorite_colors": user.favorite_colors,
        "disliked_colors": user.disliked_colors,
        "preferred_occasions": user.preferred_occasions,
        "clothing_items": user.clothing_items,
    }
