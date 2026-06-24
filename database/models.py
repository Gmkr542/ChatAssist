from sqlalchemy import Column, DateTime, Integer, String
from database.db import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(String, nullable=False)
    original_romanized = Column(String, nullable=False)
    target_language = Column(String, nullable=False)
    target_translation_romanized = Column(String, nullable=False)
    english_translation = Column(String, nullable=False)
    detected_language = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
