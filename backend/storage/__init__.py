"""Storage abstraction layer.

Local filesystem implementation is used for dev.
Future adapters: S3, Azure Blob.
"""

from .base import StorageClient
from .local import LocalStorage

__all__ = ["StorageClient", "LocalStorage"]
