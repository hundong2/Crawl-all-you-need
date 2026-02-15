"""Anthropic LLM provider (Claude Sonnet 4.5, Claude Haiku 3.5)."""

import anthropic

from llm.base_provider import BaseLLMProvider, LLMResponse


class AnthropicProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str,
        model_id: str,
        context_window: int,
        output_limit: int,
    ) -> None:
        super().__init__(api_key, model_id, context_window, output_limit)
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        def _call() -> LLMResponse:
            response = self.client.messages.create(
                model=self.model_id,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                max_tokens=max_tokens or self.output_limit,
                temperature=0.3,
            )
            return LLMResponse(
                content=response.content[0].text,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                model=response.model,
            )

        return self._retry_with_backoff(
            _call,
            is_rate_limit=lambda e: isinstance(e, anthropic.RateLimitError),
        )

    def validate_api_key(self) -> bool:
        try:
            self.client.messages.create(
                model=self.model_id,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
            )
            return True
        except anthropic.AuthenticationError:
            return False
        except (anthropic.RateLimitError, anthropic.APIConnectionError):
            return True  # Non-auth API errors mean the key itself is valid
        except anthropic.APIStatusError:
            return False
