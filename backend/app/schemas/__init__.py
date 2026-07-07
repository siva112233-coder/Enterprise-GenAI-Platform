"""
Schemas package — Pydantic request/response models for the Enterprise GenAI Platform.

PURPOSE
-------
Schemas define the contract between the API surface and clients.
They handle:
- Request validation and coercion (FastAPI request bodies, query params)
- Response serialisation (what clients receive)
- OpenAPI documentation generation

Schemas are NEVER ORM models. The separation prevents accidental
exposure of internal database fields (e.g., hashed passwords, internal IDs).

CONVENTIONS
-----------
1. Each schema file corresponds to one resource domain.
2. Use a ``Base`` / ``Create`` / ``Update`` / ``Response`` inheritance pattern:
   - ``UserBase``: Shared fields (validated on both in and out)
   - ``UserCreate``: Request body for POST /users (includes password)
   - ``UserUpdate``: Request body for PATCH /users/{id} (all optional)
   - ``UserResponse``: Response model (excludes sensitive fields)
3. All Response schemas set ``model_config = ConfigDict(from_attributes=True)``
   to support ORM-to-schema conversion via ``model_validate(orm_obj)``.
4. Use ``Annotated`` for reusable field constraints.

STRUCTURE (to be added in future modules)
-----------------------------------------
    schemas/
        common.py        — Shared schemas: PaginatedResponse, ErrorResponse, etc.
        auth.py          — LoginRequest, TokenPair, RefreshRequest
        user.py          — UserCreate, UserUpdate, UserResponse
        provider.py      — ProviderCreate, ProviderResponse
        ...

EXAMPLE (future implementation pattern)
-----------------------------------------
    from pydantic import BaseModel, ConfigDict, EmailStr
    from datetime import datetime

    class UserBase(BaseModel):
        email: EmailStr
        full_name: str

    class UserCreate(UserBase):
        password: str  # Raw password — hashed at the service layer

    class UserResponse(UserBase):
        id: int
        created_at: datetime

        model_config = ConfigDict(from_attributes=True)
"""
