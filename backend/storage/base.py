from abc import ABC, abstractmethod
from pathlib import Path


class StorageClient(ABC):
    @abstractmethod
    def save(self, deal_id: str, filename: str, data: bytes) -> Path:
        ...

    @abstractmethod
    def read(self, path: Path) -> bytes:
        ...
