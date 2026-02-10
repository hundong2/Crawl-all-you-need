from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values


@dataclass(frozen=True)
class AppSecrets:
    openai_api_key: str | None
    anthropic_api_key: str | None
    gemini_api_key: str | None


REQUIRED_RUNTIME_KEYS = ("UV_HOST", "UV_PORT")
BLOCKED_DOTENV_KEYS = {
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
}


def load_environment(dotenv_path: str = ".env") -> None:
    """Load non-secret runtime vars from .env without overriding OS env vars."""
    env_file = Path(dotenv_path)
    if not env_file.exists():
        return

    parsed = dotenv_values(env_file)
    for key, value in parsed.items():
        if not key or value is None:
            continue
        if key in BLOCKED_DOTENV_KEYS:
            continue
        if key not in os.environ:
            os.environ[key] = value


def _require_key(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment key: {name}")
    return value


def load_runtime_settings() -> tuple[str, int]:
    """Return validated host/port with secure defaults."""
    host = _require_key("UV_HOST", "127.0.0.1")
    raw_port = _require_key("UV_PORT", "8000")
    try:
        port = int(raw_port)
    except ValueError as exc:
        raise RuntimeError("UV_PORT must be an integer") from exc
    return host, port


def load_secrets() -> AppSecrets:
    """Centralized secret access for provider auth keys."""
    return AppSecrets(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
    )
