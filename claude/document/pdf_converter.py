"""Markdown to PDF conversion using markdown2 + weasyprint."""

import markdown2
from weasyprint import HTML

PDF_CSS = """\
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');

body {
    font-family: 'Noto Sans KR', 'Noto Sans', 'AppleGothic', 'Malgun Gothic', 'Arial', sans-serif;
    line-height: 1.6;
    margin: 2cm;
    color: #1a1a1a;
}
h1 {
    color: #1a1a2e;
    border-bottom: 2px solid #16213e;
    padding-bottom: 8px;
    page-break-before: always;
}
h1:first-of-type { page-break-before: avoid; }
h2 { color: #16213e; margin-top: 2em; }
h3 { color: #0f3460; }
code {
    background: #f0f0f0;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 0.85em;
}
pre {
    background: #282c34;
    color: #abb2bf;
    padding: 16px;
    border-radius: 8px;
    overflow-x: auto;
    border-left: 4px solid #61afef;
    font-size: 0.85em;
    line-height: 1.5;
}
pre code {
    background: none;
    padding: 0;
    color: inherit;
    font-family: 'Courier New', 'Consolas', monospace;
}
blockquote {
    border-left: 4px solid #e94560;
    padding-left: 16px;
    color: #555;
}
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
th { background: #f5f5f5; }
a { color: #0f3460; }
hr { border: none; border-top: 1px solid #ddd; margin: 2em 0; }
@page { margin: 2cm; @bottom-center { content: counter(page); } }
"""


class PDFConverter:
    def convert(self, markdown_content: str, output_path: str) -> str:
        """Convert markdown string to PDF file."""
        html_content = markdown2.markdown(
            markdown_content,
            extras=[
                "fenced-code-blocks",
                "tables",
                "header-ids",
                "code-friendly",
                "cuddled-lists",
            ],
        )
        full_html = (
            "<!DOCTYPE html><html><head>"
            '<meta charset="utf-8">'
            f"<style>{PDF_CSS}</style>"
            f"</head><body>{html_content}</body></html>"
        )
        HTML(string=full_html).write_pdf(output_path)
        return output_path
