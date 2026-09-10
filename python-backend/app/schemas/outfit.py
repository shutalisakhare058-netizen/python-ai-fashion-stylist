from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GenerateOutfitRequest(BaseModel):
    occasion: Optional[str] = ""
    season: Optional[str] = ""
    style: Optional[str] = ""
    clothes: Optional[str] = ""
    colors: Optional[str] = ""


class OutfitCard(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    outfit: str = "Recommended Outfit"
    top: str = ""
    bottom: str = ""
    dress: Optional[str] = ""
    shoes: str = ""
    accessories: str = ""
    bag: str = ""
    layering: Optional[str] = ""
    styleTip: str = Field(default="", alias="style_tip")


class GenerateOutfitResponse(BaseModel):
    outfit: OutfitCard
    demo: bool


class SaveOutfitRequest(BaseModel):
    name: str = Field(default="My Outfit")
    outfit_data: OutfitCard


class SavedOutfitOut(BaseModel):
    id: int
    name: str
    outfit_data: OutfitCard
    created_at: datetime


class RenameOutfitRequest(BaseModel):
    name: str = Field(..., min_length=1)
