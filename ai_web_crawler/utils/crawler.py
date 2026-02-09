"""웹 크롤링 유틸리티"""
import asyncio
from typing import List, Dict, Optional, Callable
from urllib.parse import urljoin, urlparse
import re


class WebCrawler:
    """Crawl4AI 기반 웹 크롤러"""
    
    def __init__(self):
        self.visited_urls = set()
        self.crawled_data = []
    
    async def crawl_single_page(self, url: str, progress_callback: Optional[Callable] = None) -> Dict:
        """단일 페이지 크롤링"""
        try:
            from crawl4ai import AsyncWebCrawler
            
            if progress_callback:
                progress_callback(f"크롤링 중: {url}")
            
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(url=url)
                
                if result.success:
                    return {
                        "url": url,
                        "title": result.metadata.get("title", ""),
                        "content": result.markdown,
                        "links": result.links.get("internal", []),
                        "success": True
                    }
                else:
                    return {
                        "url": url,
                        "error": result.error_message,
                        "success": False
                    }
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "success": False
            }
    
    async def crawl_website(
        self, 
        start_url: str, 
        max_pages: int = 50,
        same_domain_only: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """웹사이트 전체 크롤링"""
        self.visited_urls.clear()
        self.crawled_data.clear()
        
        base_domain = urlparse(start_url).netloc
        to_visit = [start_url]
        
        while to_visit and len(self.visited_urls) < max_pages:
            current_url = to_visit.pop(0)
            
            if current_url in self.visited_urls:
                continue
            
            self.visited_urls.add(current_url)
            
            if progress_callback:
                progress_callback(
                    f"진행: {len(self.visited_urls)}/{max_pages} 페이지",
                    len(self.visited_urls) / max_pages
                )
            
            result = await self.crawl_single_page(current_url, progress_callback)
            
            if result["success"]:
                self.crawled_data.append(result)
                
                # 링크 추가
                if same_domain_only:
                    for link in result.get("links", []):
                        full_url = urljoin(current_url, link)
                        if urlparse(full_url).netloc == base_domain:
                            if full_url not in self.visited_urls and full_url not in to_visit:
                                to_visit.append(full_url)
            
            # 과부하 방지
            await asyncio.sleep(0.5)
        
        return self.crawled_data
    
    def get_markdown_content(self) -> str:
        """모든 크롤링 데이터를 하나의 Markdown으로 변환"""
        markdown = "# 웹사이트 크롤링 결과\n\n"
        markdown += f"총 {len(self.crawled_data)}개 페이지\n\n"
        markdown += "---\n\n"
        
        for idx, page in enumerate(self.crawled_data, 1):
            if page["success"]:
                markdown += f"## {idx}. {page['title']}\n\n"
                markdown += f"**URL**: {page['url']}\n\n"
                markdown += page["content"]
                markdown += "\n\n---\n\n"
        
        return markdown


def create_crawler() -> WebCrawler:
    """크롤러 인스턴스 생성"""
    return WebCrawler()
