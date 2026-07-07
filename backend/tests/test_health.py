"""
Tests for the health check endpoint.

Verifies:
- GET /api/v1/health returns HTTP 200
- Response body matches the specified contract: {"status": "healthy", "service": "backend"}
- Response includes X-Request-ID header (injected by RequestLoggingMiddleware)
- Response Content-Type is application/json
"""

import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    """Test suite for GET /api/v1/health."""

    @pytest.mark.asyncio
    async def test_health_returns_200(self, client: AsyncClient) -> None:
        """Health endpoint must return HTTP 200 OK."""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_response_body(self, client: AsyncClient) -> None:
        """Response body must match the exact contract specified in Module 1A."""
        response = await client.get("/api/v1/health")
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "backend"

    @pytest.mark.asyncio
    async def test_health_response_has_exactly_two_fields(self, client: AsyncClient) -> None:
        """Response body must contain exactly the fields: status and service."""
        response = await client.get("/api/v1/health")
        data = response.json()

        assert set(data.keys()) == {"status", "service"}

    @pytest.mark.asyncio
    async def test_health_content_type_is_json(self, client: AsyncClient) -> None:
        """Response must have Content-Type: application/json."""
        response = await client.get("/api/v1/health")
        assert "application/json" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_health_includes_request_id_header(self, client: AsyncClient) -> None:
        """
        Every response must include X-Request-ID injected by RequestLoggingMiddleware.
        This validates the middleware is correctly wired into the application.
        """
        response = await client.get("/api/v1/health")
        assert "x-request-id" in response.headers
        assert len(response.headers["x-request-id"]) == 36  # UUID4 format

    @pytest.mark.asyncio
    async def test_health_request_id_is_unique_per_request(self, client: AsyncClient) -> None:
        """Each request must receive a unique X-Request-ID."""
        response1 = await client.get("/api/v1/health")
        response2 = await client.get("/api/v1/health")

        assert response1.headers["x-request-id"] != response2.headers["x-request-id"]
