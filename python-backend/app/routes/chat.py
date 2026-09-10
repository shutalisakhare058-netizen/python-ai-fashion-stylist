from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatRequest, ChatResponse, MessageOut
from app.services.claude_service import get_chat_reply
from app.utils.helpers import get_or_create_profile, profile_to_dict

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    try:
        profile = get_or_create_profile(db)

        conversation = None
        if req.conversation_id:
            conversation = (
                db.query(Conversation)
                .filter(Conversation.id == req.conversation_id)
                .first()
            )
        if conversation is None:
            title = req.message[:40] + ("…" if len(req.message) > 40 else "")
            conversation = Conversation(user_id=1, title=title)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        db.add(
            Message(
                conversation_id=conversation.id,
                role="user",
                content=req.message,
            )
        )
        db.commit()

        history = (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at, Message.id)
            .all()
        )
        turns = [{"role": m.role, "content": m.content} for m in history]

        result = get_chat_reply(turns, profile_to_dict(profile))

        db.add(
            Message(
                conversation_id=conversation.id,
                role="assistant",
                content=result["reply"],
            )
        )
        db.commit()

        return ChatResponse(
            reply=result["reply"],
            conversation_id=conversation.id,
            demo=result["demo"],
        )
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while generating a reply.",
        )


@router.get("/chat/{conversation_id}/messages", response_model=list[MessageOut])
def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at, Message.id)
        .all()
    )
