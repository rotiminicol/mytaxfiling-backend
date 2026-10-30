from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.security import verify_jwt_token
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting MyTaxFiling Backend API...")
    yield
    # Shutdown
    print("Shutting down MyTaxFiling Backend API...")


app = FastAPI(
    title="MyTaxFiling API",
    description="Backend API for MyTaxFiling - Tax Management and Compliance Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

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


@app.get("/")
async def root():
    return {
        "message": "MyTaxFiling API",
        "version": "1.0.0",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Vercel serverless handler
from mangum import Mangum

handler = Mangum(app)
