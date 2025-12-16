from pathlib import Path
import os
import uuid

from .base import StorageClient


class LocalStorage(StorageClient):
    def __init__(self, root: str = "data"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, deal_id: str, filename: str, data: bytes) -> Path:
        deal_dir = self.root / deal_id
        deal_dir.mkdir(parents=True, exist_ok=True)
        safe_name = self._safe_filename(filename)
        path = deal_dir / safe_name

        # Atomic write: write to temp file then replace.
        tmp_path = deal_dir / f".{safe_name}.{uuid.uuid4().hex}.tmp"
        tmp_path.write_bytes(data)
        os.replace(tmp_path, path)

        return path

    def read(self, path: Path) -> bytes:
        return path.read_bytes()

    @staticmethod
    def _safe_filename(filename: str) -> str:
        # Prevent path traversal and weird empty names.
        name = Path(filename or "").name
        if not name:
            raise ValueError("Missing filename")
        # Very small hardening: strip null bytes.
        name = name.replace("\x00", "")
        return name
