"""
Utils package — shared utilities for the Enterprise GenAI Platform.

Contains cross-cutting helper utilities that are too small to warrant
their own package but are used across multiple application layers.

STRUCTURE (to be added as needed)
----------------------------------
    utils/
        exceptions.py    — Domain exception hierarchy (not HTTP exceptions)
        pagination.py    — PaginationParams, paginate() helper
        datetime.py      — UTC-aware datetime helpers
        hashing.py       — General-purpose hashing utilities
        ...

DOMAIN EXCEPTIONS (planned in exceptions.py)
--------------------------------------------
Domain exceptions decouple business logic from transport concerns:
- Services raise domain exceptions (e.g., ``ResourceNotFoundError``)
- Route handlers catch them and translate to HTTPException with status codes
- This prevents HTTPException from leaking into the service/repository layers

EXAMPLE (future implementation pattern)
-----------------------------------------
    class AppBaseError(Exception):
        \"\"\"Base class for all application domain exceptions.\"\"\"
        ...

    class ResourceNotFoundError(AppBaseError):
        \"\"\"Raised when a requested resource does not exist.\"\"\"
        ...

    class DuplicateResourceError(AppBaseError):
        \"\"\"Raised when a unique constraint would be violated.\"\"\"
        ...

    class InvalidCredentialsError(AppBaseError):
        \"\"\"Raised when authentication credentials are invalid.\"\"\"
        ...
"""
