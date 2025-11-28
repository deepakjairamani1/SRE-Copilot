from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.db import get_db
from app.models import Incident
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


class IncidentResponse(BaseModel):
    id: int
    incident_id: str
    service: str
    severity: str
    status: str
    title: str
    root_cause: Optional[str]
    confidence_score: Optional[float]
    detected_at: datetime
    resolved_at: Optional[datetime]
    duration_seconds: Optional[float]
    cost_usd: Optional[float]
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[IncidentResponse])
def list_incidents(
    service: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """List all incidents with optional filters"""
    query = db.query(Incident)
    
    if service:
        query = query.filter(Incident.service == service)
    if severity:
        query = query.filter(Incident.severity == severity)
    if status:
        query = query.filter(Incident.status == status)
    
    return query.order_by(Incident.detected_at.desc()).limit(limit).all()


@router.get("/stats/summary")
def get_stats(db: Session = Depends(get_db)):
    """Get incident statistics"""
    total = db.query(Incident).count()
    by_severity = db.query(Incident.severity, func.count(Incident.id)).group_by(Incident.severity).all()
    by_service = db.query(Incident.service, func.count(Incident.id)).group_by(Incident.service).all()
    
    return {
        "total_incidents": total,
        "by_severity": {sev: count for sev, count in by_severity},
        "by_service": {svc: count for svc, count in by_service}
    }


@router.get("/{incident_id}")
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    """Get incident details including full RCA report"""
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        return {"error": "Incident not found"}
    
    # Get observability data from rca_report if available
    rca_report = incident.rca_report_json or {}
    observability_data = rca_report.get("observability_data", {})
    
    # Extract similar incidents from semantic processing
    semantic_processing = incident.semantic_processing or {}
    similar_incidents = semantic_processing.get('similar_incidents', [])
    
    return {
        "incident_id": incident.incident_id,
        "service": incident.service,
        "severity": incident.severity,
        "status": incident.status,
        "title": incident.title,
        "root_cause": incident.root_cause,
        "confidence_score": incident.confidence_score,
        "detected_at": incident.detected_at,
        "resolved_at": incident.resolved_at,
        "duration_seconds": incident.duration_seconds,
        "cost_usd": incident.cost_usd,
        "rca_report": rca_report,
        "observability_data": observability_data,
        "similar_incidents": similar_incidents,
        "investigation_steps": incident.investigation_steps,
        "llm_provider": incident.llm_provider,
        "tokens_used": incident.tokens_used
    }
