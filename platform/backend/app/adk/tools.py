from google.adk.tools import FunctionTool, ToolContext
from google.adk.agents.callback_context import CallbackContext
from app.clients.loki_client import LokiClient
import logging
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)
loki_client = LokiClient(base_url="http://18.211.38.10:3100")
import json


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

async def loki_fetch_error_logs(tool_context: ToolContext, **_):
    """
    Fetch only ERROR and CRITICAL logs.
    """
    try:
        logger.info("Fetching error logs")
        results = await loki_client.query_error_logs_only()
        logs = results.get("logs", [])
        summary = {
            "total_errors": results.get("total_errors", 0),
            "error_logs": results.get("error_logs", []),
            "critical_logs": results.get("critical_logs", [])
        }
        logger.info(f"Error logs: {logs}")
        logger.info(f"Error summary: {summary}")

        # Store in state
        tool_context.state["temp:loki_errors"] = summary

        return {
            "status": "ok",
            "message": "Fetched error logs",
            "logs": logs[:200],
            "summary": summary
        }

    except Exception as e:
        return {"error": f"Loki error fetch failed: {str(e)}"}

async def loki_fetch_by_trace(tool_context: ToolContext, trace_id: str, **kwargs):
    """
    Fetch all logs for a given Trace ID and store them in state.
    """
    try:
        logger.info(f"Fetching logs for trace: {trace_id}")
        logs = await loki_client.query_by_trace_id(trace_id)

        tool_context.state["temp:loki_trace"] = {
            "trace_id": trace_id,
            "count": len(logs)
        }

        return {
            "status": "ok",
            "message": f"Fetched logs for trace: {trace_id}",
            "logs": logs[:200]        }

    except Exception as e:
        return {"error": f"Loki trace fetch failed: {str(e)}"}


loki_fetch_logs_tool = FunctionTool(
    func=loki_fetch_logs
)

loki_fetch_error_logs_tool = FunctionTool(
    func=loki_fetch_error_logs
)

loki_fetch_by_trace_tool = FunctionTool(
    func=loki_fetch_by_trace
)

loki_tools = [
    loki_fetch_logs_tool,
    # loki_fetch_error_logs_tool,
    # loki_fetch_by_trace_tool
]

