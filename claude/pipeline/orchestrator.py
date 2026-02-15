"""End-to-end pipeline orchestrator: crawl -> LLM -> output."""

import os
import re
import tempfile
import time
from collections.abc import Generator
from urllib.parse import urlparse

from crawler.content_store import ContentStore
from crawler.site_crawler import SiteCrawler
from document.builder import CancelledError, DocumentBuilder
from document.markdown_writer import MarkdownWriter
from document.pdf_converter import PDFConverter
from llm.base_provider import ProviderCancelledError
from llm.provider_factory import create_provider


class PipelineOrchestrator:
    def __init__(
        self,
        company: str,
        model_name: str,
        api_key: str,
        site_url: str,
        output_format: str,
        max_depth: int = 3,
        max_pages: int = 100,
    ):
        self.company = company
        self.model_name = model_name
        self.api_key = api_key
        self.site_url = site_url
        self.output_format = output_format
        self.max_depth = max_depth
        self.max_pages = max_pages
        self._cancelled = False
        self._crawler: SiteCrawler | None = None
        self._builder: DocumentBuilder | None = None

    def cancel(self):
        self._cancelled = True
        if self._crawler:
            self._crawler.cancel()
        if self._builder:
            self._builder.cancel()

    def _elapsed(self, start: float) -> str:
        elapsed = time.time() - start
        if elapsed < 60:
            return f"{elapsed:.0f}s"
        return f"{elapsed / 60:.1f}m"

    @staticmethod
    def _build_filename(url: str, max_length: int = 90) -> str:
        """Build a filename from a URL, preserving the meaningful tail of the path.

        Strategy: domain + last N path segments that fit within max_length.
        Segments are added right-to-left so the most specific part is always kept.
        """
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        # Sanitize domain (remove port, special chars)
        domain = re.sub(r"[^\w.-]", "_", domain)

        path_parts = [p for p in parsed.path.strip("/").split("/") if p]
        if not path_parts:
            return domain[:max_length]

        # Sanitize each segment: replace non-word chars with underscore
        clean_parts = [re.sub(r"[^\w-]", "_", seg) for seg in path_parts]

        # Build from the rightmost (most meaningful) segments
        # Reserve space for domain + separator
        prefix = domain + "_"
        budget = max_length - len(prefix)

        if budget <= 0:
            return domain[:max_length]

        selected: list[str] = []
        used = 0
        for seg in reversed(clean_parts):
            # Truncate individual segments that are excessively long
            if len(seg) > 40:
                seg = seg[:40]
            separator_cost = 1 if selected else 0  # underscore between segments
            needed = len(seg) + separator_cost
            if used + needed > budget:
                break
            selected.append(seg)
            used += needed

        if not selected:
            # Even the last segment alone is too long -- truncate it
            selected = [clean_parts[-1][:budget]]

        selected.reverse()
        slug = "_".join(selected)
        return f"{prefix}{slug}"

    def run(self) -> Generator[tuple[str, str | None], None, None]:
        """
        Generator yielding (progress_message, output_file_or_none).
        The final yield includes the output file path.
        """
        start_time = time.time()

        # Step 1: Validate API key
        yield "[1/5] Validating API key...", None
        try:
            provider = create_provider(
                self.company, self.model_name, self.api_key
            )
            if not provider.validate_api_key():
                yield ("ERROR: API key is invalid. "
                       "Please verify and re-enter your key. "
                       "(API 키가 유효하지 않습니다. 키를 확인 후 다시 입력해주세요.)"), None
                return
        except Exception as e:
            yield (f"ERROR: Could not initialize the AI provider ({e}). "
                   "(AI 프로바이더 초기화에 실패했습니다.)"), None
            return

        yield f"[1/5] API key validated. ({self._elapsed(start_time)})", None

        # Step 2: Crawl the site
        yield "[2/5] Starting site crawl...", None
        self._crawler = SiteCrawler(
            max_depth=self.max_depth,
            max_pages=self.max_pages,
        )
        content_store = ContentStore()

        try:
            for page in self._crawler.crawl(self.site_url):
                if self._cancelled:
                    yield "Cancelled by user.", None
                    return
                content_store.add_page(page)
                status = "OK" if page.success else f"FAIL: {page.error_message}"
                yield (
                    f"[2/5] Crawled ({content_store.page_count}): "
                    f"{page.title or page.url} [{status}]",
                    None,
                )
        except Exception as e:
            yield (f"ERROR: Crawling failed ({e}). "
                   "Please check the URL and your network connection. "
                   "(크롤링에 실패했습니다. URL과 네트워크 연결을 확인해주세요.)"), None
            return

        if content_store.success_count == 0:
            yield ("ERROR: No pages could be crawled from this URL. "
                   "Please verify the URL is correct and accessible. "
                   "(해당 URL에서 크롤링된 페이지가 없습니다. "
                   "URL이 올바르고 접근 가능한지 확인해주세요.)"), None
            return

        yield (
            f"[2/5] Crawling complete. {content_store.success_count}/"
            f"{content_store.page_count} pages collected. "
            f"({self._elapsed(start_time)})",
            None,
        )

        # Step 3: Build document with LLM
        yield "[3/5] Processing content with LLM...", None
        builder = DocumentBuilder(provider, content_store)
        self._builder = builder
        try:
            for progress_msg in builder.build(self.site_url):
                if self._cancelled:
                    yield "Cancelled by user.", None
                    return
                yield f"[3/5] {progress_msg} ({self._elapsed(start_time)})", None
        except (CancelledError, ProviderCancelledError):
            yield "Cancelled by user.", None
            return
        except Exception as e:
            yield (f"ERROR: LLM processing failed ({e}). "
                   "This may be a temporary API issue. Please try again. "
                   "(LLM 처리에 실패했습니다. 일시적인 API 문제일 수 있습니다. "
                   "다시 시도해주세요.)"), None
            return

        # Step 4: Write markdown
        yield "[4/5] Generating output document...", None
        generation_time = time.time() - start_time
        writer = MarkdownWriter()
        md_content = writer.write(
            sections=builder.sections,
            site_url=self.site_url,
            toc=builder.toc,
            provider=f"{self.company}/{self.model_name}",
            page_count=content_store.success_count,
            generation_time=generation_time,
        )

        # Step 5: Generate output file
        output_dir = tempfile.mkdtemp()
        sanitized = self._build_filename(self.site_url)

        if self.output_format == "PDF":
            output_path = os.path.join(output_dir, f"{sanitized}.pdf")
            converter = PDFConverter()
            try:
                converter.convert(md_content, output_path)
            except Exception as e:
                yield (
                    f"WARNING: PDF conversion failed ({e}). "
                    "Falling back to Markdown.",
                    None,
                )
                output_path = os.path.join(output_dir, f"{sanitized}.md")
                writer.save(md_content, output_path)
        else:
            output_path = os.path.join(output_dir, f"{sanitized}.md")
            writer.save(md_content, output_path)

        yield (
            f"[5/5] Complete! Generated {os.path.basename(output_path)}",
            output_path,
        )
