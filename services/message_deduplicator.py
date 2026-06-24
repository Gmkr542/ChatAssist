import hashlib


class MessageDeduplicator:
    """Deduplicate text messages to avoid repeated translation."""

    def __init__(self):
        self.seen_hashes = set()

    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def is_duplicate(self, text: str) -> bool:
        """Check whether the text has already been processed."""
        return self._hash(text) in self.seen_hashes

    def add(self, text: str) -> None:
        """Remember a new message text by its hash."""
        self.seen_hashes.add(self._hash(text))
