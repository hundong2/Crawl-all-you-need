"""UI event handlers for the Gradio interface."""

import os
import re

import gradio as gr

from config.models import get_models_for_company
from config.settings import API_KEY_ENV_VARS
from pipeline.orchestrator import PipelineOrchestrator

# Global reference for cancel support
_current_orchestrator: PipelineOrchestrator | None = None


def get_api_key_from_env(company: str) -> str:
    """Read API key from environment variable for the given company."""
    env_var = API_KEY_ENV_VARS.get(company, "")
    return os.environ.get(env_var, "")


def update_on_company_change(company: str):
    """Update model dropdown and API key when company changes."""
    models = get_models_for_company(company)
    api_key = get_api_key_from_env(company)
    return (
        gr.Dropdown(choices=models, value=models[0] if models else None),
        gr.Textbox(value=api_key),
    )


def _is_valid_url(url: str) -> bool:
    """Basic URL validation: must have a valid domain structure."""
    pattern = r"^https?://[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+"
    return bool(re.match(pattern, url))


def run_pipeline(
    company, model_name, api_key, site_url, output_format, max_depth, max_pages
):
    """
    Generator that yields (progress_log, file_or_none) tuples.
    Gradio updates outputs on each yield.
    """
    global _current_orchestrator

    # Validate inputs
    if not api_key or not api_key.strip():
        yield "ERROR: Please enter your API key.", None
        return
    if not site_url or not site_url.strip():
        yield "ERROR: Please enter a site URL.", None
        return
    if not site_url.startswith(("http://", "https://")):
        site_url = "https://" + site_url
    if not _is_valid_url(site_url.strip()):
        yield "ERROR: Invalid URL format. Please enter a valid domain (e.g. https://example.com).", None
        return

    orchestrator = PipelineOrchestrator(
        company=company,
        model_name=model_name,
        api_key=api_key.strip(),
        site_url=site_url.strip(),
        output_format=output_format,
        max_depth=int(max_depth),
        max_pages=int(max_pages),
    )
    _current_orchestrator = orchestrator

    log_lines = []
    try:
        for progress_msg, output_file in orchestrator.run():
            log_lines.append(progress_msg)
            log_text = "\n".join(log_lines)
            yield log_text, output_file if output_file else gr.skip()
    except Exception as e:
        log_lines.append(f"ERROR: Unexpected error ({e}). Please try again.")
        yield "\n".join(log_lines), None
    finally:
        _current_orchestrator = None


def cancel_pipeline():
    """Cancel the running pipeline."""
    global _current_orchestrator
    if _current_orchestrator:
        _current_orchestrator.cancel()
        return "Cancelling... waiting for current API call to finish."
    return "No pipeline running."
