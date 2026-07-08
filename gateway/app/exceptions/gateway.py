"""
Gateway-specific exception hierarchy.

All exceptions inherit from ``GatewayException`` which in turn
inherits from the shared ``BasePlatformException``.

HTTP status codes are embedded in each exception so the error-handler
middleware can map them to responses without extra logic.
"""

from shared.exceptions import GatewayException as _BaseGatewayException


class GatewayException(_BaseGatewayException):
    """
    Root exception for the AI Gateway.

    Inherits from the shared base so platform-level handlers can
    catch either the gateway or any other service exception uniformly.
    """

    def __init__(
        self,
        message: str,
        code: str = "GATEWAY_ERROR",
        status_code: int = 502,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code)


class ProviderNotFound(GatewayException):
    """
    Raised when the requested provider name is not registered.

    HTTP 404 — the provider is unknown to this gateway instance.
    """

    def __init__(self, provider: str) -> None:
        super().__init__(
            message=f"Provider '{provider}' is not registered in this gateway.",
            code="PROVIDER_NOT_FOUND",
            status_code=404,
        )
        self.provider = provider


class ProviderUnavailable(GatewayException):
    """
    Raised when a registered provider fails its health check
    or returns an unrecoverable error during a request.

    HTTP 503 — the provider exists but cannot serve traffic.
    """

    def __init__(self, provider: str, reason: str = "") -> None:
        detail = f"Provider '{provider}' is currently unavailable."
        if reason:
            detail += f" Reason: {reason}"
        super().__init__(
            message=detail,
            code="PROVIDER_UNAVAILABLE",
            status_code=503,
        )
        self.provider = provider
        self.reason = reason


class InvalidModel(GatewayException):
    """
    Raised when the requested model is not supported by the provider.

    HTTP 400 — bad request from the caller.
    """

    def __init__(self, provider: str, model: str) -> None:
        super().__init__(
            message=(
                f"Model '{model}' is not supported by provider '{provider}'. "
                "Call GET /api/v1/models to list available models."
            ),
            code="INVALID_MODEL",
            status_code=400,
        )
        self.provider = provider
        self.model = model


class RequestValidationError(GatewayException):
    """
    Raised when the incoming ChatRequest fails business-level validation
    that Pydantic did not catch (e.g. temperature out of provider range).

    HTTP 422 — semantically invalid request.
    """

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(
            message=f"Invalid value for field '{field}': {reason}",
            code="REQUEST_VALIDATION_ERROR",
            status_code=422,
        )
        self.field = field
        self.reason = reason
