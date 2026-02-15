"""OpenAI LLM provider (GPT-4o, GPT-4o-mini)."""

from openai import OpenAI, RateLimitError

from llm.base_provider import BaseLLMProvider, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str,
        model_id: str,
        context_window: int,
        output_limit: int,
    ) -> None:
        super().__init__(api_key, model_id, context_window, output_limit)
        self.client = OpenAI(api_key=api_key)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        def _call() -> LLMResponse:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens or self.output_limit,
                temperature=0.3,
            )
            choice = response.choices[0]
            return LLMResponse(
                content=choice.message.content or "",
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                model=response.model,
            )

        return self._retry_with_backoff(
            _call,
            is_rate_limit=lambda e: isinstance(e, RateLimitError),
        )

    def validate_api_key(self) -> bool:
        try:
            self.client.models.list()
            return True
        except Exception:
            return False
