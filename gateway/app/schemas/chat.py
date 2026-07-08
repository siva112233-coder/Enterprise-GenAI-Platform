"""
Pydantic schemas for the AI Gateway API contracts.

These schemas define the public surface of the Gateway's REST API.
They are intentionally decoupled from any provider-internal data model.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────

class MessageRole(str, Enum):
    """Valid roles for a chat message."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ProviderStatus(str, Enum):
    """Lifecycle status reported by a provider's health check."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNCONFIGURED = "unconfigured"  # API key missing but provider is registered


# ─────────────────────────────────────────────────────────────────────────────
# Message
# ─────────────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    """A single message in a conversation turn."""

    role: MessageRole = Field(
        ...,
        description="The speaker role for this message.",
        examples=["user", "assistant"],
    )
    content: str = Field(
        ...,
        min_length=1,
        description="The text content of the message.",
    )

    model_config = {"use_enum_values": True}


# ─────────────────────────────────────────────────────────────────────────────
# Request
# ─────────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """
    Incoming chat request payload.

    The caller specifies which provider and model to use.
    The gateway validates, routes, and returns a ``ChatResponse``.
    """

    provider: str = Field(
        ...,
        description="Target LLM provider (e.g. openai, claude, gemini, deepseek, groq, ollama).",
        examples=["openai"],
        min_length=1,
    )
    model: str = Field(
        ...,
        description="Model identifier as recognised by the provider.",
        examples=["gpt-4o"],
        min_length=1,
    )
    messages: List[ChatMessage] = Field(
        ...,
        description="Ordered list of conversation messages.",
        min_length=1,
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature. Higher values produce more random output.",
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        le=16_384,
        description="Maximum number of tokens in the completion.",
    )
    stream: bool = Field(
        default=False,
        description="Whether to stream the response via Server-Sent Events.",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional caller-supplied metadata (request IDs, tags, etc.).",
    )

    @field_validator("provider")
    @classmethod
    def normalise_provider(cls, v: str) -> str:
        """Normalise provider name to lowercase."""
        return v.strip().lower()

    @model_validator(mode="after")
    def validate_messages_have_user_turn(self) -> "ChatRequest":
        """Ensure at least one user message is present."""
        roles = [m.role for m in self.messages]
        if MessageRole.USER not in roles and "user" not in roles:
            raise ValueError("At least one message with role='user' is required.")
        return self

    model_config = {"use_enum_values": True}


# ─────────────────────────────────────────────────────────────────────────────
# Response
# ─────────────────────────────────────────────────────────────────────────────

class TokenUsage(BaseModel):
    """Token consumption details returned by the provider."""

    prompt_tokens: Optional[int] = Field(default=None, description="Tokens in the prompt.")
    completion_tokens: Optional[int] = Field(default=None, description="Tokens in the completion.")
    total_tokens: Optional[int] = Field(default=None, description="Total tokens consumed.")

    model_config = {"extra": "allow"}  # Allow provider-specific fields


class ChatResponse(BaseModel):
    """
    Response returned by the Gateway after a successful LLM call.

    ``latency_ms`` is the wall-clock time from request receipt to
    provider response — measured by GatewayService.
    """

    request_id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for this request/response pair.",
    )
    provider: str = Field(..., description="Provider that served the request.")
    model: str = Field(..., description="Model that generated the response.")
    response: str = Field(..., description="The model's text response.")
    usage: TokenUsage = Field(
        default_factory=TokenUsage,
        description="Token usage reported by the provider.",
    )
    latency_ms: float = Field(
        ...,
        description="End-to-end latency in milliseconds (gateway wall-clock).",
    )
    finish_reason: Optional[str] = Field(
        default=None,
        description="Why the model stopped generating (stop | length | content_filter).",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Provider & Model Info (for list endpoints)
# ─────────────────────────────────────────────────────────────────────────────

class ModelInfo(BaseModel):
    """Metadata about a single model offered by a provider."""

    id: str = Field(..., description="Model identifier (as used in ChatRequest.model).")
    name: str = Field(..., description="Human-readable model name.")
    context_window: Optional[int] = Field(
        default=None,
        description="Maximum context window size in tokens.",
    )
    supports_streaming: bool = Field(default=True)
    supports_system_prompt: bool = Field(default=True)


class ProviderInfo(BaseModel):
    """Summary of a registered provider returned by GET /api/v1/providers."""

    name: str = Field(..., description="Provider slug (e.g. openai).")
    display_name: str = Field(..., description="Human-readable provider name.")
    status: ProviderStatus = Field(..., description="Current health status.")
    models: List[str] = Field(
        default_factory=list,
        description="Model IDs supported by this provider.",
    )
    configured: bool = Field(
        default=False,
        description="True if the provider's API key/URL is present in settings.",
    )

    model_config = {"use_enum_values": True}


class ProvidersResponse(BaseModel):
    """Response body for GET /api/v1/providers."""

    providers: List[ProviderInfo]
    total: int = Field(..., description="Total number of registered providers.")


class ModelsResponse(BaseModel):
    """Response body for GET /api/v1/models."""

    models: List[ModelInfo]
    total: int = Field(..., description="Total number of models across all providers.")


# ─────────────────────────────────────────────────────────────────────────────
# Error response (used by error-handler middleware)
# ─────────────────────────────────────────────────────────────────────────────

class ErrorDetail(BaseModel):
    """Standard error envelope returned on non-2xx responses."""

    code: str = Field(..., description="Machine-readable error code.")
    message: str = Field(..., description="Human-readable error description.")
    provider: Optional[str] = Field(default=None)
    model: Optional[str] = Field(default=None)
