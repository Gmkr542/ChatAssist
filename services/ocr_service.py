import easyocr
from PIL import Image


class OCRService:
    """Service responsible for extracting text from images."""

    def __init__(self):
        # Lazy initialization: reader will be created on first use.
        self.reader = None

    def _initialize_reader(self):
        """Initialize the OCR reader on first use."""
        if self.reader is None:
            # Use simpler language list to avoid EasyOCR compatibility issues.
            self.reader = easyocr.Reader(
                ["en", "ch_sim"], gpu=False
            )

    def extract_text(self, image: Image.Image) -> str:
        """Run OCR on a screenshot image and return text."""
        try:
            self._initialize_reader()
            result = self.reader.readtext(image, detail=0, paragraph=True)
        except Exception:
            return ""
        return "\n".join(result).strip()
