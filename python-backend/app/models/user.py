from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, default="Guest")
    style_preferences = Column(Text, nullable=False, default="")
    favorite_colors = Column(Text, nullable=False, default="")
    disliked_colors = Column(Text, nullable=False, default="")
    preferred_occasions = Column(Text, nullable=False, default="")
    clothing_items = Column(Text, nullable=False, default="")
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
