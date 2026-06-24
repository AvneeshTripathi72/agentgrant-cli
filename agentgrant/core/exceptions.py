class AgentGrantError(Exception):
    """Base exception for the CLI."""


class ConfigurationError(AgentGrantError):
    """Raised for invalid or missing configuration."""


class AuthenticationError(AgentGrantError):
    """Raised for authentication failures."""


class APIError(AgentGrantError):
    """Raised for API response failures."""


class TokenError(AgentGrantError):
    """Raised for JWT parsing and verification failures."""


class ValidationError(AgentGrantError):
    """Raised for user-facing validation failures."""


class NetworkError(AgentGrantError):
    """Raised for transport failures."""
