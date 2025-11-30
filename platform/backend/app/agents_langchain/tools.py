"""LangChain Tools for SRE Copilot Agents"""

from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field
import json


class PrometheusQueryInput(BaseModel):
    """Input for Prometheus query tool"""
    time_range: str = Field(default="5m", description="Time range for metrics query")

class PrometheusQueryTool(BaseTool):
    """Tool for querying Prometheus metrics"""
    
    name: str = "query_prometheus_metrics"
    description: str = "Query Prometheus for system and application metrics including CPU, memory, HTTP error rates, latency"
    args_schema: Type[BaseModel] = PrometheusQueryInput
    
    def _run(self, time_range: str = "5m") -> str:
        """Execute Prometheus query"""
        return json.dumps({"tool": "prometheus", "time_range": time_range, "status": "success"})


class LokiQueryTool(BaseTool):
    """Tool for querying Loki logs"""
    
    name: str = "query_loki_logs"
    description: str = "Query Loki for application logs including errors, warnings, and patterns"
    
    def _run(self, time_range: str = "5m") -> str:
        """Execute Loki query"""
        return json.dumps({"tool": "loki", "time_range": time_range, "status": "success"})


class JaegerQueryTool(BaseTool):
    """Tool for querying Jaeger traces"""
    
    name: str = "query_jaeger_traces"
    description: str = "Query Jaeger for distributed traces, slow traces, and latency analysis"
    
    def _run(self, time_range: str = "5m") -> str:
        """Execute Jaeger query"""
        return json.dumps({"tool": "jaeger", "time_range": time_range, "status": "success"})


class VectorSearchTool(BaseTool):
    """Tool for semantic similarity search"""
    
    name: str = "search_similar_incidents"
    description: str = "Search for similar past incidents using semantic vector similarity with Bedrock Titan embeddings"
    
    def _run(self, incident_description: str) -> str:
        """Execute vector search"""
        return json.dumps({"tool": "vector_search", "query": incident_description, "status": "success"})


class RCAAnalysisTool(BaseTool):
    """Tool for RCA analysis"""
    
    name: str = "perform_rca_analysis"
    description: str = "Perform Root Cause Analysis using AI on collected observability data"
    
    def _run(self, data: str) -> str:
        """Execute RCA analysis"""
        return json.dumps({"tool": "rca_analysis", "status": "success"})


def get_all_tools():
    """Get all available tools"""
    return [
        PrometheusQueryTool(),
        LokiQueryTool(),
        JaegerQueryTool(),
        VectorSearchTool(),
        RCAAnalysisTool()
    ]