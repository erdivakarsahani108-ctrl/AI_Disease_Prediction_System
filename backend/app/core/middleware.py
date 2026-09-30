"""Request correlation ID + basic hardening middleware."""
from __future__ import annotations

import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        cid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.correlation_id = cid
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = cid
        response.headers["X-Response-Time-ms"] = f"{elapsed:.1f}"
        return response
