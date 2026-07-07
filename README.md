# Enterprise GenAI Platform — Module 1C: Infrastructure Foundation

> **Status**: Module 1C — Infrastructure Foundation ✅  
> **Stack**: React · FastAPI · Nginx · PostgreSQL · Docker Compose · Pydantic · LangGraph

---

## Overview

This repository contains the foundational infrastructure for the **Enterprise GenAI Platform**. It orchestrates a multi-service architecture including a core business backend, a React frontend, an LLM routing API gateway, a stateful multi-agent LangGraph orchestrator, and a shared platform module.

All services are containerized and coordinated using Docker Compose for a seamless local development experience.

---

## Architecture and Services

The platform consists of the following services:

### 1. Shared Module (`shared/`)
A centralized package shared across the Python microservices (`backend`, `gateway`, `langgraph-service`) to ensure consistency, type-safety, and DRY code.
- **`constants/`**: Defines global provider strings (`openai`, `anthropic`, `gemini`, `deepseek`, `groq`, `ollama`), service identifiers, and configuration environments.
- **`exceptions/`**: Standard exceptions such as `GatewayException`, `AgentException`, and validation errors.
- **`config/`**: Base setting class powered by Pydantic Settings supporting environment variable overrides.
- **`utils/`**: Standardized system utilities, including a unified telemetry/logging helper.
- **`models/`**: Shared API schemas, including standardized health check formats and LLM request/response structures.

### 2. AI Gateway (`gateway/`)
A lightweight, fast ASGI service (FastAPI) responsible for proxying requests, implementing LLM provider routing, rate limiting, cost tracking, and provider fallback logic.
- **Folders**: `providers/`, `router/`, `telemetry/`, `services/`.
- **Status**: Scaffolded and ready for routing implementation. Includes a `/health` endpoint.

### 3. LangGraph Agent Service (`langgraph-service/`)
A stateful backend service responsible for coordinating multi-agent loops, state graphs, persistent conversational memory, prompt template rendering, and tool execution.
- **Folders**: `agents/`, `graphs/`, `memory/`, `prompts/`, `tools/`, `state/`.
- **Status**: Scaffolded and ready for agent definitions. Includes a `/health` endpoint.

### 4. Core Backend (`backend/`)
The platform's business logic engine handling authentication, user management, database persistence (SQLAlchemy ORM + Alembic migrations), and billing records.
- **Status**: Fully functional with a `/health` endpoint and PostgreSQL database connectivity.

### 5. Frontend (`frontend/`)
A modern React Single Page Application (React Router, TailwindCSS) compiled with Vite. It is containerized using a multi-stage Dockerfile and served using Nginx for production-grade performance.
- **Status**: Configured to build SPA routing assets and proxy API requests.

---

## Directory Structure

```
Enterprise-GenAI-Platform/
├── backend/               # FastAPI core backend & DB migrations
├── frontend/              # React frontend (Vite + SPA Nginx Dockerfile)
├── gateway/               # FastAPI LLM Routing Gateway service
├── langgraph-service/     # FastAPI LangGraph Agent Service
├── shared/                # Common models, configuration, and utilities
├── docker-compose.yml     # Local orchestration for all 5 containers
└── .env.example           # Global environment configuration
```

---

## Environment Variables

Copy `.env.example` to `.env` to configure infrastructure and LLM provider credentials:

```bash
cp .env.example .env
```

The configuration includes:
- **`DATABASE_URL`**: Async PostgreSQL connection string.
- **`JWT_SECRET`**: Key used for cryptographic signing of authorization tokens.
- **`REDIS_URL`**: Connection string for caching/rate-limiting backend.
- **`OPENAI_API_KEY`, `CLAUDE_API_KEY`, `GEMINI_API_KEY`...**: API keys for provider integrations.
- **`OLLAMA_URL`**: URL pointing to a locally running Ollama instance (default: `http://localhost:11434`).

---

## Quick Start (Docker Compose)

Launch all five services, including the database, with a single command:

```bash
# Start all containers in detatched mode
docker compose up -d --build
```

### Health Endpoints Verification

Verify the status of the running backend services:

*   **Core Backend**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
*   **AI Gateway**: [http://localhost:8010/health](http://localhost:8010/health)
*   **LangGraph Service**: [http://localhost:8020/health](http://localhost:8020/health)
