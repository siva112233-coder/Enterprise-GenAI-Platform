"""
Shared Request/Response Models for the Enterprise GenAI Platform.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Standard health check response model."""
    status: str = "healthy"
    service: str
    version: str = "0.1.0"


class LLMRequest(BaseModel):
    """Standard payload model for LLM requests passing through the Gateway."""
    provider: str = Field(..., description="Target LLM Provider (e.g. openai, gemini)")
    model: str = Field(..., description="Target model name")
    prompt: str = Field(..., description="Input prompt for the model")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, description="Max response tokens")
    stream: Optional[bool] = Field(False, description="Whether to stream response")


class LLMResponse(BaseModel):
    """Standard response model for LLM requests."""
    provider: str
    model: str
    content: str
    usage: Dict[str, Any] = Field(default_factory=dict, description="Token usage details")
