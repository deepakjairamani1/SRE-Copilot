# Albeyla - Autonomous Incident Investigation Platform

Complete documentation for the SRE Copilot platform built for autonomous root cause analysis.

## Documentation Structure

- **[Frontend Documentation](./frontend/)** - React + TypeScript frontend application
- **[Backend Documentation](./backend/)** - FastAPI backend with AI-powered RCA

## Quick Links

- [Frontend Components](./frontend/COMPONENTS.md)
- [Backend API Reference](./backend/API.md)
- [Architecture Overview](./ARCHITECTURE.md)
- [Development Guide](./DEVELOPMENT.md)

## Platform Overview

Albeyla is an autonomous incident investigation platform that uses AI to analyze observability data (metrics, logs, traces) and generate comprehensive root cause analysis reports with remediation steps.

### Key Features

- **Autonomous Investigation**: AI-powered agentic loop (Plan → Act → Check → Adapt)
- **Multi-Source Analysis**: Integrates Prometheus, Loki, and Jaeger
- **Real-time Monitoring**: Live metrics and incident tracking
- **Comprehensive RCA**: Detailed reports with evidence and remediation
- **Beautiful UI**: Modern glassmorphism design with smooth animations

### Technology Stack

**Frontend:**
- React 18 + TypeScript + Vite
- TailwindCSS + Framer Motion
- React Query + React Router
- Recharts + Lucide Icons

**Backend:**
- FastAPI + Python 3.11
- AWS Bedrock (Claude 3.5 Sonnet)
- Redis for caching
- Prometheus, Loki, Jaeger integration

**Infrastructure:**
- Docker Compose
- Grafana for visualization
- Redis for session storage
