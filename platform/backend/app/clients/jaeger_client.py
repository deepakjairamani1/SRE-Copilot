import httpx
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class JaegerClient:
    """Async Jaeger client for querying distributed traces"""
    
    def __init__(self, base_url: str = "http://jaeger:16686", timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
    
    def _parse_span(self, span: Dict) -> Dict[str, Any]:
        """Parse Jaeger span into simplified format"""
        tags = {tag["key"]: tag["value"] for tag in span.get("tags", [])}
        
        return {
            "span_id": span["spanID"],
            "parent_span_id": span.get("references", [{}])[0].get("spanID") if span.get("references") else None,
            "operation_name": span["operationName"],
            "start_time": span["startTime"],
            "duration_ms": span["duration"] / 1000,
            "tags": tags,
            "error": tags.get("error", False) or tags.get("otel.status_code") == "ERROR"
        }
    
    def _build_span_tree(self, spans: List[Dict]) -> Dict:
        """Build hierarchical span tree"""
        span_map = {s["span_id"]: s for s in spans}
        root = None
        
        for span in spans:
            if not span["parent_span_id"]:
                root = span
            else:
                parent = span_map.get(span["parent_span_id"])
                if parent:
                    if "children" not in parent:
                        parent["children"] = []
                    parent["children"].append(span)
        
        return root or spans[0] if spans else {}
    
    def _calculate_critical_path(self, spans: List[Dict]) -> List[Dict]:
        """Find critical path (slowest sequential spans)"""
        sorted_spans = sorted(spans, key=lambda x: x["duration_ms"], reverse=True)
        return [
            {
                "operation": s["operation_name"],
                "duration_ms": s["duration_ms"],
                "start_time": s["start_time"]
            }
            for s in sorted_spans[:5]
        ]
    
    async def query_traces(self, time_range: str = "5m", limit: int = 100) -> Dict[str, Any]:
        """Query traces from Jaeger"""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(minutes=int(time_range.rstrip('m')))
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/traces",
                    params={
                        "service": "core-athenamind",
                        "start": int(start_time.timestamp() * 1e6),
                        "end": int(end_time.timestamp() * 1e6),
                        "limit": limit
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            if not data.get("data"):
                return self._empty_response()
            
            # Parse all traces
            all_traces = []
            durations = []
            
            for trace_data in data["data"]:
                trace = self._parse_trace(trace_data)
                all_traces.append(trace)
                durations.append(trace["duration_ms"])
            
            # Calculate percentiles
            durations.sort()
            p50 = durations[len(durations) // 2] if durations else 0
            p95 = durations[int(len(durations) * 0.95)] if durations else 0
            p99 = durations[int(len(durations) * 0.99)] if durations else 0
            
            # Categorize traces
            slow_traces = [t for t in all_traces if t["duration_ms"] > 500]
            error_traces = [t for t in all_traces if t["error"]]
            recent_traces = sorted(all_traces, key=lambda x: x["start_time"], reverse=True)[:10]
            
            # Get sample traces with full span details for AI analysis
            sample_traces_with_spans = []
            for trace in recent_traces[:5]:  # Top 5 recent traces
                trace_details = await self.get_trace_details(trace["trace_id"])
                if "error" not in trace_details:
                    sample_traces_with_spans.append({
                        "trace_id": trace["trace_id"],
                        "duration_ms": trace["duration_ms"],
                        "root_operation": trace["root_operation"],
                        "spans": trace_details["spans"],
                        "duration_breakdown": trace_details["duration_breakdown"]
                    })
            
            # Detect patterns
            patterns = self._detect_patterns(all_traces, slow_traces, error_traces)
            
            return {
                "traces": {
                    "slow_traces": slow_traces,
                    "error_traces": error_traces,
                    "recent_traces": recent_traces,
                    "sample_traces_with_spans": sample_traces_with_spans
                },
                "trace_summary": {
                    "total_traces": len(all_traces),
                    "slow_trace_count": len(slow_traces),
                    "error_trace_count": len(error_traces),
                    "p50_latency_ms": p50,
                    "p95_latency_ms": p95,
                    "p99_latency_ms": p99,
                    "avg_spans_per_trace": sum(t["total_spans"] for t in all_traces) / len(all_traces) if all_traces else 0
                },
                "patterns": patterns,
                "query_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Jaeger query failed: {e}")
            return {"error": "jaeger_unavailable", "query_timestamp": datetime.now(timezone.utc).isoformat()}
    
    def _parse_trace(self, trace_data: Dict) -> Dict[str, Any]:
        """Parse single trace"""
        spans = [self._parse_span(s) for s in trace_data["spans"]]
        
        # Get root span
        root_span = next((s for s in spans if not s["parent_span_id"]), spans[0] if spans else {})
        
        # Calculate trace duration
        if spans:
            start_times = [s["start_time"] for s in spans]
            end_times = [s["start_time"] + s["duration_ms"] * 1000 for s in spans]
            duration_us = max(end_times) - min(start_times)
            duration_ms = duration_us / 1000
        else:
            duration_ms = 0
        
        # Get services involved
        services = list(set(trace_data["processes"][span.get("processID", "")]["serviceName"] 
                           for span in trace_data["spans"] if span.get("processID")))
        
        # Find errors
        error_spans = [s for s in spans if s["error"]]
        
        # Find slowest span
        slowest_span = max(spans, key=lambda x: x["duration_ms"]) if spans else None
        
        return {
            "trace_id": trace_data["traceID"],
            "start_time": datetime.fromtimestamp(root_span.get("start_time", 0) / 1e6, tz=timezone.utc).isoformat(),
            "duration_ms": duration_ms,
            "total_spans": len(spans),
            "services": services,
            "root_operation": root_span.get("operation_name", "unknown"),
            "error": len(error_spans) > 0,
            "error_message": error_spans[0]["tags"].get("error.message") if error_spans else None,
            "slowest_span": {
                "operation": slowest_span["operation_name"],
                "duration_ms": slowest_span["duration_ms"],
                "service": services[0] if services else "unknown",
                "tags": slowest_span["tags"]
            } if slowest_span else None,
            "critical_path": self._calculate_critical_path(spans)
        }
    
    async def get_trace_details(self, trace_id: str) -> Dict[str, Any]:
        """Get full details for a specific trace"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/traces/{trace_id}")
                response.raise_for_status()
                data = response.json()
            
            if not data.get("data") or not data["data"]:
                return {"error": "trace_not_found"}
            
            trace_data = data["data"][0]
            spans = [self._parse_span(s) for s in trace_data["spans"]]
            
            # Build span tree
            span_tree = self._build_span_tree(spans)
            
            # Calculate duration breakdown by operation type
            duration_breakdown = defaultdict(float)
            for span in spans:
                op_type = span["operation_name"].split(".")[0] if "." in span["operation_name"] else "other"
                duration_breakdown[op_type] += span["duration_ms"]
            
            return {
                "trace_id": trace_id,
                "spans": sorted(spans, key=lambda x: x["start_time"]),
                "span_tree": span_tree,
                "duration_breakdown": dict(duration_breakdown)
            }
            
        except Exception as e:
            logger.error(f"Trace details query failed: {e}")
            return {"error": "jaeger_unavailable"}
    
    async def find_slow_operations(self) -> List[Dict[str, Any]]:
        """Find operations with consistently high latency"""
        try:
            traces_data = await self.query_traces(time_range="5m", limit=200)
            
            if "error" in traces_data:
                return []
            
            # Group by operation
            operation_stats = defaultdict(list)
            
            for trace in traces_data["traces"]["slow_traces"] + traces_data["traces"]["recent_traces"]:
                if trace.get("slowest_span"):
                    op = trace["slowest_span"]["operation"]
                    operation_stats[op].append({
                        "duration": trace["slowest_span"]["duration_ms"],
                        "trace_id": trace["trace_id"]
                    })
            
            # Calculate stats
            results = []
            for op, data_points in operation_stats.items():
                durations = [d["duration"] for d in data_points]
                if len(durations) >= 3:
                    results.append({
                        "operation": op,
                        "avg_duration_ms": statistics.mean(durations),
                        "p95_duration_ms": durations[int(len(durations) * 0.95)] if len(durations) > 1 else durations[0],
                        "count": len(durations),
                        "slowest_trace_id": max(data_points, key=lambda x: x["duration"])["trace_id"]
                    })
            
            return sorted(results, key=lambda x: x["avg_duration_ms"], reverse=True)
            
        except Exception as e:
            logger.error(f"Slow operations query failed: {e}")
            return []
    
    async def find_error_patterns(self) -> Dict[str, Any]:
        """Analyze error traces for patterns"""
        try:
            traces_data = await self.query_traces(time_range="5m", limit=200)
            
            if "error" in traces_data:
                return {"most_common_errors": [], "error_rate_trend": "stable"}
            
            error_traces = traces_data["traces"]["error_traces"]
            
            # Group errors by message
            error_counter = defaultdict(lambda: {"count": 0, "operations": set(), "trace_ids": []})
            
            for trace in error_traces:
                if trace.get("error_message"):
                    msg = trace["error_message"]
                    error_counter[msg]["count"] += 1
                    error_counter[msg]["operations"].add(trace["root_operation"])
                    error_counter[msg]["trace_ids"].append(trace["trace_id"])
            
            most_common = [
                {
                    "error_type": msg,
                    "count": data["count"],
                    "affected_operations": list(data["operations"]),
                    "sample_trace_id": data["trace_ids"][0]
                }
                for msg, data in sorted(error_counter.items(), key=lambda x: x[1]["count"], reverse=True)[:5]
            ]
            
            return {
                "most_common_errors": most_common,
                "error_rate_trend": "stable",
                "newly_appearing_errors": []
            }
            
        except Exception as e:
            logger.error(f"Error patterns query failed: {e}")
            return {"most_common_errors": [], "error_rate_trend": "unknown"}
    
    async def correlate_with_logs(self, trace_id: str, loki_client) -> List[Dict[str, Any]]:
        """Correlate trace with logs"""
        try:
            # Get trace details
            trace_details = await self.get_trace_details(trace_id)
            
            if "error" in trace_details:
                return []
            
            # Get logs for this trace
            logs = await loki_client.query_by_trace_id(trace_id)
            
            # Merge timeline
            timeline = []
            
            # Add span events
            for span in trace_details["spans"]:
                timeline.append({
                    "time": datetime.fromtimestamp(span["start_time"] / 1e6, tz=timezone.utc).isoformat(),
                    "type": "span_start",
                    "operation": span["operation_name"],
                    "span_id": span["span_id"]
                })
                
                end_time = span["start_time"] + (span["duration_ms"] * 1000)
                timeline.append({
                    "time": datetime.fromtimestamp(end_time / 1e6, tz=timezone.utc).isoformat(),
                    "type": "span_end",
                    "operation": span["operation_name"],
                    "error": span["error"]
                })
            
            # Add log events
            for log in logs:
                timeline.append({
                    "time": log["timestamp"],
                    "type": "log",
                    "level": log["level"],
                    "message": log["message"]
                })
            
            # Sort by time
            return sorted(timeline, key=lambda x: x["time"])
            
        except Exception as e:
            logger.error(f"Correlation failed: {e}")
            return []
    
    def _detect_patterns(self, all_traces: List, slow_traces: List, error_traces: List) -> Dict[str, Any]:
        """Detect patterns in traces"""
        patterns = {
            "slow_operation": None,
            "error_operation": None,
            "bottleneck_service": None,
            "cascade_failure_detected": False
        }
        
        # Find most common slow operation
        if slow_traces:
            slow_ops = [t["slowest_span"]["operation"] for t in slow_traces if t.get("slowest_span")]
            if slow_ops:
                from collections import Counter
                most_common = Counter(slow_ops).most_common(1)[0]
                avg_duration = statistics.mean([t["slowest_span"]["duration_ms"] 
                                               for t in slow_traces if t.get("slowest_span")])
                patterns["slow_operation"] = f"{most_common[0]} (avg {avg_duration:.1f}ms)"
        
        # Find most common error operation
        if error_traces:
            error_ops = [t["root_operation"] for t in error_traces]
            if error_ops:
                from collections import Counter
                most_common = Counter(error_ops).most_common(1)[0]
                patterns["error_operation"] = f"{most_common[0]} ({most_common[1]} failures)"
        
        # Find bottleneck service
        if slow_traces:
            services = []
            for t in slow_traces:
                services.extend(t["services"])
            if services:
                from collections import Counter
                most_common = Counter(services).most_common(1)[0]
                patterns["bottleneck_service"] = most_common[0]
        
        return patterns
    
    def _empty_response(self) -> Dict[str, Any]:
        """Return empty response structure"""
        return {
            "traces": {
                "slow_traces": [],
                "error_traces": [],
                "recent_traces": []
            },
            "trace_summary": {
                "total_traces": 0,
                "slow_trace_count": 0,
                "error_trace_count": 0,
                "p50_latency_ms": 0,
                "p95_latency_ms": 0,
                "p99_latency_ms": 0,
                "avg_spans_per_trace": 0
            },
            "patterns": {
                "slow_operation": None,
                "error_operation": None,
                "bottleneck_service": None,
                "cascade_failure_detected": False
            },
            "query_timestamp": datetime.now(timezone.utc).isoformat()
        }


# Usage:
# client = JaegerClient("http://localhost:16686")
# traces = await client.query_traces()
# details = await client.get_trace_details("abc123")
# slow_ops = await client.find_slow_operations()
