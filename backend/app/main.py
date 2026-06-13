"""FastAPI application entrypoint.

Configures CORS, mounts routes, and sets up logging.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings

# Configure logging.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="DSA Learning Guide Generator",
    description="Multi-agentic DSA study guide generator powered by Google Antigravity SDK",
    version="0.1.0",
)

# CORS — allow the frontend dev server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes.
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint redirect hint."""
    return {
        "message": "DSA Learning Guide Generator API",
        "docs": "/docs",
        "health": "/api/health",
    }
