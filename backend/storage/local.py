from pathlib import Path

from .base import StorageClient


class LocalStorage(StorageClient):
    def __init__(self, root: str = "data"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, deal_id: str, filename: str, data: bytes) -> Path:
        deal_dir = self.root / deal_id
        deal_dir.mkdir(parents=True, exist_ok=True)
        path = deal_dir / filename
        path.write_bytes(data)
        return path

    def read(self, path: Path) -> bytes:
        return path.read_bytes()
