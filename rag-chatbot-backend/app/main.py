"""
FastAPI application entry point.
Configures CORS, middleware, routes, and lifecycle events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import db_pool
from app.qdrant_client import qdrant_client
from app.gemini_client import gemini_client
from app.middleware.logging import RequestTracingMiddleware, log_info, log_error
from app.api import health, chat, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for startup and shutdown events.
    
    Startup:
    - Connect to PostgreSQL database
    - Initialize Qdrant client
    - Initialize Gemini client
    
    Shutdown:
    - Close database connections
    - Close Qdrant client
    - Cleanup Gemini client
    """
    # Startup
    log_info("application_startup_started")
    
    try:
        # Connect to database
        log_info("connecting_to_database")
        await db_pool.connect()
        log_info("database_connected")
        
        # Initialize Qdrant client
        log_info("initializing_qdrant_client")
        await qdrant_client.connect()
        log_info("qdrant_client_initialized")
        
        # Initialize Gemini client
        log_info("initializing_gemini_client")
        gemini_client.connect()
        log_info("gemini_client_initialized")
        
        log_info("application_startup_completed")
        
    except Exception as e:
        log_error("application_startup_failed", error=str(e))
        raise
    
    yield
    
    # Shutdown
    log_info("application_shutdown_started")
    
    try:
        # Disconnect from database
        log_info("disconnecting_from_database")
        await db_pool.disconnect()
        log_info("database_disconnected")
        
        # Close Qdrant client
        log_info("closing_qdrant_client")
        await qdrant_client.disconnect()
        log_info("qdrant_client_closed")
        
        # Cleanup Gemini client
        log_info("cleaning_up_gemini_client")
        gemini_client.disconnect()
        log_info("gemini_client_cleaned_up")
        
        log_info("application_shutdown_completed")
        
    except Exception as e:
        log_error("application_shutdown_failed", error=str(e))


# Create FastAPI application
app = FastAPI(
    title="RAG Chatbot API",
    description="RAG chatbot backend for Physical AI textbook",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request tracing middleware
app.add_middleware(RequestTracingMiddleware)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(auth.router, tags=["auth"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "RAG Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }
