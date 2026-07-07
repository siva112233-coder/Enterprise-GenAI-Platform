# =============================================================================
# Enterprise GenAI Platform — LangGraph Service Dockerfile
# =============================================================================
FROM python:3.12-slim AS builder

WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY langgraph-service/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy the shared package and langgraph code
COPY shared ./shared
COPY langgraph-service/main.py .
COPY langgraph-service/agents ./agents
COPY langgraph-service/graphs ./graphs
COPY langgraph-service/memory ./memory
COPY langgraph-service/prompts ./prompts
COPY langgraph-service/tools ./tools
COPY langgraph-service/state ./state

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
