"""웹 크롤링 유틸리티"""
import asyncio
from typing import List, Dict, Optional, Callable
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
import markdownify


class WebCrawler:
    """Crawl4AI 기반 웹 크롤러"""
    
    def __init__(self):
        self.visited_urls = set()
        self.crawled_data = []
    
    async def crawl_single_page(
        self, 
        url: str, 
        progress_callback: Optional[Callable] = None,
        content_processor: Optional[Callable[[str], str]] = None
    ) -> Dict:
        """단일 페이지 크롤링 (JavaScript 렌더링 지원)"""
        try:
            from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
            
            if progress_callback:
                progress_callback(f"크롤링 중: {url}")
            
            # JavaScript 렌더링을 위한 브라우저 설정
            browser_config = BrowserConfig(
                headless=True,
                verbose=False
            )
            
            # 크롤링 설정
            run_config = CrawlerRunConfig(
                wait_until="networkidle",        # 네트워크 안정화까지 대기
                page_timeout=30000,              # 30초 타임아웃
                delay_before_return_html=2.0     # 동적 콘텐츠 로딩 대기
            )
            
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url=url, config=run_config)
                
                if result.success:
                    # HTML에서 메인 콘텐츠만 추출
                    content = self._extract_main_content(result.html, result.markdown)
                    
                    # LLM 콘텐츠 정제 (옵션)
                    if content_processor:
                        if progress_callback:
                            progress_callback(f"LLM 정제 중: {url}")
                        try:
                            content = await content_processor(content)
                        except Exception as e:
                            print(f"Content processing error: {e}")
                            # 실패해도 원본 콘텐츠 반환
                    
                    return {
                        "url": url,
                        "title": result.metadata.get("title", ""),
                        "content": content,
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
    
    def _extract_main_content(self, html: str, fallback_markdown: str) -> str:
        """HTML에서 메인 콘텐츠만 추출하고 마크다운으로 변환"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 다양한 사이트 지원을 위한 선택자 우선순위
            selectors = [
                '#article-contents',      # GitHub Docs
                'main',                   # 일반적인 메인 콘텐츠
                'article',                # 아티클
                '.markdown-body',         # Markdown 콘텐츠
                '[role="main"]',          # ARIA main
            ]
            
            main_content = None
            for selector in selectors:
                main_content = soup.select_one(selector)
                if main_content and len(main_content.get_text().strip()) > 200:
                    break
            
            if main_content:
                # 불필요한 요소 제거
                for tag in main_content.select('nav, header, footer, aside, .sidebar, .navigation'):
                    tag.decompose()
                
                # HTML을 마크다운으로 변환
                markdown = markdownify.markdownify(
                    str(main_content),
                    heading_style="ATX",
                    code_language="",
                    bullets="-"
                )
                
                # 과도한 빈 줄 제거
                while '\n\n\n' in markdown:
                    markdown = markdown.replace('\n\n\n', '\n\n')
                
                return markdown.strip()
            
            return fallback_markdown
        except Exception as e:
            print(f"Content extraction error: {e}")
            return fallback_markdown
    
    def _clean_content(self, markdown: str) -> str:
        """콘텐츠에서 네비게이션과 불필요한 요소 제거"""
        lines = markdown.split('\n')
        cleaned_lines = []
        in_main_content = False
        skip_section = False
        
        # 제거할 패턴들
        skip_patterns = [
            'Skip to main content',
            'Search or ask Copilot',
            'Select language:',
            'Open menu',
            'Open Sidebar',
            'Sign up',
            'This article is also available in',
            'Version: Free, Pro',
            'GitHub Docs](https://docs.github.com',
        ]
        
        # 섹션 시작 패턴 (실제 문서 내용)
        content_start_patterns = [
            '# Installing',
            '## Installing',
            '# About',
            '## About',
            '# Get started',
            '## Prerequisites',
            '## Steps',
        ]
        
        # 섹션 종료 패턴 (푸터 시작)
        footer_patterns = [
            '### Did this doc help',
            '### Still need help',
            '## Legal',
            '© 2026 GitHub',
            '[Terms]',
            '[Privacy]',
        ]
        
        for line in lines:
            # 푸터 시작되면 스킵
            if any(pattern in line for pattern in footer_patterns):
                skip_section = True
                continue
            
            if skip_section:
                continue
            
            # 스킵할 패턴 체크
            if any(pattern in line for pattern in skip_patterns):
                continue
            
            # 메인 콘텐츠 시작 감지
            if any(pattern in line for pattern in content_start_patterns):
                in_main_content = True
            
            # 사이드바/네비게이션 필터링 (들여쓰기가 많은 리스트 항목)
            stripped = line.lstrip()
            if stripped.startswith('* [') and not in_main_content:
                continue
            
            # 빈 줄이 너무 많이 연속되지 않도록
            if line.strip() == '':
                if cleaned_lines and cleaned_lines[-1].strip() == '':
                    continue
            
            cleaned_lines.append(line)
        
        # 앞뒤 공백 제거
        while cleaned_lines and cleaned_lines[0].strip() == '':
            cleaned_lines.pop(0)
        while cleaned_lines and cleaned_lines[-1].strip() == '':
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    async def crawl_website(
        self, 
        start_url: str, 
        max_pages: int = 50,
        same_domain_only: bool = True,
        progress_callback: Optional[Callable] = None,
        content_processor: Optional[Callable[[str], str]] = None
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
            
            result = await self.crawl_single_page(
                current_url, 
                progress_callback,
                content_processor=content_processor
            )
            
            if result["success"]:
                self.crawled_data.append(result)
                
                # 링크 추가 (딕셔너리 형태 처리)
                if same_domain_only:
                    links = result.get("links", [])
                    
                    # links가 딕셔너리 리스트인 경우 처리
                    for link in links:
                        # link가 딕셔너리인 경우 href 추출
                        if isinstance(link, dict):
                            link_url = link.get('href', '')
                        else:
                            link_url = str(link) if link else ''
                        
                        # 유효한 URL인지 확인
                        if not link_url or not isinstance(link_url, str):
                            continue
                        
                        # 상대 URL을 절대 URL로 변환
                        try:
                            full_url = urljoin(current_url, link_url)
                            
                            # 같은 도메인인지 확인
                            if urlparse(full_url).netloc == base_domain:
                                if full_url not in self.visited_urls and full_url not in to_visit:
                                    to_visit.append(full_url)
                        except Exception as e:
                            # URL 처리 오류는 무시하고 계속 진행
                            continue
            
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
