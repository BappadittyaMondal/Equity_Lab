"""IERL AI Equity Intelligence OS — Integrated Production Server.

Serves the institutional research frontend and FastAPI backend API engines.
"""

import os
import sys

# Ensure project root is in sys.path so 'import app...' works regardless of working directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
app_dir = os.path.abspath(os.path.dirname(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from fastapi import FastAPI, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

try:
    from app.core.config import settings
    # Validate CORS settings for production environment
    settings._validate_cors_settings()
    from app.core.security import ApiSecurityMiddleware, SecurityHeadersMiddleware, verify_api_key
    from app.api import health, market, comparison, probability, options, strategies, query, research_data, watchlist, decision, watchlist_digest, monitoring, admin, portfolio
except ModuleNotFoundError:
    from core.config import settings
    # Validate CORS settings for production environment
    settings._validate_cors_settings()
    from core.security import ApiSecurityMiddleware, SecurityHeadersMiddleware, verify_api_key
    from api import health, market, comparison, probability, options, strategies, query, research_data, watchlist, decision, watchlist_digest, monitoring, admin, portfolio

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(ApiSecurityMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Restrict CORS to explicit allowed origins from environment configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Global Exception Handler for uniform JSON error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An unexpected error occurred during analytical execution.",
            "path": request.url.path
        }
    )

# Include API Routers under /api/v1
# Health check endpoints stay unauthenticated for infrastructure monitoring / readiness probes
app.include_router(health.router)

# All product API routers require API key authentication
auth_deps = [Depends(verify_api_key)]
app.include_router(market.router, dependencies=auth_deps)
app.include_router(comparison.router, dependencies=auth_deps)
app.include_router(probability.router, dependencies=auth_deps)
app.include_router(options.router, dependencies=auth_deps)
app.include_router(strategies.router, dependencies=auth_deps)
app.include_router(query.router, dependencies=auth_deps)
app.include_router(research_data.router, dependencies=auth_deps)
app.include_router(watchlist.router, dependencies=auth_deps)
app.include_router(decision.router, dependencies=auth_deps)
app.include_router(watchlist_digest.router, dependencies=auth_deps)
app.include_router(monitoring.router, dependencies=auth_deps)
app.include_router(portfolio.router, dependencies=auth_deps)
app.include_router(admin.router)

# Mount Frontend Assets
frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend_deploy")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/", include_in_schema=False)
def serve_ui():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "ONLINE", "message": "Backend engine active. Frontend UI loading."}


@app.get("/style.css", include_in_schema=False)
def serve_ui_stylesheet():
    stylesheet_path = os.path.join(frontend_dir, "style.css")
    if os.path.exists(stylesheet_path):
        return FileResponse(stylesheet_path, media_type="text/css")
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Frontend stylesheet is unavailable."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
