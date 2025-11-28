from google.genai.tools import tool
from app.clients.loki_client import LokiClient
from google.genai.agents import ToolContext

loki_client = LokiClient(base_url="http://loki:3100")
import json

@tool
async def loki_query_logs(time_range: str = "5m") -> str:
    """
    Fetch logs from Loki within a time range.
    Returns a concise summary instead of raw logs.
    """
    result = await loki_client.query_logs(time_range=time_range)

    # Sanitize large logs and never return raw content to the LLM
    summary = {
        "error_count": result["log_summary"]["error_count"],
        "critical_count": result["log_summary"]["critical_count"],
        "warning_count": result["log_summary"]["warning_count"],
        "total_logs": result["log_summary"]["total_logs"],
        "patterns": result["patterns"],
    }
    return json.dumps(summary)


@tool
async def loki_query_errors() -> str:
    """
    Fetch ERROR and CRITICAL logs only.
    Returns a cleaned summary.
    """
    result = await loki_client.query_error_logs_only()

    summary = {
        "total_errors": result.get("total_errors", 0),
        "error_logs_count": len(result.get("error_logs", [])),
        "critical_logs_count": len(result.get("critical_logs", [])),
    }
    return json.dumps(summary)

@tool
async def loki_logs_by_trace(trace_id: str) -> str:
    """
    Fetch logs correlated to a specific trace ID.
    Returns a summarized response.
    """
    result = await loki_client.query_by_trace_id(trace_id)
    return json.dumps({"log_count": len(result), "logs": result[:5]})




tool_context = ToolContext(
    tools=[
        loki_query_logs,
        loki_query_errors,
        loki_logs_by_trace
    ]
)