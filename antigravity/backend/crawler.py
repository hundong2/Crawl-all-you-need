import asyncio
from typing import List, Dict, Any
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy

class DocumentationCrawler:
    def __init__(self):
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=True,
        )
        self.run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=10,
        )
        # We will use the shared LLM service; need to import it inside methods to avoid circular imports 
        # or just import here if possible. 
        # Actually, let's inject it or import it.
        from .llm_service import llm_service
        self.llm_service = llm_service

    async def enhance_content(self, url: str, content: str) -> str:
        """Uses Gemini to enhance and design the content."""
        instruction = (
            "You are an expert technical writer and designer. "
            "Refactor the following markdown content from a documentation page to be cleaner, "
            "better structured, and more aesthetically pleasing. "
            "Fix any broken tables or code blocks. "
            "Do NOT remove important information, just improve the presentation. "
            "Add a clear title if missing."
        )
        # Using gemini-flash-latest for potentially better availability
        try:
             enhanced = await self.llm_service.process_content("google", "gemini-flash-latest", content, instruction)
             return enhanced
        except Exception as e:
            print(f"Error enhancing content for {url}: {e}")
            return f"{content}\n\n> **Warning:** AI Enhancement failed for this page due to: {str(e)}"

    async def crawl_single_page(self, url: str, enhance: bool = False) -> str:
        """Crawls a single page and returns the markdown content."""
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=self.run_config)
            if result.success:
                content = result.markdown
                if enhance:
                    content = await self.enhance_content(url, content)
                return f"# {result.url}\n\n{content}\n\n---\n\n"
            else:
                return f"Error crawling {url}: {result.error_message}\n\n"

    async def crawl_site(self, start_url: str, recursive: bool = False, max_pages: int = 10, enhance: bool = False) -> str:
        if recursive:
            return await self.crawl_recursive(start_url, max_depth=2, enhance=enhance) # Depth 2 for safety in MVP
        return await self.crawl_single_page(start_url, enhance=enhance)

    async def crawl_recursive(self, url: str, max_depth: int = 2, enhance: bool = False) -> str:
        """
        A placeholder for recursive crawling.
        """
        # TODO: Implement robust recursive crawling
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=self.run_config)
            if not result.success:
                 return f"Error crawling {url}: {result.error_message}\n\n"
            
            content = result.markdown
            if enhance:
                content = await self.enhance_content(url, content)

            combined_markdown = f"# {result.url}\n\n{content}\n\n---\n\n"
            
            # Simple link extraction (this is naive)
            internal_links = [
                link['href'] for link in result.links.get('internal', [])
                if link['href'].startswith(url) or link['href'].startswith('/')
            ]
            
            # Limit links for safety
            for link in internal_links[:5]: # Crawl top 5 links for demo
                full_link = link if link.startswith('http') else url + link
                sub_result = await crawler.arun(url=full_link, config=self.run_config)
                if sub_result.success:
                    sub_content = sub_result.markdown
                    if enhance:
                        sub_content = await self.enhance_content(full_link, sub_content)
                    combined_markdown += f"# {sub_result.url}\n\n{sub_content}\n\n---\n\n"
            
            return combined_markdown

# Create a global instance
crawler = DocumentationCrawler()
