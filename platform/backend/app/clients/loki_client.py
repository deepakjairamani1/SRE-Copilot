import httpx
import json
import re
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from collections import Counter

logger = logging.getLogger(__name__)


class LokiClient:
    """Async Loki client for querying logs"""
    
    def __init__(self, base_url: str = "http://loki:3100", timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
    
    def _parse_log_line(self, log_line: str, labels: Dict[str, str]) -> Dict[str, Any]:
        """Parse log line and extract structured data"""
        parsed = {
            "level": "INFO",
            "message": log_line,
            "trace_id": None,
            "span_id": None,
            "service_name": labels.get("service_name", "unknown"),
            "source": None,
            "exception": None,
            "stack_trace": []
        }
        
        # Try JSON parsing first (OTLP format)
        try:
            if log_line.strip().startswith("{"):
                data = json.loads(log_line)
                
                # Handle nested OTLP format
                if "body" in data:
                    body = json.loads(data["body"]) if isinstance(data["body"], str) else data["body"]
                    parsed["level"] = body.get("level", "INFO").upper()
                    parsed["message"] = body.get("message", log_line)
                    parsed["trace_id"] = body.get("trace_id")
                    parsed["span_id"] = body.get("span_id")
                    
                    if "module" in body and "line" in body:
                        parsed["source"] = f"{body['module']}:{body['line']}"
                    
                    if "attributes" in data:
                        parsed["service_name"] = data["attributes"].get("service.name", parsed["service_name"])
                    
                    return parsed
                
                # Handle simple JSON format
                parsed["level"] = data.get("level", data.get("severity", "INFO")).upper()
                parsed["message"] = data.get("message", data.get("msg", log_line))
                parsed["trace_id"] = data.get("trace_id", data.get("traceId"))
                parsed["span_id"] = data.get("span_id", data.get("spanId"))
                parsed["exception"] = data.get("exception", data.get("error_type"))
                
                if "source" in data:
                    parsed["source"] = data["source"]
                elif "file" in data and "line" in data:
                    parsed["source"] = f"{data['file']}:{data['line']}"
                
                if "stack_trace" in data:
                    parsed["stack_trace"] = data["stack_trace"][:5]
                
                return parsed
        except Exception as e:
            logger.debug(f"JSON parse failed: {e}")
            pass
        
        # Extract level from patterns
        level_match = re.search(r'\b(DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL)\b', log_line, re.IGNORECASE)
        if level_match:
            parsed["level"] = level_match.group(1).upper()
            if parsed["level"] == "WARNING":
                parsed["level"] = "WARN"
        
        # Extract trace_id
        trace_match = re.search(r'trace[_-]?id[=:]?\s*([a-f0-9]{16,32})', log_line, re.IGNORECASE)
        if trace_match:
            parsed["trace_id"] = trace_match.group(1)
        
        # Extract span_id
        span_match = re.search(r'span[_-]?id[=:]?\s*([a-f0-9]{16})', log_line, re.IGNORECASE)
        if span_match:
            parsed["span_id"] = span_match.group(1)
        
        # Extract source file:line
        source_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_/]*\.py):(\d+)', log_line)
        if source_match:
            parsed["source"] = f"{source_match.group(1)}:{source_match.group(2)}"
        
        # Extract exception type
        exc_match = re.search(r'(Exception|Error):\s*(.+?)(?:\n|$)', log_line)
        if exc_match:
            parsed["exception"] = exc_match.group(1)
            parsed["message"] = exc_match.group(2).strip()
        
        return parsed
    
    async def query_logs(self, time_range: str = "5m", limit: int = 1000, start_time_iso: str = None) -> Dict[str, Any]:
        """Query logs from Loki with categorization"""
        try:
            end_time = datetime.now(timezone.utc)
            
            if start_time_iso:
                start_time = datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))
            else:
                start_time = end_time - timedelta(minutes=int(time_range.rstrip('m')))
            
            query = '{exporter="OTLP"}'
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/loki/api/v1/query_range",
                    params={
                        "query": query,
                        "start": int(start_time.timestamp() * 1e9),
                        "end": int(end_time.timestamp() * 1e9),
                        "limit": limit
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            if data["status"] != "success" or not data["data"]["result"]:
                return self._empty_response()
            
            # Parse all logs
            all_logs = []
            for stream in data["data"]["result"]:
                labels = stream["stream"]
                for entry in stream["values"]:
                    timestamp_ns, log_line = entry
                    parsed = self._parse_log_line(log_line, labels)
                    parsed["timestamp"] = datetime.fromtimestamp(
                        int(timestamp_ns) / 1e9, tz=timezone.utc
                    ).isoformat()
                    all_logs.append(parsed)
            
            # Categorize logs
            error_logs = [log for log in all_logs if log["level"] == "ERROR"]
            critical_logs = [log for log in all_logs if log["level"] in ["CRITICAL", "FATAL"]]
            warning_logs = [log for log in all_logs if log["level"] in ["WARN", "WARNING"]]
            info_logs = [log for log in all_logs if log["level"] == "INFO"]
            debug_logs = [log for log in all_logs if log["level"] == "DEBUG"]
            
            # Get top warnings by frequency
            warning_messages = [log["message"] for log in warning_logs]
            warning_counter = Counter(warning_messages)
            top_warnings = []
            for msg, count in warning_counter.most_common(20):
                matching_log = next(log for log in warning_logs if log["message"] == msg)
                matching_log["frequency"] = count
                top_warnings.append(matching_log)
            
            # Most common errors
            error_messages = [log["message"] for log in error_logs]
            error_counter = Counter(error_messages)
            most_common_errors = [
                {"message": msg, "count": count}
                for msg, count in error_counter.most_common(5)
            ]
            
            # Detect patterns
            patterns = await self._detect_patterns(all_logs, error_logs)
            
            return {
                "logs": {
                    "error_logs": error_logs,
                    "critical_logs": critical_logs,
                    "warning_logs": top_warnings,
                    "info_logs": sorted(info_logs, key=lambda x: x["timestamp"], reverse=True)[:10],
                    "debug_logs_sample": sorted(debug_logs, key=lambda x: x["timestamp"], reverse=True)[:5]
                },
                "log_summary": {
                    "total_logs": len(all_logs),
                    "error_count": len(error_logs),
                    "critical_count": len(critical_logs),
                    "warning_count": len(warning_logs),
                    "time_range": time_range,
                    "most_common_errors": most_common_errors
                },
                "patterns": patterns,
                "query_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Loki query failed: {e}")
            return {"error": "loki_unavailable", "logs": {}, "query_timestamp": datetime.now(timezone.utc).isoformat()}
    
    async def query_error_logs_only(self, start_time_iso: str = None) -> Dict[str, Any]:
        """Quick query for ERROR and CRITICAL logs only"""
        try:
            end_time = datetime.now(timezone.utc)
            
            if start_time_iso:
                start_time = datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))
            else:
                start_time = end_time - timedelta(minutes=5)
            
            query = '{exporter="OTLP"} |~ "ERROR|CRITICAL|FATAL"'
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/loki/api/v1/query_range",
                    params={
                        "query": query,
                        "start": int(start_time.timestamp() * 1e9),
                        "end": int(end_time.timestamp() * 1e9),
                        "limit": 500
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            if data["status"] != "success" or not data["data"]["result"]:
                return {"error_logs": [], "critical_logs": []}
            
            error_logs = []
            critical_logs = []
            
            for stream in data["data"]["result"]:
                labels = stream["stream"]
                for entry in stream["values"]:
                    timestamp_ns, log_line = entry
                    parsed = self._parse_log_line(log_line, labels)
                    parsed["timestamp"] = datetime.fromtimestamp(
                        int(timestamp_ns) / 1e9, tz=timezone.utc
                    ).isoformat()
                    
                    if parsed["level"] in ["CRITICAL", "FATAL"]:
                        critical_logs.append(parsed)
                    elif parsed["level"] == "ERROR":
                        error_logs.append(parsed)
            
            return {
                "error_logs": error_logs,
                "critical_logs": critical_logs,
                "total_errors": len(error_logs) + len(critical_logs)
            }
            
        except Exception as e:
            logger.error(f"Error logs query failed: {e}")
            return {"error": "loki_unavailable", "error_logs": [], "critical_logs": []}
    
    async def query_by_trace_id(self, trace_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a specific trace ID"""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=1)
            
            query = f'{{exporter="OTLP"}} |~ "{trace_id}"'
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/loki/api/v1/query_range",
                    params={
                        "query": query,
                        "start": int(start_time.timestamp() * 1e9),
                        "end": int(end_time.timestamp() * 1e9),
                        "limit": 1000
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            if data["status"] != "success" or not data["data"]["result"]:
                return []
            
            logs = []
            for stream in data["data"]["result"]:
                labels = stream["stream"]
                for entry in stream["values"]:
                    timestamp_ns, log_line = entry
                    parsed = self._parse_log_line(log_line, labels)
                    if parsed["trace_id"] == trace_id or trace_id in log_line:
                        parsed["timestamp"] = datetime.fromtimestamp(
                            int(timestamp_ns) / 1e9, tz=timezone.utc
                        ).isoformat()
                        logs.append(parsed)
            
            return sorted(logs, key=lambda x: x["timestamp"])
            
        except Exception as e:
            logger.error(f"Trace query failed: {e}")
            return []
    
    async def detect_log_patterns(self) -> Dict[str, Any]:
        """Detect patterns in logs"""
        result = await self.query_logs(time_range="5m")
        
        if "error" in result:
            return {"error": result["error"]}
        
        return result.get("patterns", {})
    
    async def _detect_patterns(self, all_logs: List[Dict], error_logs: List[Dict]) -> Dict[str, Any]:
        """Analyze logs for patterns"""
        patterns = {
            "repeated_errors": [],
            "spike_detected": False,
            "new_errors": [],
            "cascade_detected": False
        }
        
        # Detect repeated errors (same error >5 times in 1 minute)
        if error_logs:
            error_messages = [log["message"] for log in error_logs]
            error_counter = Counter(error_messages)
            
            for msg, count in error_counter.items():
                if count >= 5:
                    patterns["repeated_errors"].append({
                        "message": msg,
                        "count": count,
                        "severity": "high" if count >= 10 else "medium"
                    })
            
            # Detect spike (compare error rate)
            recent_errors = [log for log in error_logs 
                           if datetime.fromisoformat(log["timestamp"]) > 
                           datetime.now(timezone.utc) - timedelta(minutes=2)]
            
            if len(error_logs) > 0:
                recent_rate = len(recent_errors) / 2  # errors per minute
                overall_rate = len(error_logs) / 5
                
                if recent_rate > overall_rate * 1.5:
                    patterns["spike_detected"] = True
        
        return patterns
    
    def _empty_response(self) -> Dict[str, Any]:
        """Return empty response structure"""
        return {
            "logs": {
                "error_logs": [],
                "critical_logs": [],
                "warning_logs": [],
                "info_logs": [],
                "debug_logs_sample": []
            },
            "log_summary": {
                "total_logs": 0,
                "error_count": 0,
                "critical_count": 0,
                "warning_count": 0,
                "time_range": "5m",
                "most_common_errors": []
            },
            "patterns": {
                "repeated_errors": [],
                "spike_detected": False,
                "new_errors": [],
                "cascade_detected": False
            },
            "query_timestamp": datetime.now(timezone.utc).isoformat()
        }


# Usage:
# client = LokiClient("http://localhost:3100")
# logs = await client.query_logs()
# errors = await client.query_error_logs_only()
# trace_logs = await client.query_by_trace_id("abc123")
