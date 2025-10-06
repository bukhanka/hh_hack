"""FastAPI backend for the News Intelligence Platform - modular structure."""

import asyncio
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from database import db_manager
from background_worker import background_worker

# Import all routers
from api.routes import (
    health_router,
    financial_router,
    personal_router,
    feed_router,
    onboarding_router,
    learning_router,
    admin_router
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="News Intelligence Platform",
    description="Dual-mode news aggregation system: Financial RADAR & Personal News Aggregator",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(health_router)
app.include_router(financial_router)
app.include_router(personal_router)
app.include_router(feed_router)
app.include_router(onboarding_router)
app.include_router(learning_router)
app.include_router(admin_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database and start background worker on startup."""
    logger.info("Initializing database...")
    try:
        await db_manager.init_async()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Don't fail startup, just log the error
    
    # Start background worker for automated tasks
    try:
        background_worker.start()
        logger.info("Background worker started successfully")
    except Exception as e:
        logger.error(f"Failed to start background worker: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background worker on shutdown."""
    try:
        background_worker.stop()
        logger.info("Background worker stopped")
    except Exception as e:
        logger.error(f"Error stopping background worker: {e}")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page."""
    template_path = Path(__file__).parent / "templates" / "index.html"
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    import uvicorn
    
    # When running from backend directory: python -m api
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

