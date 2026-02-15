"""Global settings and provider/model configuration."""

API_KEY_ENV_VARS = {
    "OpenAI": "OPENAI_API_KEY",
    "Anthropic": "ANTHROPIC_API_KEY",
    "Google": "GEMINI_API_KEY",
}

PROVIDERS = {
    "OpenAI": {
        "models": {
            "GPT-4o": {
                "id": "gpt-4o",
                "context_window": 128000,
                "output_limit": 16384,
            },
            "GPT-4o-mini": {
                "id": "gpt-4o-mini",
                "context_window": 128000,
                "output_limit": 16384,
            },
        }
    },
    "Anthropic": {
        "models": {
            "Claude Sonnet 4.5": {
                "id": "claude-sonnet-4-5-20250929",
                "context_window": 200000,
                "output_limit": 8192,
            },
            "Claude Haiku 3.5": {
                "id": "claude-3-5-haiku-20241022",
                "context_window": 200000,
                "output_limit": 8192,
            },
        }
    },
    "Google": {
        "models": {
            "Gemini 2.0 Flash": {
                "id": "gemini-2.0-flash",
                "context_window": 1048576,
                "output_limit": 8192,
            },
            "Gemini 1.5 Pro": {
                "id": "gemini-1.5-pro",
                "context_window": 2097152,
                "output_limit": 8192,
            },
        }
    },
}

# Crawl defaults
DEFAULT_MAX_DEPTH = 3
DEFAULT_MAX_PAGES = 100
DEFAULT_DELAY = 0.5
DEFAULT_TIMEOUT = 60000

# Chunking
SAFETY_MARGIN_RATIO = 0.8
