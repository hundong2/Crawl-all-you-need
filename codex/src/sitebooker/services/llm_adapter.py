from __future__ import annotations

from sitebooker.config.env_loader import AppSecrets
from sitebooker.schemas import Provider


def _full_model_name(provider: Provider, model: str) -> str:
    if provider is Provider.openai:
        return f"openai/{model}"
    if provider is Provider.anthropic:
        return f"anthropic/{model}"
    if provider is Provider.google:
        return f"gemini/{model}"
    return model


def _has_provider_key(provider: Provider, secrets: AppSecrets) -> bool:
    if provider is Provider.openai:
        return bool(secrets.openai_api_key)
    if provider is Provider.anthropic:
        return bool(secrets.anthropic_api_key)
    if provider is Provider.google:
        return bool(secrets.gemini_api_key)
    return False


def refine_markdown(markdown: str, provider: Provider, model: str, secrets: AppSecrets) -> str:
    """Apply optional cleanup using configured LLM provider via LiteLLM.

    If credentials are missing or request fails, return original markdown.
    """
    if not markdown.strip() or not _has_provider_key(provider, secrets):
        return markdown

    try:
        from litellm import completion
    except Exception:
        return markdown

    prompt = (
        "You are a technical editor. Preserve facts and code blocks. "
        "Remove duplicated paragraphs, improve section ordering, and keep markdown output only."
    )

    try:
        response = completion(
            model=_full_model_name(provider, model),
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": markdown[:120000]},
            ],
            temperature=0,
        )
        content = response.choices[0].message.content
        return content.strip() if content else markdown
    except Exception:
        return markdown
