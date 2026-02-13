from __future__ import annotations

import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable
from uuid import uuid4

from sitebooker.config.env_loader import AppSecrets
from sitebooker.schemas import BuildRequest
from sitebooker.services.crawler import crawl_site
from sitebooker.services.llm_adapter import refine_markdown

ProgressFn = Callable[[int, str], None]


def _safe_slug(url: str) -> str:
    return (
        url.replace("https://", "")
        .replace("http://", "")
        .replace("/", "_")
        .replace(":", "_")
        .replace("?", "_")
    )[:80]


def _assemble_markdown(root_url: str, pages: list[tuple[str, str, str]]) -> str:
    lines = [f"# Book Export for {root_url}", ""]
    lines.append("## Table of Contents")
    for i, (title, url, _) in enumerate(pages, start=1):
        lines.append(f"{i}. [{title}]({url})")

    lines.append("")
    for i, (title, url, content) in enumerate(pages, start=1):
        lines.append(f"## {i}. {title}")
        lines.append("")
        lines.append(f"Source: {url}")
        lines.append("")
        lines.append(content)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _convert_with_pandoc(book_path: Path, fmt: str) -> tuple[bool, str]:
    """Convert markdown into the requested format using pandoc when available."""
    if shutil.which("pandoc") is None:
        return False, "pandoc not installed"

    out_file = book_path.with_suffix(f".{fmt}")
    cmd = ["pandoc", str(book_path), "-o", str(out_file)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True, out_file.name
    except Exception as exc:
        return False, f"pandoc {fmt} conversion failed: {exc}"


async def build_book(
    request: BuildRequest,
    output_dir: str,
    secrets: AppSecrets,
    on_progress: ProgressFn | None = None,
) -> dict[str, object]:
    if on_progress:
        on_progress(5, "Starting build")
    run_id = str(uuid4())
    if on_progress:
        on_progress(20, "Crawling pages")
    crawl_result = await crawl_site(
        root_url=str(request.root_url),
        max_pages=request.max_pages,
        max_depth=request.max_depth,
    )

    pages = [(p.title, p.url, p.markdown) for p in crawl_result.pages]
    if on_progress:
        on_progress(45, "Assembling markdown")
    markdown = _assemble_markdown(str(request.root_url), pages)
    if request.llm_refine:
        if on_progress:
            on_progress(60, "Refining with LLM")
        markdown = refine_markdown(
            markdown=markdown,
            provider=request.provider,
            model=request.model,
            secrets=secrets,
        )

    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_folder = Path(output_dir) / f"{ts}_{_safe_slug(str(request.root_url))}_{run_id[:8]}"
    run_folder.mkdir(parents=True, exist_ok=True)

    book_path = run_folder / "book.md"
    manifest_path = run_folder / "manifest.json"

    if on_progress:
        on_progress(80, "Writing book artifact")
    book_path.write_text(markdown, encoding="utf-8")
    output_files = ["book.md"]
    conversion_notes: list[str] = []
    if on_progress:
        on_progress(88, "Converting requested formats")
    for fmt in request.output_formats:
        if fmt.value == "md":
            continue
        success, info = _convert_with_pandoc(book_path, fmt.value)
        if success:
            output_files.append(info)
        else:
            conversion_notes.append(info)

    manifest = {
        "run_id": run_id,
        "created_at_utc": ts,
        "provider": request.provider.value,
        "model": request.model,
        "root_url": str(request.root_url),
        "pages_collected": len(crawl_result.pages),
        "failures": crawl_result.failures,
        "output_files": output_files,
        "conversion_notes": conversion_notes,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if on_progress:
        on_progress(98, "Finalizing manifest")

    return {
        "run_id": run_id,
        "output_path": str(book_path),
        "manifest_path": str(manifest_path),
        "pages_collected": len(crawl_result.pages),
        "failures": crawl_result.failures + conversion_notes,
        "output_files": output_files,
    }
