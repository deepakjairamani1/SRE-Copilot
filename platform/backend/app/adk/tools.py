from google.adk.tools import Tool, ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.types import Part, Content
from .loki_client import LokiClient  # your async Loki client

loki_client = LokiClient(base_url="http://loki:3100")
import json

async def loki_fetch_logs(tool_context: ToolContext, time_range: str = "5m", **kwargs):
    """
    Fetch logs from Loki and store summary in ToolContext state.
    """
    try:
        results = await loki_client.query_logs(time_range=time_range)

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

        return {
            "status": "ok",
            "message": f"Fetched logs for last {time_range}"
        }

    except Exception as e:
        return {"error": f"Loki fetch failed: {str(e)}"}

async def loki_fetch_error_logs(tool_context: ToolContext, **_):
    """
    Fetch only ERROR and CRITICAL logs.
    """
    try:
        results = await loki_client.query_error_logs_only()

        summary = {
            "total_errors": results.get("total_errors", 0),
            "error_logs": len(results.get("error_logs", [])),
            "critical_logs": len(results.get("critical_logs", []))
        }

        # Store in state
        tool_context.state["temp:loki_errors"] = summary

        return {
            "status": "ok",
            "message": "Fetched error logs"
        }

    except Exception as e:
        return {"error": f"Loki error fetch failed: {str(e)}"}

async def loki_fetch_by_trace(tool_context: ToolContext, trace_id: str, **kwargs):
    """
    Fetch all logs for a given Trace ID and store them in state.
    """
    try:
        logs = await loki_client.query_by_trace_id(trace_id)

        tool_context.state["temp:loki_trace"] = {
            "trace_id": trace_id,
            "count": len(logs)
        }

        return {
            "status": "ok",
            "message": f"Fetched logs for trace: {trace_id}"
        }

    except Exception as e:
        return {"error": f"Loki trace fetch failed: {str(e)}"}


loki_tools = [
    Tool(name="loki_fetch_logs", code=loki_fetch_logs),
    Tool(name="loki_fetch_error_logs", code=loki_fetch_error_logs),
    Tool(name="loki_fetch_by_trace", code=loki_fetch_by_trace),
]



def loki_callback(callback_context: CallbackContext, **kwargs):
    last_summary = callback_context.state.get("temp:loki_summary")
    last_errors = callback_context.state.get("temp:loki_errors")
    last_trace = callback_context.state.get("temp:loki_trace")

    if last_summary:
        print("[Callback] Last summary:", last_summary)

    if last_errors:
        print("[Callback] Last errors:", last_errors)

    if last_trace:
        print("[Callback] Last trace info:", last_trace)

    return None
