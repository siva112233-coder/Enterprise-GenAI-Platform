"""
Domain exception hierarchy for the Enterprise GenAI Platform.

Decouples business logic from HTTP transport concerns.
"""


class DomainError(Exception):
    """Base class for all domain exceptions."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ResourceNotFoundError(DomainError):
    """Raised when a requested resource (e.g. User, Organization) is not found."""

    pass


class DuplicateResourceError(DomainError):
    """Raised when creating a resource would violate a unique constraint."""

    pass


class ValidationError(DomainError):
    """Raised when business logic validation rules are violated."""

    pass


class ForbiddenError(DomainError):
    """Raised when the current user does not have permissions for the action."""

    pass
