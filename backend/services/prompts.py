from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.models.prompt_version import PromptVersion
from backend.utils.hashing import sha256_text


PROMPTS_ROOT = Path(settings.prompts_root)


def load_prompt_template(name: str, version: str) -> str:
    path = PROMPTS_ROOT / name / f"{version}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def ensure_prompt_version(db: Session, *, name: str, version: str, content: str) -> PromptVersion:
    content_hash = sha256_text(content)

    existing = (
        db.query(PromptVersion)
        .filter(PromptVersion.name == name, PromptVersion.version == version)
        .one_or_none()
    )
    if existing:
        return existing

    pv = PromptVersion(name=name, version=version, content_hash=content_hash, content=content)
    db.add(pv)
    db.flush()
    return pv
