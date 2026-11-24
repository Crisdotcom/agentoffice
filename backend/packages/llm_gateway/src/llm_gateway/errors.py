class LLMError(Exception):
    """Base error for llm_gateway."""


class AuthenticationError(LLMError):
    """The API key was rejected by the provider."""


class RateLimitError(LLMError):
    """The provider rate-limited the request; safe to retry with backoff."""


class ProviderError(LLMError):
    """Any other provider-side failure."""
