import sys
import os
import traceback
import logging

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

startup_error = None
logger = logging.getLogger(__name__)
app = FastAPI(
    title="MyTaxFiling API",
    description="Backend API for MyTaxFiling",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

try:
    from app.core.config import settings
    from app.api.v1 import api_router

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.FRONTEND_URLS,
        allow_origin_regex=r"https://.*\.manus\.computer",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
except Exception as e:
    startup_error = traceback.format_exc()
    print("STARTUP ERROR:", startup_error)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled backend error on %s %s", request.method, request.url.path)
    origin = request.headers.get("origin", "")
    headers = {}
    if origin.endswith(".manus.computer"):
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Vary": "Origin",
        }
    return JSONResponse(
        status_code=500,
        content={"detail": f"Backend diagnostic: {type(exc).__name__}: {exc}"},
        headers=headers,
    )


@app.get("/")
@app.get("/api")
@app.get("/api/index")
async def root():
    if startup_error:
        return JSONResponse(
            status_code=500,
            content={"status": "startup_failed", "error": startup_error}
        )
    return {
        "message": "MyTaxFiling API",
        "version": "1.0.0",
        "docs": "/api/docs",
    }


@app.get("/health")
@app.get("/api/health")
@app.get("/api/index/health")
async def health_check():
    if startup_error:
        return JSONResponse(
            status_code=500,
            content={"status": "startup_failed", "error": startup_error}
        )
    from app.core.config import settings
    return {
        "status": "healthy",
        "supabase_configured": bool(settings.SUPABASE_URL),
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)
