"""Entry point for the Site-to-Document Generator."""

import gradio as gr

from ui.gradio_app import create_ui


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
