"""Simple in-memory rate limiter (per-IP). Replace with Redis in production."""
from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List

from fastapi import HTTPException, Request


class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = time.time()
        with self._lock:
            hits = self._hits[key]
            # drop old
            self._hits[key] = [t for t in hits if now - t < self.window]
            if len(self._hits[key]) >= self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {self.max_requests} requests per {self.window}s",
                )
            self._hits[key].append(now)


limiter = RateLimiter(max_requests=120, window_seconds=60)


async def rate_limit_dependency(request: Request):
    client = request.client.host if request.client else "unknown"
    limiter.check(client)
