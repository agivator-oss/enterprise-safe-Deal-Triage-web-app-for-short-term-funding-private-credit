from __future__ import annotations

from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.core.config import settings


class DevAuthMiddleware(BaseHTTPMiddleware):
    """Placeholder auth.

    Sets request.state.actor based on X-Dev-Actor header.
    Extension point: replace with SSO (Okta/Azure AD) and proper identity claims.
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        if not settings.dev_auth_enabled:
            request.state.actor = "anonymous"
            return await call_next(request)

        actor = request.headers.get("x-dev-actor") or settings.dev_auth_default_actor
        request.state.actor = actor
        return await call_next(request)
