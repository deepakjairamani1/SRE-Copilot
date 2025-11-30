"""Monitoring Agent - Collects observability data from Prometheus, Loki, Jaeger"""

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_aws import ChatBedrock
from .tools import PrometheusQueryTool, LokiQueryTool, JaegerQueryTool
from typing import Dict, Any
import json


class MonitoringAgent:
    """Agent responsible for collecting observability data"""
    
    def __init__(self):
        self.llm = ChatBedrock(
            model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            region_name="us-east-1"
        )
        
        self.tools = [
            PrometheusQueryTool(),
            LokiQueryTool(),
            JaegerQueryTool()
        ]
        
        self.prompt = PromptTemplate.from_template("""
You are a Monitoring Agent responsible for collecting observability data.

Your task: Collect metrics, logs, and traces for the incident.

Available tools:
{tools}

Tool names: {tool_names}

Incident Details:
Service: {service}
Detected At: {detected_at}
Severity: {severity}

Instructions:
1. Query Prometheus for metrics (CPU, memory, HTTP errors, latency)
2. Query Loki for error logs and patterns
3. Query Jaeger for slow traces and bottlenecks
4. Summarize findings

{agent_scratchpad}

Begin!
""")
        
        self.agent = create_react_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    def collect_data(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect observability data for incident"""
        
        result = self.agent_executor.invoke({
            "service": incident_data.get("service", "unknown"),
            "detected_at": incident_data.get("detected_at", ""),
            "severity": incident_data.get("severity", "high")
        })
        
        return {
            "agent": "monitoring",
            "status": "completed",
            "data_collected": {
                "prometheus": "metrics collected",
                "loki": "logs collected",
                "jaeger": "traces collected"
            },
            "output": result.get("output", "")
        }