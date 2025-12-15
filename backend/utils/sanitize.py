from __future__ import annotations

import re


def sanitize_text(text: str) -> str:
    """MVP sanitization to reduce prompt injection / weird control chars."""
    if not text:
        return text

    # Remove null bytes and other control chars (keep newlines/tabs)
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", " ", text)
    # Collapse excessive whitespace
    text = re.sub(r"[ \t]{3,}", "  ", text)
    return text.strip()
