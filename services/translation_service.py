from deep_translator import GoogleTranslator

SUPPORTED_TARGETS = {
    "en": "english",
    "ko": "korean",
    "ja": "japanese",
    "zh-cn": "chinese",
    "hi": "hindi",
    "te": "telugu",
    "ta": "tamil",
    "ar": "arabic",
    "ru": "russian",
}


class TranslationService:
    """Service responsible for translating text to desired languages."""

    def translate_text(self, text: str, target_language: str) -> str:
        """Translate input text into the target language."""
        translator_language = SUPPORTED_TARGETS.get(target_language, "english")
        try:
            translated = GoogleTranslator(source="auto", target=translator_language).translate(text)
        except Exception:
            # Fallback to original text on service failure
            translated = text
        return translated
