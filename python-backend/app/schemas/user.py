from datetime import datetime

from pydantic import BaseModel


class ProfileIn(BaseModel):
    name: str = "Guest"
    style_preferences: str = ""
    favorite_colors: str = ""
    disliked_colors: str = ""
    preferred_occasions: str = ""
    clothing_items: str = ""


class ProfileOut(ProfileIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
