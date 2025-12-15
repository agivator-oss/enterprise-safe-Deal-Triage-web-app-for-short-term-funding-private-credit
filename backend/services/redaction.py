from __future__ import annotations

import re
from typing import Any

_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)

# Simple phone heuristic: +country / leading 0, spaced/dashed blocks
_PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}\b")

# Long digit strings (account numbers, IDs)
_LONG_DIGITS_RE = re.compile(r"\b\d{9,}\b")

# Very simple 'Person Name' heuristic: 2-3 capitalised words (avoid sentence-start false positives a bit)
_NAME_RE = re.compile(r"\b([A-Z][a-z]{2,})(\s+[A-Z][a-z]{2,}){1,2}\b")


def redact(text: str) -> str:
    """Mask obvious PII patterns.

    Notes:
    - This is MVP-grade heuristic redaction, not a privacy guarantee.
    - Applied before sending to LLM and before persisting LLM outputs.
    """

    if not text:
        return text

    redacted = text
    redacted = _EMAIL_RE.sub("[REDACTED_EMAIL]", redacted)
    redacted = _LONG_DIGITS_RE.sub("[REDACTED_NUMBER]", redacted)

    # Replace phone-like patterns conservatively (avoid clobbering short numeric terms)
    def _mask_phone(m: re.Match[str]) -> str:
        s = m.group(0)
        digits = re.sub(r"\D", "", s)
        if len(digits) < 9:
            return s
        return "[REDACTED_PHONE]"

    redacted = _PHONE_RE.sub(_mask_phone, redacted)

    # Names heuristic (best-effort)
    redacted = _NAME_RE.sub("[REDACTED_NAME]", redacted)

    return redacted


def redact_obj(obj: Any) -> Any:
    """Recursively redact strings in JSON-like objects."""
    if obj is None:
        return None
    if isinstance(obj, str):
        return redact(obj)
    if isinstance(obj, list):
        return [redact_obj(v) for v in obj]
    if isinstance(obj, dict):
        return {k: redact_obj(v) for k, v in obj.items()}
    return obj
