import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from app.services.monitor import SystemMonitor
from app.services.slack_notifier import SlackNotifier
from app.agents.rca_agent import RCAAgent
from app.clients.prometheus_client import PrometheusClient
from app.clients.loki_client import LokiClient
from app.clients.jaeger_client import JaegerClient

logger = logging.getLogger(__name__)


class AutoInvestigator:
    """Automatic investigation trigger based on metrics and logs"""
    
    def __init__(self, slack_webhook_url: str = None):
        from app.context import get_context
        ctx = get_context()
        
        self.prometheus_client = PrometheusClient(ctx.PROMETHEUS_URL)
        self.loki_client = LokiClient(ctx.LOKI_URL)
        self.jaeger_client = JaegerClient(ctx.JAEGER_QUERY_URL)
        
        self.monitor = SystemMonitor(self.prometheus_client, self.loki_client)
        self.slack_notifier = SlackNotifier(slack_webhook_url or "")
        self.rca_agent = RCAAgent()
        
        self.running = False
        self.check_interval = 10  # seconds
        self.investigation_in_progress = False
    
    async def start_monitoring(self):
        """Start continuous monitoring loop"""
        self.running = True
        logger.info("🔍 Auto-investigation monitoring started")
        
        while self.running:
            try:
                await self._check_and_investigate()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop monitoring loop"""
        self.running = False
        logger.info("Auto-investigation monitoring stopped")
    
    async def _check_and_investigate(self):
        """Check triggers and start investigation if needed"""
        if self.investigation_in_progress:
            logger.debug("Investigation already in progress, skipping check")
            return
        
        trigger_status = await self.monitor.evaluate_triggers()
        
        if not trigger_status.get('should_investigate'):
            return
        
        logger.info("🚨 Investigation trigger detected!")
        logger.info(f"Metrics: {trigger_status.get('metrics')}")
        logger.info(f"Logs: {trigger_status.get('logs')}")
        
        self.investigation_in_progress = True
        
        try:
            await self._run_investigation(trigger_status)
        finally:
            self.investigation_in_progress = False
    
    async def _run_investigation(self, trigger_status: Dict[str, Any]):
        """Run RCA investigation and send to Slack if severity > 0.6"""
        import uuid
        
        incident_id = f"AUTO-{uuid.uuid4().hex[:8].upper()}"
        
        incident_data = {
            "service": "core-athenamind",
            "detected_at": datetime.utcnow().isoformat(),
            "trigger_reason": self._format_trigger_reason(trigger_status)
        }
        
        logger.info(f"[{incident_id}] Starting automatic investigation...")
        
        result = await self.rca_agent.investigate(incident_id, incident_data)
        
        if "error" in result:
            logger.error(f"[{incident_id}] Investigation failed: {result['error']}")
            return
        
        rca_report = result.get('rca_report', {})
        severity_score = rca_report.get('root_cause', {}).get('confidence_score', 0.0)
        
        logger.info(f"[{incident_id}] Investigation complete. Severity: {severity_score}")
        
        if severity_score > 0.8:
            logger.info(f"[{incident_id}] Severity {severity_score} > 0.8, sending to Slack")
            import os
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3001")
            await self.slack_notifier.send_rca(incident_id, rca_report, severity_score, frontend_url)
        else:
            logger.info(f"[{incident_id}] Severity {severity_score} <= 0.6, ignoring as false alert")
    
    def _format_trigger_reason(self, trigger_status: Dict[str, Any]) -> str:
        """Format trigger reason for incident data"""
        reasons = []
        
        metrics = trigger_status.get('metrics', {})
        if metrics.get('cpu_alert'):
            reasons.append(f"CPU: {metrics.get('cpu_usage', 0):.1f}%")
        if metrics.get('ram_alert'):
            reasons.append(f"RAM: {metrics.get('ram_usage', 0):.1f}%")
        
        logs = trigger_status.get('logs', {})
        if logs.get('alert_triggered'):
            reasons.append(f"Consecutive errors: {logs.get('error_count', 0)}")
        
        return " | ".join(reasons) if reasons else "Unknown trigger"
