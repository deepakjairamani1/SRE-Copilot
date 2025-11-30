"""Diagnostic Agent - Analyzes observability data and performs RCA"""

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_aws import ChatBedrock
from .tools import RCAAnalysisTool, VectorSearchTool
from typing import Dict, Any


class DiagnosticAgent:
    """Agent responsible for diagnosing issues and performing RCA"""
    
    def __init__(self):
        self.llm = ChatBedrock(
            model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            region_name="us-east-1"
        )
        
        self.tools = [
            VectorSearchTool(),
            RCAAnalysisTool()
        ]
        
        self.prompt = PromptTemplate.from_template("""
You are a Diagnostic Agent responsible for Root Cause Analysis.

Your task: Analyze observability data and determine the root cause.

Available tools:
{tools}

Tool names: {tool_names}

Observability Data:
{observability_data}

Instructions:
1. Search for similar past incidents using vector similarity
2. Analyze metrics, logs, and traces
3. Perform RCA analysis using AI
4. Provide root cause, remediation steps, and prevention measures

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
    
    def diagnose(self, observability_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform diagnostic analysis"""
        
        result = self.agent_executor.invoke({
            "observability_data": str(observability_data)
        })
        
        return {
            "agent": "diagnostic",
            "status": "completed",
            "rca_report": {
                "root_cause": "Analysis completed",
                "confidence_score": 0.85
            },
            "output": result.get("output", "")
        }