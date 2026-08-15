"""IERL AI Equity Intelligence OS — Integrated Production Server.

Serves the institutional research frontend and FastAPI backend API engines.
"""

import os
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import settings
from app.core.security import ApiSecurityMiddleware, SecurityHeadersMiddleware
from app.api import health, market, comparison, probability, options, strategies, query, research_data, watchlist

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
app.include_router(health.router)
app.include_router(market.router)
app.include_router(comparison.router)
app.include_router(probability.router)
app.include_router(options.router)
app.include_router(strategies.router)
app.include_router(query.router)
app.include_router(research_data.router)
app.include_router(watchlist.router)

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
