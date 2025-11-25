from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from datetime import datetime, timedelta
from app.db import get_db
from app.models import Incident

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/trends/incidents")
def incident_trends(
    days: int = Query(7, le=90),
    service: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Incident trends over time"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(
        func.date(Incident.detected_at).label('date'),
        func.count(Incident.id).label('count')
    ).filter(Incident.detected_at >= start_date)
    
    if service:
        query = query.filter(Incident.service == service)
    
    results = query.group_by(func.date(Incident.detected_at)).all()
    
    return {
        "period_days": days,
        "service": service,
        "data": [{"date": str(r.date), "count": r.count} for r in results]
    }


@router.get("/trends/mttr")
def mttr_trends(
    days: int = Query(30, le=90),
    db: Session = Depends(get_db)
):
    """Mean Time To Resolution trends"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(
        func.date(Incident.detected_at).label('date'),
        func.avg(Incident.resolution_time_seconds).label('avg_mttr')
    ).filter(
        and_(
            Incident.detected_at >= start_date,
            Incident.resolution_time_seconds.isnot(None)
        )
    )
    
    results = query.group_by(func.date(Incident.detected_at)).all()
    
    return {
        "period_days": days,
        "data": [{"date": str(r.date), "avg_mttr_seconds": r.avg_mttr} for r in results]
    }


@router.get("/top-issues")
def top_issues(
    days: int = Query(30, le=90),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Most frequent root causes"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        Incident.root_cause,
        func.count(Incident.id).label('count')
    ).filter(
        and_(
            Incident.detected_at >= start_date,
            Incident.root_cause.isnot(None)
        )
    ).group_by(Incident.root_cause).order_by(func.count(Incident.id).desc()).limit(limit).all()
    
    return {
        "period_days": days,
        "top_issues": [{"root_cause": r.root_cause, "count": r.count} for r in results]
    }


@router.get("/service-health")
def service_health(db: Session = Depends(get_db)):
    """Current health status by service"""
    results = db.query(
        Incident.service,
        func.count(Incident.id).label('total'),
        func.sum(func.case((Incident.severity == 'critical', 1), else_=0)).label('critical'),
        func.sum(func.case((Incident.status == 'open', 1), else_=0)).label('open')
    ).group_by(Incident.service).all()
    
    return {
        "services": [
            {
                "service": r.service,
                "total_incidents": r.total,
                "critical_count": r.critical,
                "open_count": r.open,
                "health": "critical" if r.critical > 0 else "degraded" if r.open > 0 else "healthy"
            }
            for r in results
        ]
    }


@router.get("/confidence-analysis")
def confidence_analysis(db: Session = Depends(get_db)):
    """RCA confidence score analysis"""
    results = db.query(
        func.avg(Incident.confidence_score).label('avg_confidence'),
        func.min(Incident.confidence_score).label('min_confidence'),
        func.max(Incident.confidence_score).label('max_confidence'),
        func.count(Incident.id).label('total')
    ).filter(Incident.confidence_score.isnot(None)).first()
    
    return {
        "avg_confidence": results.avg_confidence,
        "min_confidence": results.min_confidence,
        "max_confidence": results.max_confidence,
        "total_analyzed": results.total
    }
