from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base


class SavedOutfit(Base):
    __tablename__ = "saved_outfits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, default=1)
    name = Column(String, nullable=False)
    outfit_data = Column(Text, nullable=False)  # JSON string
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
