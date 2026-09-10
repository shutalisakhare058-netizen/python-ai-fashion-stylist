from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.conversation import Conversation
from app.schemas.chat import ConversationOut, RenameRequest

router = APIRouter(prefix="/api/chats", tags=["conversations"])


@router.get("", response_model=list[ConversationOut])
def list_chats(db: Session = Depends(get_db)):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == 1)
        .order_by(Conversation.created_at.desc(), Conversation.id.desc())
        .all()
    )


@router.post("", response_model=ConversationOut)
def create_chat(db: Session = Depends(get_db)):
    conv = Conversation(user_id=1, title="New Chat")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router.delete("/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == chat_id).first()
    if conv is None:
        raise HTTPException(status_code=404, detail="Chat not found.")
    db.delete(conv)
    db.commit()
    return {"ok": True}


@router.patch("/{chat_id}", response_model=ConversationOut)
def rename_chat(
    chat_id: int, req: RenameRequest, db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(Conversation.id == chat_id).first()
    if conv is None:
        raise HTTPException(status_code=404, detail="Chat not found.")
    conv.title = req.title
    db.commit()
    db.refresh(conv)
    return conv
