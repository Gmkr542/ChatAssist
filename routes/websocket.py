import base64
import io
import json
from datetime import datetime
from hashlib import sha256

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from PIL import Image

from database.db import SessionLocal
from database.models import ChatMessage
from services.language_detector import LanguageDetector
from services.translation_service import TranslationService
from services.romanization_service import RomanizationService
from services.message_deduplicator import MessageDeduplicator

router = APIRouter()

# Initialize services lazily or on first WebSocket connection
_ocr_service = None
_language_detector = None
_translation_service = None
_romanization_service = None
_deduplicator = None


def _get_services():
    """Initialize services on first use."""
    global _ocr_service, _language_detector, _translation_service, _romanization_service, _deduplicator
    if _ocr_service is None:
        from services.ocr_service import OCRService
        _ocr_service = OCRService()
    if _language_detector is None:
        _language_detector = LanguageDetector()
    if _translation_service is None:
        _translation_service = TranslationService()
    if _romanization_service is None:
        _romanization_service = RomanizationService()
    if _deduplicator is None:
        _deduplicator = MessageDeduplicator()
    return _ocr_service, _language_detector, _translation_service, _romanization_service, _deduplicator


def get_db() -> Session:
    """Provide a database session for saving chat records."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Accept a WebSocket client and stream translation results live."""
    await websocket.accept()
    
    # Initialize services on WebSocket connection
    ocr_service, language_detector, translation_service, romanization_service, deduplicator = _get_services()
    
    try:
        while True:
            payload = await websocket.receive_text()
            data = json.loads(payload)
            if data.get("type") != "screenshot":
                await websocket.send_json({"type": "error", "detail": "Unsupported message type."})
                continue

            target_language = data.get("target_language", "en")
            image_data = data.get("image_data")
            if not image_data:
                await websocket.send_json({"type": "error", "detail": "No image data provided."})
                continue

            try:
                image = _decode_screenshot(image_data)
                extracted_text = ocr_service.extract_text(image)
            except Exception as exc:
                await websocket.send_json({"type": "error", "detail": f"OCR failed: {exc}"})
                continue

            if not extracted_text.strip():
                await websocket.send_json({"type": "status", "detail": "No text detected."})
                continue

            text_lines = [line.strip() for line in extracted_text.split("\n") if line.strip()]
            for line in text_lines:
                if deduplicator.is_duplicate(line):
                    continue
                deduplicator.add(line)

                detected_code = language_detector.detect_language(line)
                detected_name = language_detector.get_language_name(detected_code)
                original_romanized = romanization_service.romanize(line, detected_code)
                target_translation = translation_service.translate_text(line, target_language)
                target_romanized = romanization_service.romanize(target_translation, target_language)
                english_translation = translation_service.translate_text(line, "en")

                message_record = ChatMessage(
                    original_text=line,
                    original_romanized=original_romanized,
                    target_language=target_language,
                    target_translation_romanized=target_romanized,
                    english_translation=english_translation,
                    detected_language=detected_name,
                    timestamp=datetime.utcnow(),
                )

                with SessionLocal() as db:
                    db.add(message_record)
                    db.commit()
                    db.refresh(message_record)

                await websocket.send_json({
                    "type": "translation",
                    "payload": {
                        "id": message_record.id,
                        "detected_language": detected_name,
                        "original_text": line,
                        "original_romanized": original_romanized,
                        "target_language": target_language,
                        "target_translation_romanized": target_romanized,
                        "english_translation": english_translation,
                        "timestamp": message_record.timestamp.isoformat() + "Z",
                    },
                })
    except WebSocketDisconnect:
        return


def _decode_screenshot(base64_data: str) -> Image.Image:
    """Decode a base64-encoded screenshot into a Pillow image."""
    header, _, encoded = base64_data.partition(",")
    image_bytes = base64.b64decode(encoded or header)
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")
