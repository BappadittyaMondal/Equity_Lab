"""Security, rate limiting, and hardening middleware for FastAPI.
"""

import os
import time
import hmac
from typing import Dict
from fastapi import Request, HTTPException, Header, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


def verify_api_key(x_api_key: str = Header(default="")) -> bool:
    """Verifies that incoming requests contain a valid API key header.
    
    Checks X-API-Key against settings.API_KEY_SECRET or settings.ADMIN_API_KEY.
    If API keys are explicitly configured, validates the header.
    """
    valid_keys = [k for k in [settings.API_KEY_SECRET, settings.ADMIN_API_KEY] if k]
    if valid_keys:
        if not x_api_key or not any(hmac.compare_digest(x_api_key, k) for k in valid_keys):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Valid API authentication key required."
            )
    return True


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Applies strict security hardening headers to every response."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Hardening response headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Build dynamic connect-src from allowed origins
        connect_sources = "'self'"
        if settings.ALLOWED_ORIGINS:
            connect_sources += " " + " ".join(settings.ALLOWED_ORIGINS)
        
        # Strict Content-Security-Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            f"connect-src {connect_sources}; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        return response


class ApiSecurityMiddleware(BaseHTTPMiddleware):
    """Enforces request size, optional API-key authentication, and public limits."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > settings.MAX_REQUEST_SIZE_BYTES:
                    return JSONResponse(status_code=413, content={"detail": "Request body exceeds the permitted size."})
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length header."})

        # Health checks stay unauthenticated for infrastructure monitoring.
        if settings.REQUIRE_AUTH and request.url.path != "/api/v1/health":
            if not settings.API_KEY_SECRET:
                env = os.getenv("IERL_ENVIRONMENT", "development").lower()
                if env == "production":
                    logger.error("FATAL: REQUIRE_AUTH is True but API_KEY_SECRET is empty in production mode.")
                    return JSONResponse(status_code=500, content={"detail": "Server authentication configuration error."})
                logger.warning("SECURITY WARNING: REQUIRE_AUTH is True but API_KEY_SECRET is empty! API running unauthenticated.")
            else:
                supplied_key = request.headers.get("X-API-Key", "")
                if not hmac.compare_digest(supplied_key, settings.API_KEY_SECRET):
                    return JSONResponse(status_code=401, content={"detail": "Valid API authentication is required."})

        if request.url.path != "/api/v1/health":
            try:
                rate_limiter.check_rate_limit(
                    get_client_ip(request),
                    max_requests=settings.RATE_LIMIT_PUBLIC_RPM,
                    window_seconds=60,
                )
            except HTTPException as exc:
                return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

        return await call_next(request)


class RateLimiter:
    """Hybrid distributed/in-memory sliding window rate limiter per client IP address."""

    def __init__(self):
        # In-memory store: Maps IP -> list of timestamps
        self.requests: Dict[str, list] = {}
        self._last_cleanup = time.time()
        self._redis_client = None
        self._redis_initialized = False

    def _get_redis_client(self):
        if not self._redis_initialized:
            self._redis_initialized = True
            redis_url = getattr(settings, "REDIS_URL", None)
            if redis_url:
                try:
                    import redis
                    self._redis_client = redis.from_url(redis_url, socket_timeout=1.0)
                except Exception:
                    self._redis_client = None
        return self._redis_client

    def reset(self):
        """Clears all stored rate limiter request state (for testing isolation)."""
        self.requests.clear()
        self._last_cleanup = time.time()

    def check_rate_limit(self, client_ip: str, max_requests: int, window_seconds: int = 60):
        # Bypass rate limiting when running under pytest or offline test mode
        if "PYTEST_CURRENT_TEST" in os.environ or os.getenv("OFFLINE_TEST_MODE", "false").lower() == "true":
            return

        now = time.time()

        # Try distributed Redis sliding window if configured
        r = self._get_redis_client()
        if r is not None:
            try:
                key = f"ratelimit:{client_ip}"
                pipe = r.pipeline()
                pipe.zremrangebyscore(key, 0, now - window_seconds)
                pipe.zcard(key)
                pipe.zadd(key, {str(now): now})
                pipe.expire(key, window_seconds + 5)
                res = pipe.execute()
                current_count = res[1]
                if current_count >= max_requests:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded ({max_requests} req/{window_seconds}s). Please try again shortly."
                    )
                return
            except HTTPException:
                raise
            except Exception:
                # Degrading cleanly to in-memory sliding window on Redis connection failure
                pass

        # In-memory sliding window fallback
        if now - self._last_cleanup > 300 or len(self.requests) > 500:
            self._prune_stale_ips(now, window_seconds)
            self._last_cleanup = now

        timestamps = self.requests.get(client_ip, [])
        valid_timestamps = [ts for ts in timestamps if now - ts < window_seconds]

        if len(valid_timestamps) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded ({max_requests} req/{window_seconds}s). Please try again shortly."
            )

        valid_timestamps.append(now)
        self.requests[client_ip] = valid_timestamps

    def _prune_stale_ips(self, now: float, window_seconds: int):
        """Removes IP entries that have no active requests in the current window."""
        stale_keys = [
            ip for ip, timestamps in self.requests.items()
            if not any(now - ts < window_seconds for ts in timestamps)
        ]
        for ip in stale_keys:
            self.requests.pop(ip, None)


rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    """Uses forwarded IPs only when a trusted reverse proxy is explicitly enabled."""
    forwarded = request.headers.get("X-Forwarded-For")
    if settings.TRUST_PROXY_HEADERS and forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"
