from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/auto-investigation", tags=["auto-investigation"])

# Global instance
auto_investigator = None


class AutoInvestigationConfig(BaseModel):
    enabled: bool
    slack_webhook_url: Optional[str] = None
    check_interval: Optional[int] = 10
    cpu_threshold: Optional[float] = 90.0
    ram_threshold: Optional[float] = 90.0
    consecutive_errors_threshold: Optional[int] = 3


@router.post("/start")
async def start_auto_investigation(config: AutoInvestigationConfig, background_tasks: BackgroundTasks):
    """Start automatic investigation monitoring"""
    global auto_investigator
    
    if auto_investigator and auto_investigator.running:
        return {"status": "already_running", "message": "Auto-investigation is already active"}
    
    from app.services.auto_investigator import AutoInvestigator
    
    auto_investigator = AutoInvestigator(slack_webhook_url=config.slack_webhook_url)
    auto_investigator.check_interval = config.check_interval
    auto_investigator.monitor.cpu_threshold = config.cpu_threshold
    auto_investigator.monitor.ram_threshold = config.ram_threshold
    auto_investigator.monitor.consecutive_errors_threshold = config.consecutive_errors_threshold
    
    background_tasks.add_task(auto_investigator.start_monitoring)
    
    return {
        "status": "started",
        "config": {
            "check_interval": config.check_interval,
            "cpu_threshold": config.cpu_threshold,
            "ram_threshold": config.ram_threshold,
            "consecutive_errors_threshold": config.consecutive_errors_threshold,
            "slack_enabled": bool(config.slack_webhook_url)
        }
    }


@router.post("/stop")
async def stop_auto_investigation():
    """Stop automatic investigation monitoring"""
    global auto_investigator
    
    if not auto_investigator or not auto_investigator.running:
        return {"status": "not_running", "message": "Auto-investigation is not active"}
    
    auto_investigator.stop_monitoring()
    
    return {"status": "stopped"}


@router.get("/status")
async def get_auto_investigation_status():
    """Get current status of auto-investigation"""
    global auto_investigator
    
    if not auto_investigator:
        return {
            "status": "not_initialized",
            "running": False
        }
    
    return {
        "status": "running" if auto_investigator.running else "stopped",
        "running": auto_investigator.running,
        "investigation_in_progress": auto_investigator.investigation_in_progress,
        "config": {
            "check_interval": auto_investigator.check_interval,
            "cpu_threshold": auto_investigator.monitor.cpu_threshold,
            "ram_threshold": auto_investigator.monitor.ram_threshold,
            "consecutive_errors_threshold": auto_investigator.monitor.consecutive_errors_threshold,
            "slack_enabled": auto_investigator.slack_notifier.enabled
        }
    }


@router.post("/test-trigger")
async def test_trigger():
    """Manually test the trigger evaluation"""
    global auto_investigator
    
    if not auto_investigator:
        from app.services.auto_investigator import AutoInvestigator
        auto_investigator = AutoInvestigator()
    
    trigger_status = await auto_investigator.monitor.evaluate_triggers()
    
    return {
        "trigger_status": trigger_status,
        "would_investigate": trigger_status.get('should_investigate', False)
    }


@router.post("/test-slack")
async def test_slack(slack_webhook_url: Optional[str] = None):
    """Send test message to Slack"""
    from app.services.slack_notifier import SlackNotifier
    
    webhook = slack_webhook_url
    if not webhook and auto_investigator:
        webhook = auto_investigator.slack_notifier.webhook_url
    
    if not webhook:
        return {"status": "error", "message": "No Slack webhook URL provided"}
    
    notifier = SlackNotifier(webhook)
    
    test_rca = {
        "executive_summary": {
            "title": "Test Alert from SRE Copilot",
            "severity": "low",
            "user_impact": "This is a test message"
        },
        "root_cause": {
            "primary_cause": "Testing Slack integration"
        },
        "remediation": {
            "immediate_actions": [
                {"action": "Verify Slack webhook is working"},
                {"action": "Check message formatting"}
            ]
        }
    }
    
    success = await notifier.send_rca("TEST-12345678", test_rca, 0.75)
    
    return {
        "status": "success" if success else "failed",
        "message": "Test message sent to Slack" if success else "Failed to send test message"
    }
