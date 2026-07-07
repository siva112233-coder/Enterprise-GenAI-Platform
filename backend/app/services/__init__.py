"""
Services package — business logic layer for the Enterprise GenAI Platform.

PURPOSE
-------
Services implement the application's business rules and orchestrate interactions
between repositories, external APIs, and domain events.

Services must:
- Accept dependencies (repositories, settings) via constructor injection.
- Contain NO FastAPI-specific code (no Request, Response, Depends).
- Raise domain exceptions, NOT HTTPException (translation happens in routes).
- Be independently testable without an ASGI server.

CONVENTIONS
-----------
1. One service class per bounded context (e.g., AuthService, ProviderService).
2. Services are stateless — all mutable state lives in the database.
3. Complex multi-step operations use database transactions managed at the
   service layer (not the repository or route layer).

STRUCTURE (to be added in future modules)
-----------------------------------------
    services/
        auth.py          — AuthService: token issuance, credential validation
        provider.py      — LLMProviderService: provider registry and routing
        agent.py         — AgentService: LangGraph workflow orchestration
        monitoring.py    — CostMonitoringService: usage tracking and alerting
        ...

EXAMPLE (future implementation pattern)
-----------------------------------------
    from app.repositories.user import UserRepository
    from app.schemas.auth import TokenPair
    from app.utils.exceptions import InvalidCredentialsError

    class AuthService:
        def __init__(self, user_repo: UserRepository) -> None:
            self._user_repo = user_repo

        async def authenticate(self, email: str, password: str) -> TokenPair:
            user = await self._user_repo.get_by_email(email)
            if user is None or not user.verify_password(password):
                raise InvalidCredentialsError("Invalid email or password.")
            return self._issue_tokens(user)
"""
