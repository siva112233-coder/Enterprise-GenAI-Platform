"""
POST /api/v1/chat — LLM chat completion endpoint.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_gateway_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.gateway_service import GatewayService

router = APIRouter(tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit a chat completion request",
    description=(
        "Routes the request to the specified LLM provider and returns the "
        "model's response.  Set ``stream=true`` to receive a streaming response "
        "(Server-Sent Events — not yet implemented in this foundational release)."
    ),
    responses={
        200: {"description": "Successful chat completion"},
        400: {"description": "Invalid model for the requested provider"},
        404: {"description": "Provider not found"},
        501: {"description": "Provider API integration not yet implemented"},
        503: {"description": "Provider currently unavailable"},
    },
)
async def chat_completion(
    request: ChatRequest,
    service: Annotated[GatewayService, Depends(get_gateway_service)],
) -> ChatResponse:
    """
    Submit a chat completion to the specified LLM provider.

    **Provider slugs**: ``openai`` | ``claude`` | ``gemini`` | ``deepseek`` | ``groq`` | ``ollama``

    **Streaming**: set ``stream: true`` in the request body.
    The current foundational implementation returns ``501`` for streaming
    until provider streaming is wired in.

    **Example request**:
    ```json
    {
        "provider": "openai",
        "model": "gpt-4o",
        "messages": [
            {"role": "user", "content": "Explain quantum entanglement in one sentence."}
        ],
        "temperature": 0.7
    }
    ```
    """
    if request.stream:
        # Streaming endpoint stub — returns 501 until provider streaming is implemented
        from fastapi import HTTPException
        raise HTTPException(
            status_code=501,
            detail={
                "code": "STREAMING_NOT_IMPLEMENTED",
                "message": (
                    "Streaming is not yet wired in this foundational release. "
                    "Set stream=false to use the synchronous endpoint."
                ),
            },
        )

    return await service.process_chat(request)
