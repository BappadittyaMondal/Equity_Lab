"""Metrics middleware – simple request/error counting for admin stats"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import datetime

# Shared counters (reset hourly in admin module)
_request_counters = {"total": 0, "errors": 0}
_last_reset = datetime.datetime.utcnow()

def reset_counters_if_needed():
    global _request_counters, _last_reset
    now = datetime.datetime.utcnow()
    if (now - _last_reset).total_seconds() >= 3600:
        _request_counters = {"total": 0, "errors": 0}
        _last_reset = now

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        reset_counters_if_needed()
        _request_counters["total"] += 1
        try:
            response: Response = await call_next(request)
            if response.status_code >= 400:
                _request_counters["errors"] += 1
            return response
        except Exception:
            _request_counters["errors"] += 1
            raise
