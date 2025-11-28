from google.adk.tools import FunctionTool, ToolContext
from google.adk.agents.callback_context import CallbackContext
from app.clients.loki_client import LokiClient
import logging
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)
loki_client = LokiClient(base_url="http://18.211.38.10:3100")
import json

async def loki_fetch_logs(tool_context: ToolContext, time_range: str = "5m", **kwargs):
    """
    Fetch logs from Loki and store summary in ToolContext state.
    """
    try:
        logger.info(f"Fetching logs for last {time_range}")
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
        logger.info("Fetching error logs")
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
        logger.info(f"Fetching logs for trace: {trace_id}")
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


loki_fetch_logs_tool = FunctionTool(
    name="loki_fetch_logs",
    description="Fetch Loki logs for a given time range. time_range='5m' by default.",
    input_schema={
        "type": "object",
        "properties": {
            "time_range": {"type": "string"}
        },
        "required": []
    },
    func=loki_fetch_logs
)

loki_fetch_error_logs_tool = FunctionTool(
    name="loki_fetch_error_logs",
    description="Fetch only ERROR/CRITICAL logs from Loki.",
    input_schema={"type": "object", "properties": {}},
    func=loki_fetch_error_logs
)

loki_fetch_by_trace_tool = FunctionTool(
    name="loki_fetch_by_trace",
    description="Fetch logs based on trace_id.",
    input_schema={
        "type": "object",
        "properties": {
            "trace_id": {"type": "string"}
        },
        "required": ["trace_id"]
    },
    func=loki_fetch_by_trace
)

loki_tools = [
    loki_fetch_logs_tool,
    loki_fetch_error_logs_tool,
    loki_fetch_by_trace_tool
]

