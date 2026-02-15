"""Google LLM provider (Gemini 2.0 Flash, Gemini 1.5 Pro)."""

from google import genai
from google.genai import types

from llm.base_provider import BaseLLMProvider, LLMResponse


def _is_google_rate_limit(exc: Exception) -> bool:
    """Check if the exception is a Google API rate-limit / quota error."""
    err_str = str(exc)
    return "429" in err_str or "RESOURCE_EXHAUSTED" in err_str


class GoogleProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str,
        model_id: str,
        context_window: int,
        output_limit: int,
    ) -> None:
        super().__init__(api_key, model_id, context_window, output_limit)
        self.client = genai.Client(api_key=api_key)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        def _call() -> LLMResponse:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=max_tokens or self.output_limit,
                    temperature=0.3,
                ),
            )
            usage = response.usage_metadata
            return LLMResponse(
                content=response.text or "",
                input_tokens=usage.prompt_token_count if usage else 0,
                output_tokens=usage.candidates_token_count if usage else 0,
                model=self.model_id,
            )

        return self._retry_with_backoff(_call, is_rate_limit=_is_google_rate_limit)

    def validate_api_key(self) -> bool:
        try:
            self.client.models.generate_content(
                model=self.model_id,
                contents="ping",
                config=types.GenerateContentConfig(max_output_tokens=5),
            )
            return True
        except Exception as e:
            if _is_google_rate_limit(e):
                return True
            return False
