from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urljoin, urldefrag, urlparse

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_md


@dataclass
class CrawledPage:
    url: str
    title: str
    markdown: str
    depth: int


@dataclass
class CrawlResult:
    pages: list[CrawledPage]
    failures: list[str]


def _normalize_url(base_url: str, href: str) -> str | None:
    if not href:
        return None
    merged = urljoin(base_url, href)
    clean, _ = urldefrag(merged)
    parsed = urlparse(clean)
    if parsed.scheme not in {"http", "https"}:
        return None
    return clean


def _same_domain(root: str, target: str) -> bool:
    return urlparse(root).netloc == urlparse(target).netloc


def _extract_links(base_url: str, html: str) -> Iterable[str]:
    soup = BeautifulSoup(html, "html.parser")
    for anchor in soup.select("a[href]"):
        normalized = _normalize_url(base_url, anchor.get("href", ""))
        if normalized:
            yield normalized


def _extract_content(url: str, html: str, depth: int) -> CrawledPage:
    soup = BeautifulSoup(html, "html.parser")
    for noisy in soup(["script", "style", "noscript"]):
        noisy.decompose()
    title = (soup.title.string or "Untitled").strip() if soup.title else "Untitled"
    body = soup.body or soup
    markdown = html_to_md(str(body), heading_style="ATX")
    return CrawledPage(url=url, title=title, markdown=markdown.strip(), depth=depth)


async def crawl_site(root_url: str, max_pages: int = 30, max_depth: int = 2) -> CrawlResult:
    """Crawl same-domain pages using BFS traversal."""
    pages: list[CrawledPage] = []
    failures: list[str] = []
    seen: set[str] = set()
    queue: deque[tuple[str, int]] = deque([(root_url, 0)])

    timeout = httpx.Timeout(20.0, connect=8.0)
    headers = {"User-Agent": "sitebooker/0.1 (+https://example.local)"}

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
        while queue and len(pages) < max_pages:
            url, depth = queue.popleft()
            if url in seen or depth > max_depth:
                continue
            seen.add(url)

            try:
                response = await client.get(url)
                response.raise_for_status()
            except Exception:
                failures.append(url)
                continue

            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type:
                continue

            html = response.text
            pages.append(_extract_content(url, html, depth))

            if depth == max_depth:
                continue

            for link in _extract_links(url, html):
                if _same_domain(root_url, link) and link not in seen:
                    queue.append((link, depth + 1))

            await asyncio.sleep(0)

    pages.sort(key=lambda p: (p.depth, p.url))
    return CrawlResult(pages=pages, failures=sorted(set(failures)))
