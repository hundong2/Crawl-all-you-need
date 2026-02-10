from __future__ import annotations

from sitebooker.schemas import Provider

MODEL_CATALOG: dict[Provider, list[str]] = {
    Provider.openai: [
        "gpt-4.1-mini",
        "gpt-4.1",
        "gpt-5-mini",
    ],
    Provider.anthropic: [
        "claude-3-5-haiku-latest",
        "claude-3-7-sonnet-latest",
    ],
    Provider.google: [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash",
    ],
}


def get_models(provider: Provider) -> list[str]:
    return MODEL_CATALOG.get(provider, [])
