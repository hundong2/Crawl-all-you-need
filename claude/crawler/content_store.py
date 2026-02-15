"""In-memory storage for crawled pages."""

from dataclasses import dataclass, field
from urllib.parse import urldefrag, urlparse, urlunparse


def _normalize_url(url: str) -> str:
    """Normalize a URL by stripping fragments and trailing slashes from path."""
    url_without_fragment, _ = urldefrag(url)
    parsed = urlparse(url_without_fragment)
    normalized_path = parsed.path.rstrip("/") or "/"
    return urlunparse(parsed._replace(path=normalized_path))


@dataclass
class CrawledPage:
    url: str
    title: str
    markdown_content: str
    depth: int
    success: bool
    error_message: str = ""


@dataclass
class ContentStore:
    pages: dict[str, CrawledPage] = field(default_factory=dict)
    crawl_order: list[str] = field(default_factory=list)

    def add_page(self, page: CrawledPage):
        normalized = _normalize_url(page.url)
        if normalized not in self.pages:
            page.url = normalized
            self.pages[normalized] = page
            self.crawl_order.append(normalized)

    def get_ordered_pages(self) -> list[CrawledPage]:
        """Return pages in BFS crawl order."""
        return [self.pages[url] for url in self.crawl_order if url in self.pages]

    def get_successful_pages(self) -> list[CrawledPage]:
        """Return only successfully crawled pages in order."""
        return [
            self.pages[url]
            for url in self.crawl_order
            if url in self.pages and self.pages[url].success
        ]

    def get_total_content_length(self) -> int:
        return sum(len(p.markdown_content) for p in self.pages.values())

    def get_estimated_total_tokens(self) -> int:
        """Estimate total tokens across all pages (~4 chars per token)."""
        return self.get_total_content_length() // 4

    def get_url_hierarchy(self) -> str:
        """Generate a URL tree for TOC planning by the LLM."""
        lines = []
        for url in self.crawl_order:
            page = self.pages[url]
            if not page.success:
                continue
            indent = "  " * page.depth
            title = page.title or page.url
            lines.append(f"{indent}- {title} ({page.url})")
        return "\n".join(lines)

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def success_count(self) -> int:
        return sum(1 for p in self.pages.values() if p.success)
