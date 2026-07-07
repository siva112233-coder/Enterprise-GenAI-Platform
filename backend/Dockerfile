# =============================================================================
# Enterprise GenAI Platform — Backend Dockerfile
# Module 1A: Backend Foundation
# =============================================================================
#
# Multi-stage build for a lean, secure production image:
#   Stage 1 (builder): Install dependencies in an isolated venv
#   Stage 2 (runtime): Copy only the venv — no build tools in production image
#
# Usage:
#   Build:  docker build -t genai-backend:latest .
#   Run:    docker run -p 8000:8000 --env-file .env genai-backend:latest
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Dependency builder
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

# Security: run as non-root even during build
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home appuser

# System dependencies required to compile Python packages (psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Upgrade pip and install into an isolated virtual environment
# Using a venv ensures the final stage has a clean, portable Python environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only requirements first for optimal layer caching.
# Docker will reuse this layer unless requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip==24.3.1 && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Runtime image
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

LABEL maintainer="platform-team@example.com" \
      org.opencontainers.image.title="Enterprise GenAI Platform — Backend" \
      org.opencontainers.image.description="FastAPI-based AI Gateway backend" \
      org.opencontainers.image.version="0.1.0"

# Security: create a non-root user for runtime
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home appuser

# Runtime system dependencies only (libpq for asyncpg/psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy the application source code
# .dockerignore should exclude: __pycache__, .env, .git, tests/, *.pyc
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Health check for Docker / container orchestrators
# Runs every 30s; marks container unhealthy after 3 consecutive failures
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Environment defaults (overridden via --env-file or -e flags)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    HOST=0.0.0.0

# Application entry point
# --factory: loads the app via the create_application factory for proper lifespan
# --workers: set to 1 in container (scale via replicas, not workers)
# --access-log: disabled here — handled by RequestLoggingMiddleware
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--no-access-log", \
     "--loop", "uvloop"]
