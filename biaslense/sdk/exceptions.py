"""Custom exceptions for BiasLens SDK."""


class BamiPException(Exception):
    """Base exception for all BiasLens SDK errors."""

    pass


class ValidationException(BamiPException):
    """Raised when request validation fails (e.g., empty prompt)."""

    pass


class ConnectionException(BamiPException):
    """Raised when unable to connect to remote API endpoint."""

    pass


class RateLimitException(BamiPException):
    """Raised when rate limit is exceeded.

    The SDK will automatically retry with exponential backoff.
    If you get this exception, consider waiting before retrying
    or using a local endpoint instead.
    """

    pass


class ServerException(BamiPException):
    """Raised when remote server returns a 5xx error."""

    pass
