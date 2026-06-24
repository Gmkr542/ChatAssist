from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.models import ChatMessage

router = APIRouter()


@router.get("/history")
async def get_history():
    """Return the latest chat translation history records."""
    with SessionLocal() as db:
        messages = db.query(ChatMessage).order_by(ChatMessage.timestamp.desc()).limit(50).all()
        payload = [
            {
                "id": msg.id,
                "detected_language": msg.detected_language,
                "original_text": msg.original_text,
                "original_romanized": msg.original_romanized,
                "target_language": msg.target_language,
                "target_translation_romanized": msg.target_translation_romanized,
                "english_translation": msg.english_translation,
                "timestamp": msg.timestamp.isoformat() + "Z",
            }
            for msg in messages
        ]

    return JSONResponse(content={"messages": payload})
