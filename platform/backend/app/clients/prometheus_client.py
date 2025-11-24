import httpx
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from functools import lru_cache
import asyncio

logger = logging.getLogger(__name__)


class PrometheusClient:
    """Async Prometheus client for querying host and OTLP metrics"""
    
    def __init__(self, base_url: str = "http://prometheus:9090", timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._cache_ttl = 30  # seconds
    
    async def _query(self, promql: str) -> Optional[Dict[str, Any]]:
        """Execute PromQL query against Prometheus API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/query",
                    params={"query": promql}
                )
                response.raise_for_status()
                data = response.json()
                
                if data["status"] == "success" and data["data"]["result"]:
                    return data["data"]["result"][0]
                return None
        except Exception as e:
            logger.error(f"Prometheus query failed: {promql} - {e}")
            return None
    
    async def _query_range_stats(self, query: str, time_range: str = "5m") -> Dict[str, float]:
        """Query range stats using query_range API"""
        try:
            import time
            end_time = int(time.time())
            start_time = end_time - 300  # 5 minutes
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/query_range",
                    params={
                        "query": query,
                        "start": start_time,
                        "end": end_time,
                        "step": "15s"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                if data["status"] == "success" and data["data"]["result"]:
                    values = [float(v[1]) for v in data["data"]["result"][0]["values"]]
                    if values:
                        return {
                            "max": max(values),
                            "min": min(values),
                            "avg": sum(values) / len(values),
                            "current": values[-1]
                        }
                return {"max": None, "min": None, "avg": None, "current": None}
        except Exception as e:
            logger.error(f"Range query failed: {query} - {e}")
            return {"max": None, "min": None, "avg": None, "current": None}
    
    def _calculate_status(self, value: Optional[float], metric_type: str) -> str:
        """Determine metric health status"""
        if value is None:
            return "unknown"
        
        thresholds = {
            "cpu_usage": (80, 60),
            "memory_usage": (80, 60),  # inverted logic handled in query
            "error_rate": (5, 1),
            "latency_p95": (1000, 500),
            "latency_p99": (1500, 1000)
        }
        
        if metric_type not in thresholds:
            return "ok"
        
        critical, warning = thresholds[metric_type]
        
        if value >= critical:
            return "critical"
        elif value >= warning:
            return "warning"
        return "ok"
    
    async def query_host_metrics(self, time_range: str = "5m") -> Dict[str, Any]:
        """Query host-level metrics from node_exporter"""
        cache_key = f"host_metrics_{time_range}"
        
        # Check cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if asyncio.get_event_loop().time() - cached_time < self._cache_ttl:
                return cached_data
        
        try:
            job = "core-athenamind-host-metrics"
            
            # CPU usage percentage
            cpu_query = f'100 - (avg(rate(system_cpu_time_seconds_total{{state="idle",job="{job}"}}[1m])) * 100)'
            cpu_stats = await self._query_range_stats(cpu_query, time_range)
            
            # Memory usage percentage (used / total)
            mem_query = f'(sum(system_memory_usage_bytes{{state="used",job="{job}"}}) / sum(system_memory_usage_bytes{{job="{job}"}})) * 100'
            mem_stats = await self._query_range_stats(mem_query, time_range)
            
            # Disk read bytes/sec
            disk_read_query = f'sum(rate(system_disk_io_bytes_total{{direction="read",job="{job}"}}[1m]))'
            disk_read_stats = await self._query_range_stats(disk_read_query, time_range)
            
            # Disk write bytes/sec
            disk_write_query = f'sum(rate(system_disk_io_bytes_total{{direction="write",job="{job}"}}[1m]))'
            disk_write_stats = await self._query_range_stats(disk_write_query, time_range)
            
            # Network receive bytes/sec
            net_rx_query = f'sum(rate(system_network_io_bytes_total{{direction="receive",job="{job}"}}[1m]))'
            net_rx_stats = await self._query_range_stats(net_rx_query, time_range)
            
            # Network transmit bytes/sec
            net_tx_query = f'sum(rate(system_network_io_bytes_total{{direction="transmit",job="{job}"}}[1m]))'
            net_tx_stats = await self._query_range_stats(net_tx_query, time_range)
            
            result = {
                "host_metrics": {
                    "cpu_usage_percent": {
                        **cpu_stats,
                        "unit": "percent",
                        "status": self._calculate_status(cpu_stats["current"], "cpu_usage")
                    },
                    "memory_usage_percent": {
                        **mem_stats,
                        "unit": "percent",
                        "status": self._calculate_status(mem_stats["current"], "memory_usage")
                    },
                    "disk_read_bytes_per_sec": {
                        **disk_read_stats,
                        "unit": "bytes/sec",
                        "status": "ok"
                    },
                    "disk_write_bytes_per_sec": {
                        **disk_write_stats,
                        "unit": "bytes/sec",
                        "status": "ok"
                    },
                    "network_receive_bytes_per_sec": {
                        **net_rx_stats,
                        "unit": "bytes/sec",
                        "status": "ok"
                    },
                    "network_transmit_bytes_per_sec": {
                        **net_tx_stats,
                        "unit": "bytes/sec",
                        "status": "ok"
                    }
                },
                "query_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Cache result
            self._cache[cache_key] = (result, asyncio.get_event_loop().time())
            return result
            
        except Exception as e:
            logger.error(f"Host metrics query failed: {e}")
            return {"error": "prometheus_unavailable", "query_timestamp": datetime.now(timezone.utc).isoformat()}
    
    async def query_otlp_metrics(self, time_range: str = "5m") -> Dict[str, Any]:
        """Query OTLP application metrics"""
        cache_key = f"otlp_metrics_{time_range}"
        
        # Check cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if asyncio.get_event_loop().time() - cached_time < self._cache_ttl:
                return cached_data
        
        try:
            job = "core-athenamind"
            
            # HTTP total requests (total count)
            http_total_query = f'sum(http_server_duration_milliseconds_count{{job="{job}"}})'
            http_total_stats = await self._query_range_stats(http_total_query, time_range)
            
            # HTTP error rate percentage (4xx + 5xx)
            error_rate_query = f'(sum(http_server_duration_milliseconds_count{{http_status_code=~"[45]..",job="{job}"}}) or vector(0)) / sum(http_server_duration_milliseconds_count{{job="{job}"}}) * 100'
            error_rate_stats = await self._query_range_stats(error_rate_query, time_range)
            
            # P95 latency from histogram
            p95_query = f'histogram_quantile(0.95, sum(http_server_duration_milliseconds_bucket{{job="{job}"}}) by (le))'
            p95_stats = await self._query_range_stats(p95_query, time_range)
            
            # P99 latency from histogram
            p99_query = f'histogram_quantile(0.99, sum(http_server_duration_milliseconds_bucket{{job="{job}"}}) by (le))'
            p99_stats = await self._query_range_stats(p99_query, time_range)
            
            # Active connections
            active_conn_query = f'http_server_active_requests{{job="{job}"}}'
            active_conn_stats = await self._query_range_stats(active_conn_query, time_range)
            
            # DB connections
            db_conn_query = f'db_client_connections_usage{{job="{job}"}}'
            db_conn_stats = await self._query_range_stats(db_conn_query, time_range)
            
            # Avg request size
            req_size_query = f'sum(http_server_request_size_bytes_sum{{job="{job}"}}) / sum(http_server_request_size_bytes_count{{job="{job}"}})'
            req_size_stats = await self._query_range_stats(req_size_query, time_range)
            
            # Avg response size
            resp_size_query = f'sum(http_server_response_size_bytes_sum{{job="{job}"}}) / sum(http_server_response_size_bytes_count{{job="{job}"}})'
            resp_size_stats = await self._query_range_stats(resp_size_query, time_range)
            
            # Avg response time
            avg_resp_time_query = f'sum(http_server_duration_milliseconds_sum{{job="{job}"}}) / sum(http_server_duration_milliseconds_count{{job="{job}"}})'
            avg_resp_time_stats = await self._query_range_stats(avg_resp_time_query, time_range)
            
            # P50 latency (median)
            p50_query = f'histogram_quantile(0.50, sum(http_server_duration_milliseconds_bucket{{job="{job}"}}) by (le))'
            p50_stats = await self._query_range_stats(p50_query, time_range)
            
            # P90 latency
            p90_query = f'histogram_quantile(0.90, sum(http_server_duration_milliseconds_bucket{{job="{job}"}}) by (le))'
            p90_stats = await self._query_range_stats(p90_query, time_range)
            
            # Request rate (req/sec) - using rate over time
            req_rate_query = f'sum(rate(http_server_duration_milliseconds_count{{job="{job}"}}[1m]))'
            req_rate_stats = await self._query_range_stats(req_rate_query, time_range)
            
            # Success rate (2xx + 3xx)
            success_rate_query = f'(sum(http_server_duration_milliseconds_count{{http_status_code=~"[23]..",job="{job}"}}) or vector(0)) / sum(http_server_duration_milliseconds_count{{job="{job}"}}) * 100'
            success_rate_stats = await self._query_range_stats(success_rate_query, time_range)
            
            # Asyncio process count
            asyncio_process_query = f'asyncio_process_created_total{{job="{job}"}}'
            asyncio_process_stats = await self._query_range_stats(asyncio_process_query, time_range)
            
            # Asyncio process duration avg
            asyncio_duration_query = f'rate(asyncio_process_duration_seconds_sum{{job="{job}"}}[1m]) / rate(asyncio_process_duration_seconds_count{{job="{job}"}}[1m]) * 1000'
            asyncio_duration_stats = await self._query_range_stats(asyncio_duration_query, time_range)
            
            result = {
                "otlp_metrics": {
                    "http_requests_total": {
                        **http_total_stats,
                        "unit": "requests",
                        "status": "ok"
                    },
                    "http_error_rate_percent": {
                        **error_rate_stats,
                        "unit": "percent",
                        "status": self._calculate_status(error_rate_stats["current"], "error_rate")
                    },
                    "http_latency_p95_ms": {
                        **p95_stats,
                        "unit": "milliseconds",
                        "status": self._calculate_status(p95_stats["current"], "latency_p95")
                    },
                    "http_latency_p99_ms": {
                        **p99_stats,
                        "unit": "milliseconds",
                        "status": self._calculate_status(p99_stats["current"], "latency_p99")
                    },
                    "active_connections": {
                        **active_conn_stats,
                        "unit": "connections",
                        "status": "ok"
                    },
                    "db_connections": {
                        **db_conn_stats,
                        "unit": "connections",
                        "status": "ok"
                    },
                    "avg_request_size_bytes": {
                        **req_size_stats,
                        "unit": "bytes",
                        "status": "ok"
                    },
                    "avg_response_size_bytes": {
                        **resp_size_stats,
                        "unit": "bytes",
                        "status": "ok"
                    },
                    "avg_response_time_ms": {
                        **avg_resp_time_stats,
                        "unit": "milliseconds",
                        "status": self._calculate_status(avg_resp_time_stats["current"], "latency_p95")
                    }
                },
                "query_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Cache result
            self._cache[cache_key] = (result, asyncio.get_event_loop().time())
            return result
            
        except Exception as e:
            logger.error(f"OTLP metrics query failed: {e}")
            return {"error": "prometheus_unavailable", "query_timestamp": datetime.now(timezone.utc).isoformat()}
    
    async def get_critical_metrics(self) -> Dict[str, Any]:
        """Get combined host and OTLP metrics with overall health status"""
        host_data, otlp_data = await asyncio.gather(
            self.query_host_metrics(),
            self.query_otlp_metrics()
        )
        
        # Determine overall health
        all_statuses = []
        
        if "host_metrics" in host_data:
            all_statuses.extend([m["status"] for m in host_data["host_metrics"].values()])
        
        if "otlp_metrics" in otlp_data:
            all_statuses.extend([m["status"] for m in otlp_data["otlp_metrics"].values()])
        
        if "critical" in all_statuses:
            overall_health = "critical"
        elif "warning" in all_statuses:
            overall_health = "degraded"
        elif "error" in host_data or "error" in otlp_data:
            overall_health = "unknown"
        else:
            overall_health = "healthy"
        
        return {
            **host_data,
            **otlp_data,
            "overall_health": overall_health,
            "query_timestamp": datetime.now(timezone.utc).isoformat()
        }


# Usage:
# client = PrometheusClient("http://localhost:9090")
# result = await client.get_critical_metrics()
# print(result["overall_health"])
