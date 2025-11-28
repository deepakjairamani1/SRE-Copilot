import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

from app.clients.prometheus_client import PrometheusClient
from app.clients.loki_client import LokiClient
from app.clients.jaeger_client import JaegerClient
from app.agents.bedrock_integration import call_bedrock

logger = logging.getLogger(__name__)


class RCAAgent:
    """Autonomous RCA Agent with visible agentic loop and RAG"""
    
    def __init__(self):
        from app.context import get_context
        ctx = get_context()
        
        self.prometheus_client = PrometheusClient(ctx.PROMETHEUS_URL)
        self.loki_client = LokiClient(ctx.LOKI_URL)
        self.jaeger_client = JaegerClient(ctx.JAEGER_QUERY_URL)
        self.timeout = 60
        self.steps = []
        
        # LLM Configuration from env
        self.llm_provider = os.getenv("LLM_PROVIDER", "claude").lower()
        self.llm_api_key = os.getenv("LLM_API_KEY", "")
        self.llm_model = os.getenv("LLM_MODEL", self._get_default_model())
        
        # For Bedrock, check AWS credentials instead of API key
        if self.llm_provider == "bedrock":
            self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID", "")
            self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
            self.has_credentials = bool(self.aws_access_key and self.aws_secret_key)
        else:
            self.has_credentials = bool(self.llm_api_key and self.llm_api_key != "dummy")
    
    def _get_default_model(self) -> str:
        """Get default model for provider"""
        defaults = {
            "bedrock": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            "claude": "claude-sonnet-4-20250514",
            "gpt": "gpt-4o",
            "gemini": "gemini-2.0-flash-exp",
            "grok": "llama-3.3-70b-versatile",
            "groq": "llama-3.3-70b-versatile"
        }
        return defaults.get(self.llm_provider, "claude-sonnet-4-20250514")
    
    async def investigate(self, incident_id: str, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main investigation with Plan → Act → Check → Adapt loop"""
        start_time = time.time()
        self.steps = []
        
        logger.info(f"[{incident_id}] Starting investigation for service: {incident_data.get('service')}")
        logger.info(f"[{incident_id}] LLM Provider: {self.llm_provider}, Model: {self.llm_model}")
        if self.llm_provider == "bedrock":
            logger.info(f"[{incident_id}] AWS Credentials configured: {self.has_credentials}")
        else:
            logger.info(f"[{incident_id}] API Key configured: {self.has_credentials}")
        
        try:
            # === STEP 1: PLAN ===
            await self._log_step("plan", "📋 Planning investigation strategy...")
            plan = self._create_investigation_plan(incident_data)
            await self._log_step("plan", f"Will investigate: {', '.join(plan['actions'])}")
            logger.info(f"[{incident_id}] Investigation plan created: {len(plan['actions'])} actions")
            
            # === STEP 2: ACT (Parallel data fetching) ===
            await self._log_step("act", "🔍 Fetching observability data...")
            
            logger.info(f"[{incident_id}] Starting parallel data collection...")
            # Fetch observability data first
            prom_result, loki_result, jaeger_result = await asyncio.gather(
                self._fetch_prometheus_data(incident_data),
                self._fetch_loki_data(incident_data),
                self._fetch_jaeger_data(incident_data),
                return_exceptions=True
            )
            
            prometheus_data = prom_result
            loki_data = loki_result
            jaeger_data = jaeger_result
            
            # Fetch similar incidents using observability data for keyword extraction
            similar_incidents = await self._fetch_similar_incidents(
                incident_data, prometheus_data, loki_data, jaeger_data
            )
            
            # Log data collection results
            logger.info(f"[{incident_id}] Prometheus data: {len(str(prometheus_data))} chars, has_error: {'error' in prometheus_data}")
            logger.info(f"[{incident_id}] Loki data: {len(str(loki_data))} chars, has_error: {'error' in loki_data}")
            logger.info(f"[{incident_id}] Jaeger data: {len(str(jaeger_data))} chars, has_error: {'error' in jaeger_data}")
            logger.info(f"[{incident_id}] Similar incidents found: {len(similar_incidents)}")
            
            await self._log_step("act", "✓ Data fetching complete")
            
            # === STEP 3: CHECK (Validate data quality) ===
            await self._log_step("check", "✓ Validating data quality...")
            validation = self._validate_data(prometheus_data, loki_data, jaeger_data)
            logger.info(f"[{incident_id}] Data validation: sufficient={validation['sufficient']}, reason={validation.get('reason', 'OK')}")
            
            if not validation["sufficient"]:
                await self._log_step("check", f"⚠️  {validation['reason']}")
                
                # === STEP 4: ADAPT (Retry or fallback) ===
                await self._log_step("adapt", "🔄 Adapting strategy due to insufficient data...")
                
                if validation.get("missing") == "prometheus":
                    await self._log_step("adapt", "Retrying Prometheus with wider time range...")
                    prometheus_data = await self._fetch_prometheus_data(incident_data, time_range="15m")
                
                if not self._validate_data(prometheus_data, loki_data, jaeger_data)["sufficient"]:
                    await self._log_step("adapt", "Using rule-based analysis as fallback")
                    rca_report = await self._rule_based_rca(prometheus_data, loki_data, jaeger_data)
                    
                    return {
                        "incident_id": incident_id,
                        "rca_report": rca_report,
                        "investigation_steps": self.steps,
                        "duration_seconds": round(time.time() - start_time, 2),
                        "cost_usd": 0.0,
                        "generated_at": datetime.now(timezone.utc).isoformat()
                    }
            
            await self._log_step("check", "✓ Data quality sufficient")
            
            # === STEP 5: GENERATE RCA (with RAG context) ===
            await self._log_step("act", "🧠 Generating RCA with AI (including past incident context)...")
            logger.info(f"[{incident_id}] Building LLM prompt with observability data...")
            
            # Add incident_id to incident_data for prompt saving
            incident_data_with_id = {**incident_data, "incident_id": incident_id}
            
            rca_report = await self._generate_rca_with_rag(
                prometheus_data,
                loki_data,
                jaeger_data,
                similar_incidents,
                incident_data_with_id
            )
            
            logger.info(f"[{incident_id}] RCA generation complete. Confidence: {rca_report.get('root_cause', {}).get('confidence_score', 0)}")
            await self._log_step("act", "✓ RCA generation complete")
            
            duration = time.time() - start_time
            
            investigation_result = {
                "incident_id": incident_id,
                "rca_report": rca_report,
                "investigation_steps": self.steps,
                "observability_data": {
                    "prometheus": prometheus_data,
                    "loki": loki_data,
                    "jaeger": jaeger_data,
                    "similar_incidents": similar_incidents
                },
                "duration_seconds": round(duration, 2),
                "cost_usd": self._calculate_cost(rca_report),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Save to database & JSON
            await self._save_incident_for_learning(incident_data, rca_report, investigation_result)
            
            return investigation_result
            
        except Exception as e:
            logger.error(f"[{incident_id}] Investigation failed: {e}", exc_info=True)
            await self._log_step("adapt", f"❌ Error: {str(e)}")
            return {
                "error": str(e),
                "investigation_steps": self.steps,
                "partial_results": "Investigation failed"
            }
    
    def _create_investigation_plan(self, incident_data: Dict) -> Dict:
        """Create investigation plan"""
        return {
            "actions": [
                "Query Prometheus for metrics",
                "Query Loki for error logs",
                "Query Jaeger for slow traces",
                "Search similar past incidents (RAG)"
            ]
        }
    
    async def _fetch_prometheus_data(self, incident_data: Dict, time_range: str = "5m") -> Dict:
        """Fetch metrics with error handling"""
        try:
            await self._log_step("act", f"  → Querying Prometheus (last {time_range})...")
            logger.debug(f"Prometheus URL: {self.prometheus_client.base_url}")
            data = await self.prometheus_client.get_critical_metrics()
            
            if "error" in data:
                logger.error(f"Prometheus returned error: {data['error']}")
                await self._log_step("act", f"  ✗ Prometheus error: {data['error']}")
                return data
            
            host_count = len(data.get('host_metrics', {}))
            otlp_count = len(data.get('otlp_metrics', {}))
            logger.info(f"Prometheus: {host_count} host metrics, {otlp_count} OTLP metrics")
            await self._log_step("act", f"  ✓ Fetched {host_count} host + {otlp_count} OTLP metrics")
            
            return data
        except Exception as e:
            logger.error(f"Prometheus fetch failed: {e}", exc_info=True)
            await self._log_step("act", f"  ✗ Prometheus failed: {str(e)}")
            return {"error": str(e)}
    
    async def _fetch_loki_data(self, incident_data: Dict) -> Dict:
        """Fetch logs with error handling"""
        try:
            await self._log_step("act", "  → Querying Loki for error logs...")
            logger.debug(f"Loki URL: {self.loki_client.base_url}")
            data = await self.loki_client.query_logs(time_range="5m")
            
            if "error" in data:
                logger.error(f"Loki returned error: {data['error']}")
                await self._log_step("act", f"  ✗ Loki error: {data['error']}")
                return data
            
            logs = data.get("logs", {})
            error_count = len(logs.get("error_logs", []))
            critical_count = len(logs.get("critical_logs", []))
            warning_count = len(logs.get("warning_logs", []))
            info_count = len(logs.get("info_logs", []))
            
            logger.info(f"Loki: {error_count} errors, {critical_count} critical, {warning_count} warnings, {info_count} info")
            await self._log_step("act", f"  ✓ Found {error_count} error logs, {critical_count} critical, {warning_count} warnings")
            
            return data
        except Exception as e:
            logger.error(f"Loki fetch failed: {e}", exc_info=True)
            await self._log_step("act", f"  ✗ Loki failed: {str(e)}")
            return {"error": str(e)}
    
    async def _fetch_jaeger_data(self, incident_data: Dict) -> Dict:
        """Fetch traces with error handling"""
        try:
            await self._log_step("act", "  → Querying Jaeger for traces...")
            logger.debug(f"Jaeger URL: {self.jaeger_client.base_url}")
            data = await self.jaeger_client.query_traces(time_range="5m")
            
            if "error" in data:
                logger.error(f"Jaeger returned error: {data['error']}")
                await self._log_step("act", f"  ✗ Jaeger error: {data['error']}")
                return data
            
            traces = data.get("traces", {})
            slow_count = len(traces.get("slow_traces", []))
            error_count = len(traces.get("error_traces", []))
            sample_count = len(traces.get("sample_traces_with_spans", []))
            
            logger.info(f"Jaeger: {slow_count} slow traces, {error_count} error traces, {sample_count} sample traces")
            await self._log_step("act", f"  ✓ Found {slow_count} slow traces, {error_count} error traces")
            
            return data
        except Exception as e:
            logger.error(f"Jaeger fetch failed: {e}", exc_info=True)
            await self._log_step("act", f"  ✗ Jaeger failed: {str(e)}")
            return {"error": str(e)}
    
    def _extract_current_keywords(self, prometheus_data: Dict, loki_data: Dict, jaeger_data: Dict) -> List[str]:
        """Extract keywords from current incident observability data"""
        keywords = set()
        
        # From metrics - add critical/warning status metrics
        for metric_type in ['host_metrics', 'otlp_metrics']:
            metrics = prometheus_data.get(metric_type, {})
            for name, data in metrics.items():
                status = data.get('status', 'ok')
                if status in ['critical', 'warning']:
                    # Extract key terms from metric name
                    parts = name.replace('_', '-').split('-')
                    keywords.update([p for p in parts if len(p) > 3])
        
        # From logs - extract from unique error messages
        logs = loki_data.get('logs', {})
        for level in ['error_logs', 'critical_logs']:
            for log in logs.get(level, [])[:5]:
                msg = log.get('message', '').lower()
                # Extract meaningful words
                words = [w for w in msg.split() if len(w) > 4 and w.isalpha()]
                keywords.update(words[:3])
        
        # From traces - extract operation names
        traces = jaeger_data.get('traces', {})
        for trace_type in ['slow_traces', 'error_traces']:
            for trace in traces.get(trace_type, [])[:3]:
                op = trace.get('operation_name', '').lower()
                keywords.update([w for w in op.split() if len(w) > 3])
        
        return list(keywords)[:10]
    
    def _calculate_keyword_similarity(self, current_keywords: List[str], past_keywords: List[str]) -> float:
        """Calculate keyword similarity - need at least 3 matching keywords"""
        if not current_keywords or not past_keywords:
            return 0.0
        
        current_set = set(k.lower() for k in current_keywords)
        past_set = set(k.lower() for k in past_keywords)
        
        if not current_set:
            return 0.0
        
        # Count matching keywords
        intersection = len(current_set & past_set)
        
        # Need at least 3 matches
        if intersection < 3:
            return 0.0
        
        # Calculate Jaccard similarity
        union = len(current_set | past_set)
        return (intersection / union * 100) if union > 0 else 0.0
    
    async def _fetch_similar_incidents(self, incident_data: Dict, prometheus_data: Dict = None, 
                                       loki_data: Dict = None, jaeger_data: Dict = None) -> List[Dict]:
        """RAG: Retrieve similar past incidents by keyword matching (60% threshold)"""
        try:
            await self._log_step("act", "  → Searching past incidents (RAG)...")
            
            service = incident_data.get("service", "")
            incidents_dir = Path("data/learning/incidents/")
            incidents_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract keywords from current incident
            current_keywords = self._extract_current_keywords(
                prometheus_data or {}, 
                loki_data or {}, 
                jaeger_data or {}
            )
            
            logger.debug(f"Current incident keywords: {current_keywords}")
            
            similar = []
            for filepath in incidents_dir.glob("*.json"):
                try:
                    with open(filepath, 'r') as f:
                        past = json.load(f)
                    
                    # Skip if different service
                    if past.get("service") != service:
                        continue
                    
                    # Calculate keyword similarity
                    past_keywords = past.get("keywords", [])
                    similarity = self._calculate_keyword_similarity(current_keywords, past_keywords)
                    
                    # Only include if similarity >= 60%
                    if similarity >= 60.0:
                        similar.append({
                            "incident_id": past["incident_id"],
                            "title": past["title"],
                            "root_cause": past["root_cause"],
                            "fix_applied": past["fix_applied"],
                            "success": past.get("success", True),
                            "similarity_score": round(similarity, 1),
                            "matched_keywords": list(set(current_keywords) & set(past_keywords))
                        })
                except:
                    continue
            
            similar.sort(key=lambda x: x["similarity_score"], reverse=True)
            top_similar = similar[:3]
            
            if top_similar:
                await self._log_step("act", f"  ✓ Found {len(top_similar)} similar past incidents (≥60% match)")
                for inc in top_similar:
                    await self._log_step("act", f"    • {inc['incident_id']}: {inc['similarity_score']}% match - {inc['title'][:40]}...")
            else:
                await self._log_step("act", "  ℹ No similar past incidents found (need ≥60% keyword match)")
            
            return top_similar
        except Exception as e:
            await self._log_step("act", f"  ✗ RAG retrieval failed: {str(e)}")
            return []
    
    def _validate_data(self, prometheus_data: Dict, loki_data: Dict, jaeger_data: Dict) -> Dict:
        """Check if we have sufficient data for RCA"""
        has_prometheus = "error" not in prometheus_data
        has_loki = "error" not in loki_data
        has_jaeger = "error" not in jaeger_data
        
        available = sum([has_prometheus, has_loki, has_jaeger])
        
        if available >= 2:
            return {"sufficient": True}
        
        missing = []
        if not has_prometheus: missing.append("prometheus")
        if not has_loki: missing.append("loki")
        if not has_jaeger: missing.append("jaeger")
        
        return {
            "sufficient": False,
            "reason": f"Insufficient data sources. Missing: {', '.join(missing)}",
            "missing": missing[0] if missing else None
        }
    
    async def _generate_rca_with_rag(self, prometheus_data: Dict, loki_data: Dict, 
                                     jaeger_data: Dict, similar_incidents: List, 
                                     incident_data: Dict) -> Dict:
        """Generate RCA using LLM API with RAG context"""
        prompt = self._build_enriched_prompt(
            prometheus_data, loki_data, jaeger_data, similar_incidents, incident_data
        )
        
        logger.info(f"Built prompt: {len(prompt)} chars (~{len(prompt)//4} tokens)")
        logger.debug(f"Prompt preview: {prompt[:500]}...")
        
        # Save prompt for visibility
        incident_id = incident_data.get('incident_id', 'unknown')
        self._save_prompt(incident_id, prompt)
        
        try:
            if not self.has_credentials:
                if self.llm_provider == "bedrock":
                    logger.warning("No AWS credentials configured for Bedrock, using rule-based analysis")
                    await self._log_step("adapt", "No AWS credentials, using rule-based analysis")
                else:
                    logger.warning("No LLM API key configured, using rule-based analysis")
                    await self._log_step("adapt", "No API key, using rule-based analysis")
                return await self._rule_based_rca(prometheus_data, loki_data, jaeger_data)
            
            # Call appropriate LLM provider
            logger.info(f"Calling {self.llm_provider} LLM with model {self.llm_model}...")
            response_text, tokens_used = await self._call_llm(prompt)
            logger.info(f"LLM response received: {len(response_text)} chars, {tokens_used} tokens used")
            logger.debug(f"LLM response preview: {response_text[:500]}...")
            
            # Save response
            incident_id = incident_data.get('incident_id', 'unknown')
            self._save_response(incident_id, response_text)
            
            # Extract JSON
            try:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                
                if json_start >= 0 and json_end > json_start:
                    rca_json = json.loads(response_text[json_start:json_end])
                else:
                    rca_json = self._create_structured_rca(response_text, prometheus_data, loki_data, jaeger_data)
            except:
                rca_json = self._create_structured_rca(response_text, prometheus_data, loki_data, jaeger_data)
            
            rca_json["_tokens_used"] = tokens_used
            
            return rca_json
        except Exception as e:
            logger.error(f"LLM API call failed: {e}", exc_info=True)
            await self._log_step("adapt", f"LLM API failed: {str(e)}, using rule-based analysis")
            return await self._rule_based_rca(prometheus_data, loki_data, jaeger_data)
    
    async def _call_llm(self, prompt: str) -> tuple[str, int]:
        """Call configured LLM provider"""
        if self.llm_provider == "bedrock":
            return await call_bedrock(prompt, self.llm_model)
        elif self.llm_provider == "claude":
            return await self._call_claude(prompt)
        elif self.llm_provider == "gpt":
            return await self._call_openai(prompt)
        elif self.llm_provider == "gemini":
            return await self._call_gemini(prompt)
        elif self.llm_provider == "grok":
            return await self._call_grok(prompt)
        elif self.llm_provider == "groq":
            return await self._call_groq(prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    async def _call_claude(self, prompt: str) -> tuple[str, int]:
        """Call Anthropic Claude API"""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.llm_api_key)
            
            message = client.messages.create(
                model=self.llm_model,
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            tokens_used = message.usage.input_tokens + message.usage.output_tokens
            
            return response_text, tokens_used
        except ImportError:
            raise Exception("anthropic package not installed. Run: pip install anthropic")
    
    async def _call_openai(self, prompt: str) -> tuple[str, int]:
        """Call OpenAI GPT API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.llm_api_key)
            
            response = client.chat.completions.create(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return response_text, tokens_used
        except ImportError:
            raise Exception("openai package not installed. Run: pip install openai")
    
    async def _call_gemini(self, prompt: str) -> tuple[str, int]:
        """Call Google Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.llm_api_key)
            
            model = genai.GenerativeModel(self.llm_model)
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=4000,
                    temperature=0.3
                )
            )
            
            response_text = response.text
            tokens_used = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            
            return response_text, tokens_used
        except ImportError:
            raise Exception("google-generativeai package not installed. Run: pip install google-generativeai")
    
    async def _call_grok(self, prompt: str) -> tuple[str, int]:
        """Call xAI Grok API (OpenAI-compatible)"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.llm_api_key,
                base_url="https://api.x.ai/v1"
            )
            
            response = client.chat.completions.create(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return response_text, tokens_used
        except ImportError:
            raise Exception("openai package not installed. Run: pip install openai")
    
    async def _call_groq(self, prompt: str) -> tuple[str, int]:
        """Call Groq API (OpenAI-compatible)"""
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.llm_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            
            response = client.chat.completions.create(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return response_text, tokens_used
        except ImportError:
            raise Exception("openai package not installed. Run: pip install openai")
    
    def _summarize_metrics(self, prometheus_data: Dict) -> str:
        """Show all metrics with full details"""
        summary = []
        
        # Host metrics
        host = prometheus_data.get('host_metrics', {})
        if host:
            summary.append("HOST METRICS:")
            for name, data in host.items():
                if data.get('current') is not None:
                    status = data.get('status', 'ok')
                    icon = '🔴 CRITICAL' if status == 'critical' else '🟡 WARNING' if status == 'warning' else '🟢 OK'
                    summary.append(f"  {icon} {name}: {data['current']:.2f} {data.get('unit', '')} (min:{data.get('min', 0):.1f}, max:{data.get('max', 0):.1f}, avg:{data.get('avg', 0):.1f})")
        
        # ALL OTLP metrics
        otlp = prometheus_data.get('otlp_metrics', {})
        if otlp:
            summary.append("\nOTLP METRICS:")
            for name, data in otlp.items():
                if data.get('current') is not None:
                    status = data.get('status', 'ok')
                    icon = '🔴 CRITICAL' if status == 'critical' else '🟡 WARNING' if status == 'warning' else '🟢 OK'
                    summary.append(f"  {icon} {name}: {data['current']:.2f} {data.get('unit', '')} (min:{data.get('min', 0):.1f}, max:{data.get('max', 0):.1f}, avg:{data.get('avg', 0):.1f})")
        
        return "\n".join(summary)
    
    def _deduplicate_logs(self, logs: Dict) -> str:
        """Deduplicate logs and show full messages including info logs for context"""
        result = []
        
        # Show error, critical, warning logs (all)
        for level in ['error_logs', 'critical_logs', 'warning_logs']:
            log_list = logs.get(level, [])
            if not log_list:
                continue
            
            # Group by message
            unique_msgs = {}
            for log in log_list:
                msg = log.get('message', '')
                if msg:
                    unique_msgs[msg] = unique_msgs.get(msg, 0) + 1
            
            if unique_msgs:
                result.append(f"\n{level.upper().replace('_LOGS', '')}:")
                for msg, count in sorted(unique_msgs.items(), key=lambda x: x[1], reverse=True)[:15]:
                    result.append(f"  [{count}x] {msg}")
        
        # Add 10 info logs for context (what's working normally)
        info_logs = logs.get('info_logs', [])
        if info_logs:
            result.append("\nINFO (for context - what's working):")
            unique_info = {}
            for log in info_logs:
                msg = log.get('message', '')
                if msg:
                    unique_info[msg] = unique_info.get(msg, 0) + 1
            
            for msg, count in sorted(unique_info.items(), key=lambda x: x[1], reverse=True)[:10]:
                result.append(f"  [{count}x] {msg}")
        
        return "\n".join(result) if result else "No logs found"
    
    def _summarize_traces(self, traces: Dict) -> str:
        """Show traces with full details including normal traces for context"""
        result = []
        
        slow = traces.get('slow_traces', [])[:10]
        errors = traces.get('error_traces', [])[:10]
        samples = traces.get('sample_traces_with_spans', [])[:10]
        
        if slow:
            result.append("\nSLOW TRACES (performance issues):")
            for t in slow:
                result.append(f"  - Operation: {t.get('operation_name', 'unknown')}")
                result.append(f"    Duration: {t.get('duration_ms', 0):.0f}ms, Spans: {t.get('span_count', 0)}, Service: {t.get('service', 'unknown')}")
        
        if errors:
            result.append("\nERROR TRACES (failures):")
            for t in errors:
                result.append(f"  - Operation: {t.get('operation_name', 'unknown')}")
                result.append(f"    Duration: {t.get('duration_ms', 0):.0f}ms, Service: {t.get('service', 'unknown')}")
                result.append(f"    Error: {t.get('error', 'unknown')}")
        
        if samples:
            result.append("\nNORMAL TRACES WITH SPANS (for context - what's working):")
            for t in samples[:10]:  # Show 10 normal traces
                result.append(f"  - Operation: {t.get('operation_name', 'unknown')}, Duration: {t.get('duration_ms', 0):.0f}ms")
                spans = t.get('spans', [])
                if spans:
                    result.append(f"    Spans ({len(spans)} total):")
                    for span in spans[:15]:  # Show more spans for context
                        result.append(f"      - {span.get('operation_name', 'unknown')}: {span.get('duration_ms', 0):.0f}ms")
        
        summary = traces.get('summary', {})
        if summary:
            result.append(f"\nSUMMARY: Total:{summary.get('total_traces', 0)}, P50:{summary.get('p50_latency_ms', 0):.0f}ms, P95:{summary.get('p95_latency_ms', 0):.0f}ms, P99:{summary.get('p99_latency_ms', 0):.0f}ms")
        
        return "\n".join(result) if result else "No traces found"
    
    def _build_enriched_prompt(self, prometheus_data: Dict, loki_data: Dict, 
                               jaeger_data: Dict, similar_incidents: List, 
                               incident_data: Dict) -> str:
        """Build enriched prompt with comprehensive observability data"""
        
        # Summarize metrics
        prom_str = self._summarize_metrics(prometheus_data)
        
        # Deduplicate logs
        logs = loki_data.get('logs', {})
        loki_str = self._deduplicate_logs(logs)
        
        # Summarize traces
        traces = jaeger_data.get('traces', {})
        jaeger_str = self._summarize_traces(traces)
        
        # Count data
        log_counts = f"ERROR: {len(logs.get('error_logs', []))}, CRITICAL: {len(logs.get('critical_logs', []))}, WARNING: {len(logs.get('warning_logs', []))}, INFO: {len(logs.get('info_logs', []))}"
        trace_counts = f"Slow: {len(traces.get('slow_traces', []))}, Error: {len(traces.get('error_traces', []))}, Samples: {len(traces.get('sample_traces_with_spans', []))}"
        
        prompt = f"""You are an expert SRE analyzing an incident.

CURRENT INCIDENT:
Service: {incident_data.get('service', 'core-athenamind')}
Detected: {incident_data.get('detected_at', 'now')}
Alert: Anomaly detected - investigate observability data below

=== DATA SUMMARY ===
Logs: {log_counts}
Traces: {trace_counts}
Metrics: {len(prometheus_data.get('host_metrics', {}))} host + {len(prometheus_data.get('otlp_metrics', {}))} OTLP

=== OBSERVABILITY DATA (LAST 5 MINUTES) ===

PROMETHEUS METRICS (Summarized):
{prom_str}

LOKI LOGS (Unique messages with occurrence count):
{loki_str}

JAEGER TRACES (Key traces and summary):
{jaeger_str}

=== RAG CONTEXT: SIMILAR PAST INCIDENTS ===
{self._format_similar_incidents(similar_incidents)}

=== YOUR TASK ===
Provide comprehensive RCA analysis:
1. What is going RIGHT (healthy metrics, normal behavior)
2. What is going WRONG (anomalies, errors, degradation)
3. Root cause with evidence from metrics/logs/traces
4. Immediate actions to resolve
5. Long-term prevention

Learn from similar past incidents - if a past fix worked, recommend it.

Generate a JSON response with these exact fields, give your analysis in detail and make it the best SRE agent with everything in place you need to do, use google for suggest best pratices and take your time to analyse this:
{{
  "executive_summary": {{
    "title": "brief title",
    "severity": "critical|high|medium|low",
    "impact": "what broke",
    "user_impact": "how users are affected"
  }},
  "timeline": [
    {{"timestamp": "HH:MM:SS", "event": "what happened", "source": "prometheus|loki|jaeger"}}
  ],
  "root_cause": {{
    "primary_cause": "the main issue",
    "contributing_factors": ["factor1", "factor2"],
    "evidence": [
      {{"type": "metric|log|trace", "description": "...", "value": "..."}}
    ],
    "confidence_score": 0.0-1.0,
    "similar_to_past_incident": "incident_id or null"
  }},
  "technical_details": {{
    "affected_components": [{{"component": "name", "status": "degraded|down"}}],
    "metrics_snapshot": {{}}
  }},
  "impact_assessment": {{
    "severity": "high",
    "users_affected": "estimate"
  }},
  "remediation": {{
    "immediate_actions": [
      {{"action": "what to do", "command": "exact command", "estimated_time": "30s", "expected_impact": "fixes X"}}
    ],
    "permanent_fixes": [
      {{"fix": "description", "priority": "P0|P1|P2"}}
    ]
  }},
  "prevention": {{
    "code_changes": ["change1"],
    "monitoring_enhancements": ["alert1"]
  }},
  "potential_causes": [
    {{"hypothesis": "maybe this", "probability": 0.0-1.0, "evidence": ["proof"]}}
  ],
  "confidence": {{
    "overall_score": 0.0-1.0,
    "uncertainties": ["what we're not sure about"],
    "recommendation": "what to do next"
  }}
}}

IMPORTANT: Return ONLY valid JSON, no markdown, no explanation.

AFTER generating the RCA, also provide learning metadata:
- Is this incident worth learning from? (novel issue, clear root cause, actionable fix)
- If yes, provide 5-7 relevant technical keywords (e.g., "http-error", "database-connection", "memory-leak", "timeout", "rate-limit")

Add these fields to your JSON response:
{{
  ...,
  "learning_metadata": {{
    "worth_learning": true/false,
    "reason": "why this is/isn't worth storing",
    "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
  }}
}}"""
        
        return prompt
    
    def _format_similar_incidents(self, incidents: List[Dict]) -> str:
        """Format similar incidents for RAG context"""
        if not incidents:
            return "No similar past incidents found in knowledge base."
        
        formatted = []
        for inc in incidents:
            formatted.append(f"""
Past Incident: {inc['incident_id']}
Title: {inc['title']}
Root Cause: {inc['root_cause']}
Fix Applied: {inc['fix_applied']}
Outcome: {'✓ Successful' if inc.get('success') else '✗ Failed'}
Similarity Score: {inc['similarity_score']}/5
""")
        
        return "\n---\n".join(formatted)
    
    async def _rule_based_rca(self, prometheus_data: Dict, loki_data: Dict, jaeger_data: Dict) -> Dict:
        """Fallback: Simple rule-based RCA when AI unavailable"""
        root_cause = "Unknown - insufficient data or AI unavailable"
        evidence = []
        
        # Check for high CPU
        cpu = prometheus_data.get('host_metrics', {}).get('cpu_usage_percent', {}).get('current')
        if cpu and cpu > 80:
            root_cause = f"High CPU usage detected ({cpu:.1f}%)"
            evidence.append({"type": "metric", "description": "CPU usage", "value": f"{cpu:.1f}%"})
        
        # Check for errors in logs
        error_logs = loki_data.get('logs', {}).get('error_logs', [])
        if len(error_logs) > 10:
            root_cause = f"Error burst detected ({len(error_logs)} errors in 5 minutes)"
            evidence.append({"type": "log", "description": "Error count", "value": str(len(error_logs))})
        
        # Check for slow traces
        slow_traces = jaeger_data.get('traces', {}).get('slow_traces', [])
        if slow_traces:
            duration = slow_traces[0].get('duration_ms', 0)
            root_cause = f"Slow traces detected (p95 latency: {duration:.0f}ms)"
            evidence.append({"type": "trace", "description": "Slow trace", "value": f"{duration:.0f}ms"})
        
        return {
            "executive_summary": {
                "title": "Rule-based analysis (AI unavailable)",
                "severity": "high",
                "impact": root_cause,
                "user_impact": "Service degradation possible"
            },
            "timeline": [],
            "root_cause": {
                "primary_cause": root_cause,
                "contributing_factors": [],
                "evidence": evidence,
                "confidence_score": 0.5,
                "similar_to_past_incident": None
            },
            "technical_details": {
                "affected_components": [],
                "metrics_snapshot": {}
            },
            "impact_assessment": {
                "severity": "high",
                "users_affected": "Unknown"
            },
            "remediation": {
                "immediate_actions": [
                    {"action": "Investigate manually", "command": "Check logs and metrics", "estimated_time": "5m", "expected_impact": "Identify root cause"}
                ],
                "permanent_fixes": []
            },
            "prevention": {
                "code_changes": [],
                "monitoring_enhancements": []
            },
            "potential_causes": [],
            "confidence": {
                "overall_score": 0.5,
                "uncertainties": ["Limited data available"],
                "recommendation": "Manual investigation recommended"
            },
            "learning_metadata": {
                "worth_learning": False,
                "reason": "Rule-based analysis - no AI insights",
                "keywords": []
            }
        }
    
    def _save_prompt(self, incident_id: str, prompt: str):
        """Save prompt to file for visibility"""
        try:
            prompts_dir = Path("data/prompts")
            prompts_dir.mkdir(parents=True, exist_ok=True)
            filepath = prompts_dir / f"{incident_id}.txt"
            
            with open(filepath, 'w') as f:
                f.write(prompt)
            
            logger.debug(f"[{incident_id}] Prompt saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save prompt: {e}")
    
    def _save_response(self, incident_id: str, response_text: str):
        """Save LLM response to file for visibility"""
        try:
            responses_dir = Path("data/responses")
            responses_dir.mkdir(parents=True, exist_ok=True)
            filepath = responses_dir / f"{incident_id}.txt"
            
            with open(filepath, 'w') as f:
                f.write(response_text)
            
            logger.debug(f"[{incident_id}] Response saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save response: {e}")
    
    async def _save_incident_for_learning(self, incident_data: Dict, rca_report: Dict, investigation_result: Dict):
        """Save incident to database AND JSON for RAG (only if worth learning)"""
        try:
            from app.db import SessionLocal
            from app.models import Incident, IncidentMetric
            from datetime import datetime
            
            incident_id = investigation_result.get("incident_id")
            llm_title = rca_report.get("executive_summary", {}).get("title", "Unknown incident")
            
            logger.info(f"[{incident_id}] Saving incident to database and JSON...")
            
            # Save to database
            logger.debug(f"[{incident_id}] Creating database session...")
            db = SessionLocal()
            try:
                logger.debug(f"[{incident_id}] Creating Incident record...")
                # Include observability_data in rca_report_json
                full_rca_report = {
                    **rca_report,
                    "observability_data": investigation_result.get("observability_data", {})
                }
                
                db_incident = Incident(
                    incident_id=incident_id,
                    service=incident_data.get("service", ""),
                    severity=rca_report.get("executive_summary", {}).get("severity", "high"),
                    status="open",
                    detected_at=datetime.fromisoformat(incident_data.get("detected_at", datetime.utcnow().isoformat())),
                    title=llm_title,
                    root_cause=rca_report.get("root_cause", {}).get("primary_cause", ""),
                    confidence_score=rca_report.get("root_cause", {}).get("confidence_score", 0.0),
                    user_impact=rca_report.get("executive_summary", {}).get("user_impact", ""),
                    users_affected=rca_report.get("impact_assessment", {}).get("users_affected", ""),
                    fix_applied=rca_report.get("remediation", {}).get("immediate_actions", [{}])[0].get("action", ""),
                    duration_seconds=investigation_result.get("duration_seconds", 0.0),
                    cost_usd=investigation_result.get("cost_usd", 0.0),
                    rca_report_json=full_rca_report,
                    investigation_steps=investigation_result.get("investigation_steps", []),
                    llm_provider=self.llm_provider,
                    tokens_used=rca_report.get("_tokens_used", 0)
                )
                db.add(db_incident)
                logger.debug(f"[{incident_id}] Committing to database...")
                db.commit()
                logger.info(f"[{incident_id}] Successfully saved to database")
            except Exception as db_error:
                logger.error(f"[{incident_id}] Database save failed: {db_error}", exc_info=True)
                db.rollback()
                raise
            finally:
                db.close()
            
            # Save to JSON for RAG (only if worth learning)
            learning_meta = rca_report.get("learning_metadata", {})
            worth_learning = learning_meta.get("worth_learning", False)
            
            if worth_learning:
                incidents_dir = Path("data/learning/incidents/")
                incidents_dir.mkdir(parents=True, exist_ok=True)
                filepath = incidents_dir / f"{incident_id}.json"
                
                # Use LLM-generated keywords
                keywords = learning_meta.get("keywords", [])
                if not keywords:
                    keywords = self._extract_keywords(llm_title)
                
                json_data = {
                    "incident_id": incident_id,
                    "title": llm_title,
                    "service": incident_data.get("service", ""),
                    "detected_at": incident_data.get("detected_at", ""),
                    "root_cause": rca_report.get("root_cause", {}).get("primary_cause", ""),
                    "fix_applied": rca_report.get("remediation", {}).get("immediate_actions", [{}])[0].get("action", ""),
                    "success": True,
                    "keywords": keywords,
                    "learning_reason": learning_meta.get("reason", "")
                }
                
                logger.debug(f"[{incident_id}] Writing JSON file: {filepath}")
                with open(filepath, 'w') as f:
                    json.dump(json_data, f, indent=2)
                
                logger.info(f"[{incident_id}] Successfully saved to JSON for RAG (worth learning: {learning_meta.get('reason', '')})")
                await self._log_step("act", f"  ✓ Saved to database & JSON for learning")
            else:
                logger.info(f"[{incident_id}] Skipped JSON save - not worth learning: {learning_meta.get('reason', 'No learning value')}")
                await self._log_step("act", f"  ✓ Saved to database (skipped learning - {learning_meta.get('reason', 'not novel')})")
        except Exception as e:
            logger.error(f"[{incident_id}] Failed to save incident: {e}", exc_info=True)
            await self._log_step("act", f"  ✗ Save failed: {str(e)}")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords for similarity matching"""
        stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are'}
        words = text.lower().split()
        keywords = [w for w in words if w not in stopwords and len(w) > 3]
        return keywords[:5]
    
    def _calculate_cost(self, rca_report: Dict) -> float:
        """Calculate API cost based on provider"""
        tokens = rca_report.get("_tokens_used", 0)
        
        # Cost per million tokens
        pricing = {
            "bedrock": 3.0,  # Bedrock Claude Sonnet 4
            "claude": 3.0,   # Claude Sonnet 4
            "gpt": 2.5,      # GPT-4o
            "gemini": 0.0,   # Gemini 2.0 Flash (free tier)
            "grok": 5.0,     # Grok Beta
            "groq": 0.0      # Groq (free tier)
        }
        
        cost_per_million = pricing.get(self.llm_provider, 3.0)
        cost = (tokens / 1_000_000) * cost_per_million
        return round(cost, 4)
    
    async def _log_step(self, step_type: str, message: str):
        """Log a step in the agentic loop"""
        self.steps.append({
            "step": step_type,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def _create_structured_rca(self, text: str, prometheus_data: Dict, 
                               loki_data: Dict, jaeger_data: Dict) -> Dict:
        """Create minimal structured RCA from unstructured text"""
        return {
            "executive_summary": {
                "title": "AI-generated analysis",
                "severity": "high",
                "impact": text[:200],
                "user_impact": "Service degradation"
            },
            "timeline": [],
            "root_cause": {
                "primary_cause": text[:200],
                "contributing_factors": [],
                "evidence": [],
                "confidence_score": 0.7,
                "similar_to_past_incident": None
            },
            "technical_details": {
                "affected_components": [],
                "metrics_snapshot": {}
            },
            "impact_assessment": {
                "severity": "high",
                "users_affected": "Unknown"
            },
            "remediation": {
                "immediate_actions": [{"action": "Review AI analysis", "command": "", "estimated_time": "5m", "expected_impact": ""}],
                "permanent_fixes": []
            },
            "prevention": {
                "code_changes": [],
                "monitoring_enhancements": []
            },
            "potential_causes": [],
            "confidence": {
                "overall_score": 0.7,
                "uncertainties": [],
                "recommendation": "Review analysis"
            },
            "_tokens_used": 0
        }
