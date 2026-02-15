"""Abstract base class for LLM providers."""

import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class LLMResponse:
    content: str
    input_tokens: int
    output_tokens: int
    model: str


def _extract_retry_delay(exc: Exception) -> float | None:
    """Try to extract a suggested retry delay (in seconds) from an exception."""
    err_str = str(exc)
    match = re.search(r"retry(?:Delay|_delay|In)[\"']?\s*[:=]\s*[\"']?(\d+(?:\.\d+)?)\s*s", err_str, re.IGNORECASE)
    if match:
        return float(match.group(1))
    match = re.search(r"Please retry in (\d+(?:\.\d+)?)\s*s", err_str)
    if match:
        return float(match.group(1))
    return None


class ProviderCancelledError(Exception):
    """Raised when an LLM operation is cancelled."""


class BaseLLMProvider(ABC):
    """Unified interface for all LLM providers."""

    MAX_RETRIES: int = 5

    def __init__(
        self,
        api_key: str,
        model_id: str,
        context_window: int,
        output_limit: int,
    ) -> None:
        self.api_key = api_key
        self.model_id = model_id
        self.context_window = context_window
        self.output_limit = output_limit
        self._cancel_requested = False

    def request_cancel(self):
        """Signal that pending/future operations should abort promptly."""
        self._cancel_requested = True

    def _check_cancel(self):
        if self._cancel_requested:
            raise ProviderCancelledError("Operation cancelled by user")

    def _cancellable_sleep(self, seconds: float):
        """Sleep in 1-second increments, checking for cancel each iteration."""
        remaining = seconds
        while remaining > 0:
            self._check_cancel()
            step = min(1.0, remaining)
            time.sleep(step)
            remaining -= step

    def _retry_with_backoff(
        self,
        fn: Callable[[], T],
        is_rate_limit: Callable[[Exception], bool],
    ) -> T:
        """Retry fn() with exponential backoff on rate-limit errors.

        Args:
            fn: Zero-arg callable to attempt.
            is_rate_limit: Predicate that returns True when the exception
                           is a rate-limit / quota error worth retrying.

        Returns:
            The value returned by fn().

        Raises:
            The last exception if all retries are exhausted, or any
            non-rate-limit exception immediately.
        """
        last_exc: Exception | None = None
        for attempt in range(self.MAX_RETRIES):
            self._check_cancel()
            try:
                return fn()
            except ProviderCancelledError:
                raise
            except Exception as exc:
                last_exc = exc
                is_last_attempt = attempt >= self.MAX_RETRIES - 1
                if is_rate_limit(exc) and not is_last_attempt:
                    # Use API-suggested delay if available, otherwise exponential backoff
                    suggested = _extract_retry_delay(exc)
                    wait = min(suggested or (2 ** (attempt + 2)), 120)
                    logger.warning(
                        "Rate-limited (attempt %d/%d), retrying in %ds...",
                        attempt + 1,
                        self.MAX_RETRIES,
                        wait,
                    )
                    self._cancellable_sleep(wait)
                    continue
                raise
        # Should be unreachable, but satisfies the type checker.
        raise last_exc  # type: ignore[misc]

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Send a prompt and return the response."""
        ...

    @abstractmethod
    def validate_api_key(self) -> bool:
        """Verify the API key is valid."""
        ...

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (~4 chars per token)."""
        return len(text) // 4

    def get_max_input_tokens(self) -> int:
        """Usable input tokens with safety margin."""
        return int((self.context_window - self.output_limit) * 0.8)
