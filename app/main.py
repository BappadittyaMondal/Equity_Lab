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
    from app.api import health, market, comparison, probability, options, strategies, query, research_data, watchlist, decision, watchlist_digest, monitoring, admin, portfolio, multibagger, technical
except ModuleNotFoundError as err:
    # If the error is due to top-level app package resolution, try fallback, otherwise re-raise the missing package error loudly
    if err.name in ("app", "core", "api") or (err.name and err.name.startswith("app.")):
        try:
            from core.config import settings
            settings._validate_cors_settings()
            from core.security import ApiSecurityMiddleware, SecurityHeadersMiddleware, verify_api_key
            import health, market, comparison, probability, options, strategies, query, research_data, watchlist, decision, watchlist_digest, monitoring, admin, portfolio, multibagger, technical
        except ModuleNotFoundError as inner_err:
            import logging
            logging.getLogger(__name__).error(f"Failed to import required backend router: {inner_err}")
            raise inner_err
    else:
        import logging
        logging.getLogger(__name__).error(f"Failed to start server due to missing dependency '{err.name}': {err}")
        raise err
import asyncio
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

async def _background_market_data_refresh_loop():
    """Background task running every 6 hours to ensure target market data is fresh (<72h gap)."""
    try:
        from app.services.market_data import AutoRefreshMarketDataService
    except ImportError:
        from services.market_data import AutoRefreshMarketDataService
    
    while True:
        try:
            logger.info("Triggering automated background market data freshness sync...")
            res = await AutoRefreshMarketDataService.auto_refresh_universe(max_age_hours=72)
            logger.info("Automated background market data refresh completed: %s", res)
            try:
                from app.services.decision_brain.arbiter import precalculate_universe_scorecards
                calc_res = precalculate_universe_scorecards()
                logger.info("Asynchronous pre-computation of universe scorecards completed: %s", calc_res)
            except Exception as calc_err:
                logger.warning("Universe scorecard pre-computation encountered warning: %s", calc_err)
        except Exception as e:
            logger.warning("Automated background market data refresh loop encountered error: %s", e)
        # Wait 6 hours before next automatic scan cycle
        await asyncio.sleep(21600)

async def _background_model_retrain_loop():
    """Background task running every 24 hours to automatically evaluate and retrain baseline ML model."""
    while True:
        try:
            # Wait 24 hours between retraining cycles
            await asyncio.sleep(86400)
            logger.info("Triggering automated background ML model retraining evaluation...")
            try:
                from app.services.ml.baseline_model import evaluate_and_retrain_model
            except ImportError:
                from services.ml.baseline_model import evaluate_and_retrain_model
            res = evaluate_and_retrain_model()
            logger.info("Automated background ML model retraining completed: %s", res)
        except Exception as e:
            logger.warning("Automated background ML model retraining loop encountered error: %s", e)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        try:
            from app.core.db_health import check_db_health
        except ImportError:
            from core.db_health import check_db_health
        health_status = check_db_health()
        if health_status.get("is_vercel") and not health_status.get("is_postgres"):
            if os.getenv("STRICT_VERCEL_POSTGRES_GATE", "1") == "1":
                logger.critical("BOOT ABORTED: Vercel environment detected without PostgreSQL DATABASE_URL. Set DATABASE_URL or STRICT_VERCEL_POSTGRES_GATE=0.")
                raise RuntimeError("Deployment aborted: Vercel environment requires PostgreSQL DATABASE_URL to prevent silent data loss.")
    except Exception as e:
        if isinstance(e, RuntimeError):
            raise e
        logger.warning(f"Database health startup check warning: {e}")
    refresh_task = asyncio.create_task(_background_market_data_refresh_loop())
    retrain_task = asyncio.create_task(_background_model_retrain_loop())
    yield
    refresh_task.cancel()
    retrain_task.cancel()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(ApiSecurityMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Restrict CORS to explicit allowed origins from environment configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS or ["*"],
    allow_origin_regex=r"https://.*\.vercel\.app",
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
app.include_router(multibagger.router, dependencies=auth_deps)
app.include_router(technical.router, dependencies=auth_deps)
app.include_router(admin.router)

# Mount Frontend Assets
frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend_deploy")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
    js_dir = os.path.join(frontend_dir, "js")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")
    comp_dir = os.path.join(frontend_dir, "components")
    if os.path.exists(comp_dir):
        app.mount("/components", StaticFiles(directory=comp_dir), name="components")
    data_dir = os.path.join(frontend_dir, "data")
    if os.path.exists(data_dir):
        app.mount("/data", StaticFiles(directory=data_dir), name="data")

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
