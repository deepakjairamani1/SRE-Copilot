from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/rca", tags=["rca"])


class InvestigateRequest(BaseModel):
    service: str
    detected_at: Optional[str] = None


@router.post("/investigate")
async def trigger_investigation(request: InvestigateRequest, background_tasks: BackgroundTasks):
    """Trigger RCA investigation"""
    from app.agents.rca_agent import RCAAgent
    from app.clients.prometheus_client import PrometheusClient
    from app.clients.loki_client import LokiClient
    from app.clients.jaeger_client import JaegerClient
    import uuid
    
    incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
    incident_data = {
        "service": request.service,
        "detected_at": request.detected_at or datetime.utcnow().isoformat()
    }
    
    from app.context import get_context
    ctx = get_context()
    
    agent = RCAAgent()
    agent.prometheus_client = PrometheusClient(ctx.PROMETHEUS_URL)
    agent.loki_client = LokiClient(ctx.LOKI_URL)
    agent.jaeger_client = JaegerClient(ctx.JAEGER_QUERY_URL)
    
    result = await agent.investigate(incident_id, incident_data)
    
    return {
        "incident_id": incident_id,
        "status": "completed" if "error" not in result else "failed",
        "result": result
    }


@router.get("/status/{incident_id}")
def get_investigation_status(incident_id: str):
    """Get investigation status"""
    from app.db import SessionLocal
    from app.models import Incident
    
    db = SessionLocal()
    try:
        incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
        if not incident:
            return {"status": "not_found"}
        
        return {
            "incident_id": incident_id,
            "status": incident.status,
            "progress": 100 if incident.status != "open" else 50
        }
    finally:
        db.close()
