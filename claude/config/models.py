"""Model configuration registry with helper functions."""

from dataclasses import dataclass

from config.settings import PROVIDERS


@dataclass
class ModelConfig:
    company: str
    display_name: str
    model_id: str
    context_window: int
    output_limit: int


def get_companies() -> list[str]:
    """Return list of available company names."""
    return list(PROVIDERS.keys())


def get_models_for_company(company: str) -> list[str]:
    """Return list of model display names for a given company."""
    if company not in PROVIDERS:
        return []
    return list(PROVIDERS[company]["models"].keys())


def get_model_config(company: str, model_name: str) -> ModelConfig:
    """Return full ModelConfig for a company + model name pair."""
    info = PROVIDERS[company]["models"][model_name]
    return ModelConfig(
        company=company,
        display_name=model_name,
        model_id=info["id"],
        context_window=info["context_window"],
        output_limit=info["output_limit"],
    )
