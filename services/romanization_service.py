from unidecode import unidecode


class RomanizationService:
    """Service to create romanized versions of text."""

    def romanize(self, text: str, language_code: str) -> str:
        """Return a romanized representation of text for display."""
        if language_code in {"en"}:
            return text
        try:
            # Use Unidecode for many scripts; fallback to raw text if it fails.
            romanized = unidecode(text)
            return romanized or text
        except Exception:
            return text
