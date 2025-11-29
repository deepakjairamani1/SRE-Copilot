import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from collections import deque

logger = logging.getLogger(__name__)


class SystemMonitor:
    """Monitor CPU, RAM, and error logs for automatic investigation triggering"""
    
    def __init__(self, prometheus_client, loki_client):
        self.prometheus_client = prometheus_client
        self.loki_client = loki_client
        self.error_buffer = deque(maxlen=10)
        self.cpu_threshold = 90.0
        self.ram_threshold = 90.0
        self.consecutive_errors_threshold = 3
        
    async def check_metrics(self) -> Dict[str, Any]:
        """Check CPU and RAM utilization"""
        try:
            metrics = await self.prometheus_client.get_critical_metrics()
            
            cpu = metrics.get('host_metrics', {}).get('cpu_usage_percent', {}).get('current')
            ram = metrics.get('host_metrics', {}).get('memory_usage_percent', {}).get('current')
            
            cpu_alert = cpu and cpu > self.cpu_threshold
            ram_alert = ram and ram > self.ram_threshold
            
            return {
                'cpu_usage': cpu,
                'ram_usage': ram,
                'cpu_alert': cpu_alert,
                'ram_alert': ram_alert,
                'alert_triggered': cpu_alert or ram_alert
            }
        except Exception as e:
            logger.error(f"Metrics check failed: {e}")
            return {'alert_triggered': False, 'error': str(e)}
    
    async def check_error_logs(self) -> Dict[str, Any]:
        """Check for consecutive error logs"""
        try:
            logs = await self.loki_client.query_error_logs_only()
            
            error_logs = logs.get('error_logs', [])
            critical_logs = logs.get('critical_logs', [])
            
            total_errors = len(error_logs) + len(critical_logs)
            
            if total_errors > 0:
                self.error_buffer.append({
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'count': total_errors
                })
            
            consecutive_errors = len(self.error_buffer) >= self.consecutive_errors_threshold
            high_error_count = total_errors >= 10
            
            return {
                'error_count': total_errors,
                'consecutive_errors': consecutive_errors,
                'buffer_size': len(self.error_buffer),
                'alert_triggered': consecutive_errors or high_error_count,
                'recent_errors': list(self.error_buffer)
            }
        except Exception as e:
            logger.error(f"Error log check failed: {e}")
            return {'alert_triggered': False, 'error': str(e)}
    
    async def evaluate_triggers(self) -> Dict[str, Any]:
        """Evaluate all triggers and return combined status"""
        metrics_result, logs_result = await asyncio.gather(
            self.check_metrics(),
            self.check_error_logs()
        )
        
        should_investigate = (
            metrics_result.get('alert_triggered', False) or 
            logs_result.get('alert_triggered', False)
        )
        
        return {
            'should_investigate': should_investigate,
            'metrics': metrics_result,
            'logs': logs_result,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
