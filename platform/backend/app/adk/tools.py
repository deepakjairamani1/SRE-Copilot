from google.adk.tools import FunctionTool, ToolContext
from google.adk.agents.callback_context import CallbackContext
from app.clients.loki_client import LokiClient
from app.clients.jaeger_client import JaegerClient
from app.clients.prometheus_client import PrometheusClient
import logging
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)
loki_client = LokiClient(base_url="http://18.211.38.10:3100")
jaeger_client = JaegerClient(base_url="http://18.211.38.10:16686")
prometheus_client = PrometheusClient(base_url="http://18.211.38.10:9090")


def duration_to_minutes(value: str) -> float:
    """
    Convert a duration string like '24h', '2d', '30m', '45s' into minutes.
    """
    value = value.strip().lower()
    
    # Extract numeric part and unit
    num = ""
    unit = ""
    
    for ch in value:
        if ch.isdigit() or ch == '.':
            num += ch
        else:
            unit += ch

    if not num or not unit:
        raise ValueError("Invalid duration format")

    num = float(num)

    if unit == "d":
        num= num * 24 * 60
    elif unit == "h":
        num= num * 60
    elif unit == "m":
        num= num
    elif unit == "s":
        num= num / 60
    else:
        raise ValueError(f"Unknown unit: {unit}")

    return str(int(num))+'m'


async def prometheus_fetch_metrics(tool_context: ToolContext, time_range: str = "5m", **kwargs):
    """
    Fetch metrics from Prometheus and store summary in ToolContext state.
    """
    try:
        logger.info(f"Fetching metrics for last {time_range}")
        time_range = duration_to_minutes(time_range)

        results = await prometheus_client.get_critical_metrics()
        logger.info(('prom results', results))
        metrics = results.get("host_metrics", {})
        otlp_metrics = results.get("otlp_metrics", {})

        # Extract summary
        summary = {
            "overall_health": results.get("overall_health", "unknown"),
            "host_metrics_count": metrics,
            "otlp_metrics_count": len(otlp_metrics),
            "critical_count": sum(1 for m in {**metrics, **otlp_metrics}.values() if m.get("status") == "critical"),
            "warning_count": sum(1 for m in {**metrics, **otlp_metrics}.values() if m.get("status") == "warning")
        }
        logger.info(('prom summary', summary))
        # Save summary in state for next tool
        tool_context.state["temp:prometheus_summary"] = summary
        tool_context.state["temp:last_prometheus_query"] = time_range
        logger.info(f"Summary: {summary}")
        tool_context.state["flow.prometheus_fetch_metrics_done"] = True
        return summary

    except Exception as e:
        logger.error(f"Prometheus fetch failed: {str(e)}")
        return {"error": f"Prometheus fetch failed: {str(e)}"}


async def jaeger_fetch_traces(tool_context: ToolContext, time_range: str = "5m", **kwargs):
    """
    Fetch traces from Jaeger and store summary in ToolContext state.
    """
    try:
        logger.info(f"Fetching traces for last {time_range}")
        time_range = duration_to_minutes(time_range)

        results = await jaeger_client.query_traces(time_range=time_range)
        
        traces = results.get("traces", {})

        # Extract summary
        summary = {
            "total": results["trace_summary"]["total_traces"],
            "errors": results["trace_summary"]["error_trace_count"],
            "slow_traces": results["trace_summary"]["slow_trace_count"],
            "p95_latency": results["trace_summary"]["p95_latency_ms"],
            "patterns": results["patterns"]
        }

        # Save summary in state for next tool
        tool_context.state["temp:jaeger_summary"] = summary
        tool_context.state["temp:last_jaeger_query"] = time_range
        logger.info(f"Summary: {summary}")
        tool_context.state["flow.jaeger_fetch_traces_done"] = True
        return results

    except Exception as e:
        return {"error": f"Jaeger fetch failed: {str(e)}"}


async def loki_fetch_logs(tool_context: ToolContext, time_range: str = "5m", **kwargs):
    """
    Fetch logs from Loki and store summary in ToolContext state.
    """
    try:
        logger.info(f"Fetching logs for last {time_range}")
        time_range = duration_to_minutes(time_range)

        results = await loki_client.query_logs(time_range=time_range)
        
        logs = results.get("logs", [])  # <-- ensure logs returned


        # Extract summary
        summary = {
            "total": results["log_summary"]["total_logs"],
            "errors": results["log_summary"]["error_count"],
            "critical": results["log_summary"]["critical_count"],
            "warnings": results["log_summary"]["warning_count"],
            "patterns": results["patterns"]
        }

        # Save summary in state for next tool
        tool_context.state["temp:loki_summary"] = summary
        tool_context.state["temp:last_loki_query"] = time_range
        logger.info(f"Summary: {summary}")
        logger.info(f"Patterns: {logs}")
        tool_context.state["flow.loki_fetch_logs_done"] = True
        return logs

    except Exception as e:
        return {"error": f"Loki fetch failed: {str(e)}"}



loki_fetch_logs_tool = FunctionTool(
    func=loki_fetch_logs
)

prometheus_fetch_metrics_tool = FunctionTool(
    func=prometheus_fetch_metrics
)

jaeger_fetch_traces_tool = FunctionTool(
    func=jaeger_fetch_traces
)

tools = [
    loki_fetch_logs_tool,
    prometheus_fetch_metrics_tool,
    jaeger_fetch_traces_tool
]
