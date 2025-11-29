import logging
import sys
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .context import get_context
from .routers import incidents, analytics, rca, observability, vector_db
import os

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
    
    # Auto-start investigation if enabled
    auto_inv_enabled = os.getenv("AUTO_INVESTIGATION_ENABLED", "false").lower()
    logger.info(f"AUTO_INVESTIGATION_ENABLED={auto_inv_enabled}")
    
    if auto_inv_enabled == "true":
        from app.services.auto_investigator import AutoInvestigator
        from app.routers import auto_investigation
        import asyncio
        
        slack_webhook = os.getenv("SLACK_WEBHOOK_URL", "")
        check_interval = int(os.getenv("AUTO_INVESTIGATION_CHECK_INTERVAL", "10"))
        cpu_threshold = float(os.getenv("AUTO_INVESTIGATION_CPU_THRESHOLD", "90.0"))
        ram_threshold = float(os.getenv("AUTO_INVESTIGATION_RAM_THRESHOLD", "90.0"))
        consecutive_errors = int(os.getenv("AUTO_INVESTIGATION_CONSECUTIVE_ERRORS", "3"))
        
        auto_inv = AutoInvestigator(slack_webhook_url=slack_webhook)
        auto_inv.check_interval = check_interval
        auto_inv.monitor.cpu_threshold = cpu_threshold
        auto_inv.monitor.ram_threshold = ram_threshold
        auto_inv.monitor.consecutive_errors_threshold = consecutive_errors
        
        # Store globally so API can access it
        auto_investigation.auto_investigator = auto_inv
        
        asyncio.create_task(auto_inv.start_monitoring())
        logger.info(f"✅ Auto-investigation started (interval: {check_interval}s, CPU: {cpu_threshold}%, RAM: {ram_threshold}%, Slack: {bool(slack_webhook)})")


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
from .routers import auto_investigation
app.include_router(incidents.router)
app.include_router(analytics.router)
app.include_router(rca.router)
app.include_router(observability.router)
app.include_router(vector_db.router)
app.include_router(auto_investigation.router)