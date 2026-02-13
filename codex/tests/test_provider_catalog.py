from sitebooker.schemas import Provider
from sitebooker.services.provider_catalog import get_models


def test_provider_models_exist() -> None:
    assert get_models(Provider.openai)
    assert get_models(Provider.anthropic)
    assert get_models(Provider.google)
