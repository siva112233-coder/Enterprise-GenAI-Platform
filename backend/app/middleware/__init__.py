"""
Middleware package — custom ASGI middleware components.

Available middleware:
- ``RequestLoggingMiddleware`` (app.middleware.logging): Structured request/response logging.

Planned middleware (future modules):
- ``RateLimitingMiddleware``: Per-user/per-route request rate limiting.
- ``TelemetryMiddleware``: OpenTelemetry trace propagation and span injection.
- ``AuthenticationMiddleware``: JWT validation and principal extraction.
"""
