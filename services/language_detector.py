from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

LANGUAGE_MAP = {
    "en": "English",
    "ko": "Korean",
    "ja": "Japanese",
    "zh-cn": "Chinese",
    "zh-tw": "Chinese",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "ar": "Arabic",
    "ru": "Russian",
}


class LanguageDetector:
    """Service to detect language from text."""

    def detect_language(self, text: str) -> str:
        """Detect the source language code for the given text."""
        try:
            detected = detect(text)
        except Exception:
            return "en"

        if detected.startswith("zh"):
            return "zh-cn"
        if detected not in LANGUAGE_MAP:
            return "en"
        return detected

    def get_language_name(self, code: str) -> str:
        """Map a language code to a human-readable language name."""
        return LANGUAGE_MAP.get(code, "English")
