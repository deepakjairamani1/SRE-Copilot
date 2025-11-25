from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.db import Base


class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, unique=True, index=True, nullable=False)
    
    # Basic info
    service = Column(String, index=True, nullable=False)
    severity = Column(String, index=True)
    status = Column(String, index=True, default="open")
    
    # Timestamps
    detected_at = Column(DateTime, index=True, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # RCA fields
    title = Column(String, nullable=False)
    root_cause = Column(Text)
    confidence_score = Column(Float)
    
    # Impact
    user_impact = Column(Text)
    users_affected = Column(String)
    
    # Resolution
    fix_applied = Column(Text)
    resolution_time_seconds = Column(Float)
    
    # Metrics
    duration_seconds = Column(Float)
    cost_usd = Column(Float)
    
    # Full RCA report (JSON)
    rca_report_json = Column(JSON)
    
    # Investigation metadata
    investigation_steps = Column(JSON)
    llm_provider = Column(String)
    tokens_used = Column(Integer)


class IncidentMetric(Base):
    __tablename__ = "incident_metrics"
    
    id = Column(Integer, primary_key=True)
    incident_id = Column(String, index=True, nullable=False)
    
    # Metric snapshot
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_io = Column(Float)
    network_io = Column(Float)
    http_error_rate = Column(Float)
    http_latency_p95 = Column(Float)
    http_latency_p99 = Column(Float)
    
    created_at = Column(DateTime, server_default=func.now())
