"""Security, rate limiting, and hardening middleware for FastAPI.
"""

import time
import hmac
from typing import Dict
from fastapi import Request, HTTPException, Header, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from app.core.config import settings


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
        if settings.REQUIRE_AUTH and settings.API_KEY_SECRET and request.url.path != "/api/v1/health":
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
    """In-memory sliding window rate limiter per client IP address."""
    
    def __init__(self):
        # Maps IP -> list of timestamps
        self.requests: Dict[str, list] = {}
        
    def check_rate_limit(self, client_ip: str, max_requests: int, window_seconds: int = 60):
        now = time.time()
        timestamps = self.requests.get(client_ip, [])
        # Keep only timestamps within window
        valid_timestamps = [ts for ts in timestamps if now - ts < window_seconds]
        
        if len(valid_timestamps) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded ({max_requests} req/{window_seconds}s). Please try again shortly."
            )
            
        valid_timestamps.append(now)
        self.requests[client_ip] = valid_timestamps


rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    """Uses forwarded IPs only when a trusted reverse proxy is explicitly enabled."""
    forwarded = request.headers.get("X-Forwarded-For")
    if settings.TRUST_PROXY_HEADERS and forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"
