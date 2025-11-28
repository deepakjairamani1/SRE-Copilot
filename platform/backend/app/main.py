import logging
import sys
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .context import get_context
from .routers import chatbot, incidents, observability

# Create logs directory
Path('logs').mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/sre_copilot.log', mode='a')
    ]
)

# Set specific loggers
logging.getLogger('app.agents.rca_agent').setLevel(logging.DEBUG)
logging.getLogger('app.clients').setLevel(logging.DEBUG)
logging.getLogger('uvicorn.access').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SRE Copilot API",
    description="Backend API for SRE Copilot Platform",
    version="1.0.0"
)

# CORS middleware - allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Startup event - load configuration and print debug info"""
    ctx = get_context()
    logger.info("🚀 SRE Copilot API starting up...")
    logger.info("📋 Configuration loaded:")
    debug_info = ctx.debug_info()
    for key, value in debug_info["config"].items():
        logger.info(f"   {key}: {value}")
    
    logger.info("Logging configured: INFO level to stdout and logs/sre_copilot.log")
    logger.info("Debug logging enabled for RCA agent and clients")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "ok",
        "service": "sre-copilot-api"
    }


# Debug configuration endpoint
@app.get("/debug/config")
async def debug_config():
    """Debug endpoint to view current configuration"""
    ctx = get_context()
    return ctx.debug_info()

# Include routers
app.include_router(chatbot.router)
app.include_router(incidents.router)
app.include_router(observability.router)