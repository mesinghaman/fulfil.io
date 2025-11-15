"""
Main FastAPI application entry point.

This module creates and configures the FastAPI application with all routes,
middleware, and dependencies.
"""

import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import products_router, webhooks_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Product Importer",
    description="A scalable web application for importing products from CSV files",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(products_router, tags=["products"])
app.include_router(webhooks_router, tags=["webhooks"])


@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    logger.info("Product Importer application starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    logger.info("Product Importer application shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
