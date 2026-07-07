"""
Security package — authentication and authorisation utilities.

PURPOSE
-------
This package will house all security-critical components:
- Password hashing and verification (bcrypt via passlib)
- JWT token issuance, validation, and revocation
- Role-based access control (RBAC) guards
- API key management (hashing, rotation, scopes)
- OAuth2 flow helpers

IMPORTANT: No security logic is implemented in Module 1A.
Authentication and authorisation are out of scope for the backend foundation.
These components will be added in a dedicated security module.

SECURITY PRINCIPLES (to be followed when implementing)
-------------------------------------------------------
1. Passwords are NEVER stored in plaintext — always bcrypt-hashed.
2. JWTs are short-lived (default: 30 min) and signed with HS256 or RS256.
3. Refresh tokens are stored server-side (database) to support revocation.
4. All sensitive values (SECRET_KEY, DB passwords) come from environment
   variables or a secrets manager — never hardcoded.
5. Use ``secrets.compare_digest()`` for all string comparisons that could
   be vulnerable to timing attacks.
6. Rate-limit all authentication endpoints to prevent brute-force attacks.

STRUCTURE (to be added in future security module)
-------------------------------------------------
    security/
        password.py      — PasswordHasher (bcrypt via passlib)
        jwt.py           — TokenService: issue, verify, revoke JWTs
        dependencies.py  — get_current_user, require_role FastAPI dependencies
        api_keys.py      — APIKeyManager: hash, validate, rotate API keys
        ...
"""
