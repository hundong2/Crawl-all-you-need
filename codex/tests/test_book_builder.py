import json
from pathlib import Path

import pytest

from sitebooker.config.env_loader import AppSecrets
from sitebooker.schemas import BuildRequest
from sitebooker.services import book_builder
from sitebooker.services.crawler import CrawlResult, CrawledPage


@pytest.mark.asyncio
async def test_build_book_writes_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_crawl_site(root_url: str, max_pages: int, max_depth: int) -> CrawlResult:
        return CrawlResult(
            pages=[
                CrawledPage(
                    url="https://example.com/docs",
                    title="Docs",
                    markdown="# Docs",
                    depth=0,
                )
            ],
            failures=[],
        )

    monkeypatch.setattr(book_builder, "crawl_site", fake_crawl_site)

    request = BuildRequest(
        provider="openai",
        model="gpt-4.1-mini",
        root_url="https://example.com/docs",
        llm_refine=False,
    )

    result = await book_builder.build_book(
        request=request,
        output_dir=str(tmp_path),
        secrets=AppSecrets(None, None, None),
    )

    book_path = Path(result["output_path"])
    manifest_path = Path(result["manifest_path"])

    assert book_path.exists()
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["pages_collected"] == 1
    assert result["output_files"] == ["book.md"]
