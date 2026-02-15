"""Gradio interface definition."""

import gradio as gr

from config.models import get_companies, get_models_for_company
from ui.callbacks import (
    cancel_pipeline,
    get_api_key_from_env,
    run_pipeline,
    update_on_company_change,
)


def create_ui() -> gr.Blocks:
    companies = get_companies()
    default_company = companies[0]
    default_models = get_models_for_company(default_company)

    with gr.Blocks(
        title="Site-to-Document Generator",
    ) as demo:
        gr.Markdown(
            "# Site-to-Document Generator\n"
            "Crawl a website and generate a consolidated document using AI."
        )

        with gr.Row():
            # Left column: controls
            with gr.Column(scale=1):
                company_dropdown = gr.Dropdown(
                    choices=companies,
                    label="AI Provider",
                    info="Select the LLM provider to use for content processing",
                    value=default_company,
                )
                model_dropdown = gr.Dropdown(
                    choices=default_models,
                    label="Model",
                    info="Choose a model from the selected provider",
                    value=default_models[0] if default_models else None,
                )
                api_key_input = gr.Textbox(
                    label="API Key",
                    type="password",
                    placeholder="Enter your API key or set env var...",
                    info="Auto-filled from environment variable if available",
                    value=get_api_key_from_env(default_company),
                )
                site_url_input = gr.Textbox(
                    label="Site URL",
                    placeholder="https://example.com/docs",
                    info="The root URL to start crawling from",
                )
                output_format = gr.Radio(
                    choices=["Markdown", "PDF"],
                    label="Output Format",
                    info="Markdown is lightweight; PDF includes styled formatting",
                    value="Markdown",
                )

                with gr.Accordion("Advanced Settings", open=True):
                    max_depth_slider = gr.Slider(
                        minimum=1,
                        maximum=5,
                        step=1,
                        value=3,
                        label="Max Crawl Depth",
                        info="1 = start page only, 2 = start + direct links, etc.",
                    )
                    max_pages_slider = gr.Slider(
                        minimum=10,
                        maximum=500,
                        step=10,
                        value=100,
                        label="Max Pages",
                        info="Maximum number of pages to crawl",
                    )

                with gr.Row():
                    start_btn = gr.Button("Start", variant="primary")
                    cancel_btn = gr.Button("Cancel", variant="stop")

            # Right column: output
            with gr.Column(scale=2):
                progress_display = gr.Textbox(
                    label="Progress",
                    lines=20,
                    max_lines=30,
                    interactive=False,
                    autoscroll=True,
                )
                download_output = gr.File(label="Download Output")

        # Event bindings
        company_dropdown.change(
            fn=update_on_company_change,
            inputs=[company_dropdown],
            outputs=[model_dropdown, api_key_input],
        )

        start_btn.click(
            fn=run_pipeline,
            inputs=[
                company_dropdown,
                model_dropdown,
                api_key_input,
                site_url_input,
                output_format,
                max_depth_slider,
                max_pages_slider,
            ],
            outputs=[progress_display, download_output],
        )

        cancel_btn.click(
            fn=cancel_pipeline,
            inputs=[],
            outputs=[progress_display],
        )

    return demo
