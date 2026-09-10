import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.outfit import SavedOutfit
from app.schemas.outfit import (
    GenerateOutfitRequest,
    GenerateOutfitResponse,
    OutfitCard,
    RenameOutfitRequest,
    SavedOutfitOut,
    SaveOutfitRequest,
)
from app.services.outfit_service import generate_outfit
from app.utils.helpers import get_or_create_profile, profile_to_dict

router = APIRouter(prefix="/api/outfits", tags=["outfits"])


@router.post("/generate", response_model=GenerateOutfitResponse)
def generate(req: GenerateOutfitRequest, db: Session = Depends(get_db)):
    profile = get_or_create_profile(db)
    result = generate_outfit(req.model_dump(), profile_to_dict(profile))
    return GenerateOutfitResponse(
        outfit=OutfitCard(**result["outfit"]), demo=result["demo"]
    )


@router.get("/saved", response_model=list[SavedOutfitOut])
def list_saved(db: Session = Depends(get_db)):
    rows = (
        db.query(SavedOutfit)
        .filter(SavedOutfit.user_id == 1)
        .order_by(SavedOutfit.created_at.desc(), SavedOutfit.id.desc())
        .all()
    )
    return [
        SavedOutfitOut(
            id=r.id,
            name=r.name,
            outfit_data=OutfitCard(**json.loads(r.outfit_data)),
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.post("/save", response_model=SavedOutfitOut)
def save(req: SaveOutfitRequest, db: Session = Depends(get_db)):
    row = SavedOutfit(
        user_id=1,
        name=req.name,
        outfit_data=req.outfit_data.model_dump_json(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return SavedOutfitOut(
        id=row.id,
        name=row.name,
        outfit_data=req.outfit_data,
        created_at=row.created_at,
    )


@router.delete("/{outfit_id}")
def delete(outfit_id: int, db: Session = Depends(get_db)):
    row = db.query(SavedOutfit).filter(SavedOutfit.id == outfit_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Outfit not found.")
    db.delete(row)
    db.commit()
    return {"ok": True}


@router.patch("/{outfit_id}", response_model=SavedOutfitOut)
def rename(
    outfit_id: int, req: RenameOutfitRequest, db: Session = Depends(get_db)
):
    row = db.query(SavedOutfit).filter(SavedOutfit.id == outfit_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Outfit not found.")
    row.name = req.name
    db.commit()
    db.refresh(row)
    return SavedOutfitOut(
        id=row.id,
        name=row.name,
        outfit_data=OutfitCard(**json.loads(row.outfit_data)),
        created_at=row.created_at,
    )
