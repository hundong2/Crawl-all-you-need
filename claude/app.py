"""Entry point for the Site-to-Document Generator."""

import logging

import gradio as gr

from ui.gradio_app import create_ui

# Suppress Gradio's debug-level event logging to prevent API keys
# from being written to log files (Gradio logs all callback inputs at DEBUG level)
logging.getLogger("gradio").setLevel(logging.WARNING)


def main():
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        theme=gr.themes.Soft(),
    )


if __name__ == "__main__":
    main()
