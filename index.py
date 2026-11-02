import sys
import os
import traceback

curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

startup_error = None
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
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
except Exception as e:
    startup_error = traceback.format_exc()
    print("STARTUP ERROR:", startup_error)


@app.get("/")
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
