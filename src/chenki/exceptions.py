class ChenkiError(Exception):
    """Base exception for all chenki errors."""


class ChenkiTimeout(ChenkiError):
    """Raised when a request to chenki-llm exceeds the configured timeout."""


class ChenkiServerError(ChenkiError):
    """Raised when chenki-llm returns a 5xx response."""


class ChenkiRateLimited(ChenkiError):
    """Raised when chenki-llm returns a 429 response."""


class ChenkiParseError(ChenkiError):
    """Raised when a structured-output helper cannot parse the LLM response."""

    def __init__(self, message: str = "", *, raw: str = "") -> None:
        super().__init__(message or f"could not parse LLM output: {raw[:200]!r}")
        self.raw = raw
