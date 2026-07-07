from enum import Enum


class UserRole(str, Enum):
    """Roles for platform users defining authorization levels."""
    ADMIN = "ADMIN"
    DEVELOPER = "DEVELOPER"
    VIEWER = "VIEWER"


class UserStatus(str, Enum):
    """Account status for users restricting or permitting access."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
