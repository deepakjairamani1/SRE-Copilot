from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/api/observability", tags=["observability"])


@router.get("/metrics/current")
async def get_current_metrics(service: Optional[str] = None):
    """Get current metrics from Prometheus"""
    from app.clients.prometheus_client import PrometheusClient
    from app.context import get_context
    
    ctx = get_context()
    client = PrometheusClient(ctx.PROMETHEUS_URL)
    metrics = await client.get_critical_metrics()
    
    return {
        "service": service or "all",
        "metrics": metrics,
        "timestamp": metrics.get("query_timestamp")
    }


@router.get("/logs/recent")
async def get_recent_logs(service: Optional[str] = None, time_range: str = "5m"):
    """Get recent logs from Loki"""
    from app.clients.loki_client import LokiClient
    from app.context import get_context
    
    ctx = get_context()
    client = LokiClient(ctx.LOKI_URL)
    logs = await client.query_logs(time_range=time_range)
    
    return {
        "service": service or "all",
        "time_range": time_range,
        "logs": logs
    }


@router.get("/traces/recent")
async def get_recent_traces(service: Optional[str] = None, time_range: str = "5m"):
    """Get recent traces from Jaeger"""
    from app.clients.jaeger_client import JaegerClient
    from app.context import get_context
    
    ctx = get_context()
    client = JaegerClient(ctx.JAEGER_QUERY_URL)
    traces = await client.query_traces(time_range=time_range)
    
    return {
        "service": service or "all",
        "time_range": time_range,
        "traces": traces
    }


@router.get("/health-check")
async def observability_health():
    """Check health of observability stack"""
    from app.clients.prometheus_client import PrometheusClient
    from app.clients.loki_client import LokiClient
    from app.clients.jaeger_client import JaegerClient
    from app.context import get_context
    
    ctx = get_context()
    prom = PrometheusClient(ctx.PROMETHEUS_URL)
    loki = LokiClient(ctx.LOKI_URL)
    jaeger = JaegerClient(ctx.JAEGER_QUERY_URL)
    
    prom_data = await prom.get_critical_metrics()
    loki_data = await loki.query_logs(time_range="1m")
    jaeger_data = await jaeger.query_traces(time_range="1m")
    
    return {
        "prometheus": "healthy" if "error" not in prom_data else "unhealthy",
        "loki": "healthy" if "error" not in loki_data else "unhealthy",
        "jaeger": "healthy" if "error" not in jaeger_data else "unhealthy"
    }
