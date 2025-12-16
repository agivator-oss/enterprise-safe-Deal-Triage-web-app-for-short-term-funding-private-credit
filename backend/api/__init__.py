"""API routers."""

from .health import router as health_router
from .deals import router as deals_router

__all__ = ["health_router", "deals_router"]
