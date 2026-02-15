"""Crawl4AI wrapper for deep site crawling."""

import asyncio
import logging
import threading
from collections.abc import Generator
from queue import Empty, Queue

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
except ImportError:
    AsyncWebCrawler = None  # type: ignore[assignment,misc]

from crawler.content_store import CrawledPage

logger = logging.getLogger(__name__)

_SENTINEL = object()


class SiteCrawler:
    def __init__(
        self,
        max_depth: int = 3,
        max_pages: int = 100,
        delay: float = 0.5,
        timeout: int = 60000,
    ):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.delay = delay
        self.timeout = timeout
        self._cancel_flag = False

    def cancel(self):
        self._cancel_flag = True

    def crawl(self, url: str) -> Generator[CrawledPage, None, None]:
        """
        Synchronous generator that yields CrawledPage objects.
        Runs Crawl4AI async code on a background thread.
        """
        if AsyncWebCrawler is None:
            raise RuntimeError(
                "crawl4ai is not installed. Install it with: pip install crawl4ai"
            )

        result_queue: Queue = Queue()
        error_queue: Queue = Queue()

        def _run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._async_crawl(url, result_queue))
            except Exception as e:
                error_queue.put(e)
            finally:
                result_queue.put(_SENTINEL)
                loop.close()

        thread = threading.Thread(target=_run_async, daemon=True)
        thread.start()

        while True:
            if self._cancel_flag:
                logger.info("Crawl cancelled by user")
                break
            try:
                result = result_queue.get(timeout=2.0)
            except Empty:
                if not thread.is_alive():
                    break
                continue

            if result is _SENTINEL:
                break
            yield result

        thread.join(timeout=10)
        if thread.is_alive():
            logger.warning("Crawler thread did not terminate within timeout")

        if not error_queue.empty():
            raise error_queue.get()

    async def _async_crawl(self, url: str, result_queue: Queue):
        # UI depth 1 = only the start page, depth 2 = start + direct children, etc.
        # crawl4ai uses 0-based depth, so subtract 1.
        crawl4ai_depth = max(0, self.max_depth - 1)
        strategy = BFSDeepCrawlStrategy(
            max_depth=crawl4ai_depth,
            include_external=False,
            max_pages=self.max_pages,
        )
        config = CrawlerRunConfig(
            deep_crawl_strategy=strategy,
            stream=True,
            word_count_threshold=50,
            delay_before_return_html=self.delay,
            page_timeout=self.timeout,
            verbose=False,
        )
        browser_config = BrowserConfig(headless=True)

        logger.info("Starting crawl: %s (max_depth=%d, max_pages=%d)",
                     url, self.max_depth, self.max_pages)

        async with AsyncWebCrawler(config=browser_config) as crawler:
            page_num = 0
            async for result in await crawler.arun(url, config=config):
                if self._cancel_flag:
                    break

                page_num += 1

                # Extract markdown content
                md_content = ""
                if result.success and result.markdown:
                    if hasattr(result.markdown, "raw_markdown"):
                        md_content = result.markdown.raw_markdown
                    elif isinstance(result.markdown, str):
                        md_content = result.markdown

                title = ""
                if result.metadata and isinstance(result.metadata, dict):
                    title = result.metadata.get("title", "")

                depth = 0
                if result.metadata and isinstance(result.metadata, dict):
                    depth = result.metadata.get("depth", 0)

                page = CrawledPage(
                    url=result.url,
                    title=title,
                    markdown_content=md_content,
                    depth=depth,
                    success=result.success,
                    error_message=result.error_message or "",
                )
                result_queue.put(page)

                if result.success:
                    logger.debug("Page %d crawled: %s (%d chars)",
                                 page_num, result.url, len(md_content))
                else:
                    logger.warning("Page %d failed: %s - %s",
                                   page_num, result.url,
                                   result.error_message or "unknown error")

            logger.info("Crawl finished: %d pages processed", page_num)
