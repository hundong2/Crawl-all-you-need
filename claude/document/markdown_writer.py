"""Assembles the final merged markdown document."""

from datetime import datetime


class MarkdownWriter:
    def write(
        self,
        sections: list,
        site_url: str,
        toc: str,
        provider: str = "",
        page_count: int = 0,
        generation_time: float = 0.0,
    ) -> str:
        """Generate the final merged markdown document."""
        lines = []

        # Source URL as hidden comment
        lines.append(f"<!-- Source: {site_url} -->")

        # Document header
        lines.append(f"# Documentation: {site_url}")
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        meta_parts = [f"Generated on {now}"]
        if provider:
            meta_parts.append(f"Provider: {provider}")
        if page_count > 0:
            meta_parts.append(f"Pages crawled: {page_count}")
        if generation_time > 0:
            meta_parts.append(f"Generation time: {generation_time:.1f}s")
        lines.append(f"\n_{' | '.join(meta_parts)}_\n")

        # Table of Contents
        lines.append("## Table of Contents\n")
        lines.append(toc)
        lines.append("\n---\n")

        # Content sections (skip empty)
        for section in sections:
            if section.content and section.content.strip():
                lines.append(section.content)
                lines.append("\n---\n")

        return "\n".join(lines)

    def save(self, content: str, output_path: str) -> str:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path
