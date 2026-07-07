"""
Custom Exceptions for the Enterprise GenAI Platform.
"""

class BasePlatformException(Exception):
    """Base exception for all platform services."""
    def __init__(self, message: str, code: str = "INTERNAL_SERVER_ERROR", status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class GatewayException(BasePlatformException):
    """Exceptions originating in the Gateway service."""
    def __init__(self, message: str, code: str = "GATEWAY_ERROR", status_code: int = 502):
        super().__init__(message, code, status_code)


class AgentException(BasePlatformException):
    """Exceptions originating in the LangGraph agent service."""
    def __init__(self, message: str, code: str = "AGENT_EXECUTION_ERROR", status_code: int = 500):
        super().__init__(message, code, status_code)


class ValidationException(BasePlatformException):
    """Exception raised when validation fails."""
    def __init__(self, message: str, code: str = "VALIDATION_ERROR", status_code: int = 422):
        super().__init__(message, code, status_code)
