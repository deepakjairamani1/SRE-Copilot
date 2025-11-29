import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Send RCA reports to Slack"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.enabled = bool(webhook_url and webhook_url != "")
    
    async def send_rca(self, incident_id: str, rca_report: Dict[str, Any], severity_score: float, frontend_url: str = "http://localhost:3001") -> bool:
        """Send RCA to Slack based on severity"""
        if not self.enabled:
            logger.warning("Slack webhook not configured, skipping notification")
            return False
        
        if severity_score < 0.5:
            logger.info(f"Severity {severity_score} < 0.5, skipping Slack notification (too low)")
            return False
        
        is_potential_false_alert = 0.5 <= severity_score <= 0.8
        
        try:
            summary = rca_report.get('executive_summary', {})
            root_cause = rca_report.get('root_cause', {})
            remediation = rca_report.get('remediation', {})
            
            if is_potential_false_alert:
                severity_emoji = "⚠️"
                alert_type = "POTENTIAL FALSE ALERT"
            else:
                severity_emoji = "🔴" if severity_score > 0.9 else "🟠"
                alert_type = "CRITICAL INCIDENT"
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{severity_emoji} {alert_type}: {summary.get('title', 'Unknown')}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Incident ID:*\n{incident_id}"},
                        {"type": "mrkdwn", "text": f"*Severity Score:*\n{severity_score:.2f}/1.0"},
                        {"type": "mrkdwn", "text": f"*Severity:*\n{summary.get('severity', 'unknown').upper()}"},
                        {"type": "mrkdwn", "text": f"*User Impact:*\n{summary.get('user_impact', 'Unknown')}"}
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Root Cause:*\n{root_cause.get('primary_cause', 'Unknown')}"
                    }
                }
            ]
            
            immediate_actions = remediation.get('immediate_actions', [])
            if immediate_actions:
                action_text = "\n".join([f"• {a.get('action', 'N/A')}" for a in immediate_actions[:3]])
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Solution (Immediate Actions):*\n{action_text}"
                    }
                })
            
            permanent_fixes = remediation.get('permanent_fixes', [])
            if permanent_fixes:
                fix_text = "\n".join([f"• {f.get('fix', 'N/A')}" for f in permanent_fixes[:2]])
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Permanent Fixes:*\n{fix_text}"
                    }
                })
            
            if is_potential_false_alert:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "⚠️ *This may be a false alert* (severity 0.5-0.8). Review and dismiss if not critical."
                    }
                })
            
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🔗 View Full RCA"
                        },
                        "url": f"{frontend_url}/incidents/{incident_id}",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ Dismiss (False Alert)"
                        },
                        "url": f"{frontend_url}/incidents/{incident_id}?action=dismiss",
                        "style": "danger" if is_potential_false_alert else None
                    }
                ]
            })
            
            payload = {
                "text": f"Incident {incident_id}: {summary.get('title', 'Unknown')}",
                "blocks": blocks
            }
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
            
            logger.info(f"Slack notification sent for {incident_id} (severity: {severity_score})")
            return True
            
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            return False
