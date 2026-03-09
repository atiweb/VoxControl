"""
Rate limiting and security middleware for VoxControl API.
"""

import logging
import time
from collections import defaultdict
from typing import Optional

from fastapi import Request, WebSocket
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter per IP address."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> bool:
        """Check if the client is within rate limits."""
        now = time.time()
        cutoff = now - self.window

        # Clean old entries
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip] if ts > cutoff
        ]

        if len(self._requests[client_ip]) >= self.max_requests:
            return False

        self._requests[client_ip].append(now)
        return True

    def get_remaining(self, client_ip: str) -> int:
        """Get remaining requests for this client."""
        now = time.time()
        cutoff = now - self.window
        recent = [ts for ts in self._requests[client_ip] if ts > cutoff]
        return max(0, self.max_requests - len(recent))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""

    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"

        # Skip rate limiting for static files
        if request.url.path.startswith("/static"):
            return await call_next(request)

        if not self.rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests. Please try again later."},
            )

        response = await call_next(request)
        remaining = self.rate_limiter.get_remaining(client_ip)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.max_requests)
        return response
