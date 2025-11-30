"""Orchestrator using LangGraph - Coordinates all agents in a workflow"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator
from .monitoring_agent import MonitoringAgent
from .diagnostic_agent import DiagnosticAgent


class AgentState(TypedDict):
    """State shared across all agents"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    incident_data: dict
    observability_data: dict
    rca_report: dict
    similar_incidents: list
    current_step: str
    investigation_steps: list


class OrchestratorGraph:
    """LangGraph-based orchestrator for multi-agent RCA workflow"""
    
    def __init__(self):
        self.monitoring_agent = MonitoringAgent()
        self.diagnostic_agent = DiagnosticAgent()
        
        # Build the graph
        self.workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        self.workflow.add_node("plan", self.plan_investigation)
        self.workflow.add_node("monitor", self.collect_observability_data)
        self.workflow.add_node("diagnose", self.perform_diagnosis)
        self.workflow.add_node("validate", self.validate_findings)
        self.workflow.add_node("adapt", self.adapt_strategy)
        
        # Define edges (workflow)
        self.workflow.set_entry_point("plan")
        self.workflow.add_edge("plan", "monitor")
        self.workflow.add_edge("monitor", "diagnose")
        self.workflow.add_edge("diagnose", "validate")
        
        # Conditional edge: validate -> adapt or END
        self.workflow.add_conditional_edges(
            "validate",
            self.should_adapt,
            {
                "adapt": "adapt",
                "end": END
            }
        )
        self.workflow.add_edge("adapt", "monitor")  # Retry with adapted strategy
        
        self.app = self.workflow.compile()
    
    def plan_investigation(self, state: AgentState) -> AgentState:
        """Plan the investigation strategy"""
        state["current_step"] = "plan"
        state["investigation_steps"].append({
            "step": "plan",
            "message": "📋 Planning investigation strategy...",
            "actions": [
                "Query Prometheus for metrics",
                "Query Loki for error logs",
                "Query Jaeger for slow traces",
                "Search similar past incidents"
            ]
        })
        return state
    
    def collect_observability_data(self, state: AgentState) -> AgentState:
        """Collect data using Monitoring Agent"""
        state["current_step"] = "monitor"
        state["investigation_steps"].append({
            "step": "act",
            "message": "🔍 Fetching observability data..."
        })
        
        # Use Monitoring Agent to collect data
        monitoring_result = self.monitoring_agent.collect_data(state["incident_data"])
        state["observability_data"] = monitoring_result["data_collected"]
        
        state["investigation_steps"].append({
            "step": "act",
            "message": "✓ Data fetching complete"
        })
        
        return state
    
    def perform_diagnosis(self, state: AgentState) -> AgentState:
        """Perform RCA using Diagnostic Agent"""
        state["current_step"] = "diagnose"
        state["investigation_steps"].append({
            "step": "act",
            "message": "🧠 Generating RCA with AI..."
        })
        
        # Use Diagnostic Agent for RCA
        diagnostic_result = self.diagnostic_agent.diagnose(state["observability_data"])
        state["rca_report"] = diagnostic_result["rca_report"]
        
        state["investigation_steps"].append({
            "step": "act",
            "message": "✓ RCA generation complete"
        })
        
        return state
    
    def validate_findings(self, state: AgentState) -> AgentState:
        """Validate the RCA findings"""
        state["current_step"] = "validate"
        state["investigation_steps"].append({
            "step": "check",
            "message": "✓ Validating RCA findings..."
        })
        
        # Check confidence score
        confidence = state["rca_report"].get("confidence_score", 0)
        
        if confidence >= 0.7:
            state["investigation_steps"].append({
                "step": "check",
                "message": f"✓ High confidence ({confidence:.0%})"
            })
        else:
            state["investigation_steps"].append({
                "step": "check",
                "message": f"⚠️  Low confidence ({confidence:.0%})"
            })
        
        return state
    
    def adapt_strategy(self, state: AgentState) -> AgentState:
        """Adapt investigation strategy if needed"""
        state["current_step"] = "adapt"
        state["investigation_steps"].append({
            "step": "adapt",
            "message": "🔄 Adapting strategy..."
        })
        return state
    
    def should_adapt(self, state: AgentState) -> str:
        """Decide whether to adapt or end"""
        confidence = state["rca_report"].get("confidence_score", 0)
        
        # If confidence is low and we haven't adapted yet, try adapting
        if confidence < 0.7 and len([s for s in state["investigation_steps"] if s["step"] == "adapt"]) == 0:
            return "adapt"
        
        return "end"
    
    def investigate(self, incident_data: dict) -> dict:
        """Run the full investigation workflow"""
        
        initial_state = {
            "messages": [],
            "incident_data": incident_data,
            "observability_data": {},
            "rca_report": {},
            "similar_incidents": [],
            "current_step": "",
            "investigation_steps": []
        }
        
        # Execute the graph
        final_state = self.app.invoke(initial_state)
        
        return {
            "incident_id": incident_data.get("incident_id"),
            "rca_report": final_state["rca_report"],
            "investigation_steps": final_state["investigation_steps"],
            "observability_data": final_state["observability_data"],
            "workflow": "langgraph",
            "agents_used": ["monitoring", "diagnostic", "orchestrator"]
        }