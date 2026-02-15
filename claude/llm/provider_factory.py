"""Factory for creating LLM provider instances."""

from config.models import get_model_config
from llm.anthropic_provider import AnthropicProvider
from llm.base_provider import BaseLLMProvider
from llm.google_provider import GoogleProvider
from llm.openai_provider import OpenAIProvider

_PROVIDER_MAP = {
    "OpenAI": OpenAIProvider,
    "Anthropic": AnthropicProvider,
    "Google": GoogleProvider,
}


def create_provider(
    company: str, model_name: str, api_key: str
) -> BaseLLMProvider:
    """Create the appropriate LLM provider instance."""
    model_config = get_model_config(company, model_name)
    provider_class = _PROVIDER_MAP[company]
    return provider_class(
        api_key=api_key,
        model_id=model_config.model_id,
        context_window=model_config.context_window,
        output_limit=model_config.output_limit,
    )
