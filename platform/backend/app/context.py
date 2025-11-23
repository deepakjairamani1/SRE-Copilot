from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Dict, Any


class Context(BaseSettings):
    """Configuration management using Pydantic BaseSettings"""
    
    # Database
    DB_URL: str = "sqlite:////data/sre_copilot.db"
    
    # External services
    REDIS_URL: str = "redis://redis:6379"
    JAEGER_QUERY_URL: str = "http://jaeger:16686"
    PROMETHEUS_URL: str = "http://prometheus:9090"
    LOKI_URL: str = "http://loki:3100"
    
    # API keys and secrets
    ANTHROPIC_API_KEY: str = ""
    
    # Environment
    ENV: str = "dev"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def debug_info(self) -> Dict[str, Any]:
        """Return configuration with masked secrets for debugging"""
        config = self.dict()
        
        # Mask sensitive fields
        if config.get("ANTHROPIC_API_KEY"):
            config["ANTHROPIC_API_KEY"] = f"{config['ANTHROPIC_API_KEY'][:8]}***"
        
        return {
            "service": "sre-copilot-api",
            "environment": config["ENV"],
            "config": config
        }


@lru_cache()
def get_context() -> Context:
    """Singleton pattern for configuration - cached for performance"""
    return Context()