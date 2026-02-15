"""Document builder: orchestrates LLM calls to organize crawled content."""

import logging
import re
from collections.abc import Generator
from dataclasses import dataclass

from crawler.content_store import ContentStore
from llm.base_provider import BaseLLMProvider, ProviderCancelledError
from llm.prompts import (
    CONTENT_ORGANIZATION_SYSTEM,
    CONTENT_ORGANIZATION_USER,
    MERGE_CHUNKS_SYSTEM,
    MERGE_CHUNKS_USER,
    TOC_GENERATION_SYSTEM,
    TOC_GENERATION_USER,
)

logger = logging.getLogger(__name__)


@dataclass
class DocumentSection:
    title: str
    heading_level: int
    source_url: str
    content: str


class CancelledError(Exception):
    """Raised when the build is cancelled by the user."""


class DocumentBuilder:
    def __init__(self, provider: BaseLLMProvider, content_store: ContentStore):
        self.provider = provider
        self.content_store = content_store
        self.sections: list[DocumentSection] = []
        self.toc: str = ""
        self._cancelled = False

    def cancel(self):
        """Signal that the build should stop as soon as possible."""
        self._cancelled = True
        self.provider.request_cancel()

    def _check_cancelled(self):
        if self._cancelled:
            raise CancelledError()

    def build(self, site_url: str) -> Generator[str, None, None]:
        """
        Generator that yields progress messages.
        Populates self.sections and self.toc.
        Raises CancelledError if cancelled.
        """
        # Phase 1: Generate TOC
        yield "Generating table of contents..."
        self.toc = self._generate_toc(site_url)
        self._check_cancelled()

        # Phase 2: Process each page
        pages = self.content_store.get_successful_pages()
        for i, page in enumerate(pages):
            self._check_cancelled()
            title = page.title or page.url
            yield f"Processing page {i + 1}/{len(pages)}: {title}"

            if not page.markdown_content.strip():
                continue

            estimated_tokens = self.provider.estimate_tokens(page.markdown_content)
            max_input = self.provider.get_max_input_tokens()

            try:
                if estimated_tokens <= max_input:
                    section = self._process_single_page(page)
                else:
                    section = self._process_chunked_page(page, max_input)
            except CancelledError:
                raise
            except Exception as e:
                logger.warning("LLM processing failed for '%s': %s. "
                               "Using raw content as fallback.", title, e)
                section = DocumentSection(
                    title=title,
                    heading_level=2,
                    source_url=page.url,
                    content=page.markdown_content,
                )

            self.sections.append(section)

        yield f"Document build complete. {len(self.sections)} sections created."

    def _generate_toc(self, site_url: str) -> str:
        hierarchy = self.content_store.get_url_hierarchy()
        try:
            response = self.provider.generate(
                system_prompt=TOC_GENERATION_SYSTEM,
                user_prompt=TOC_GENERATION_USER.format(
                    site_url=site_url,
                    url_hierarchy=hierarchy,
                ),
            )
            toc = response.content.strip()
            if toc:
                return toc
        except (ProviderCancelledError, CancelledError):
            raise
        except Exception as e:
            logger.warning("TOC generation failed: %s", e)

        # Fallback: build a simple TOC from the URL hierarchy
        logger.info("Using fallback TOC from URL hierarchy")
        return hierarchy or "# Table of Contents\n\n(Auto-generated)"

    def _process_single_page(self, page) -> DocumentSection:
        """Process a page that fits within the context window."""
        title = page.title or page.url
        response = self.provider.generate(
            system_prompt=CONTENT_ORGANIZATION_SYSTEM,
            user_prompt=CONTENT_ORGANIZATION_USER.format(
                section_title=title,
                heading_level=2,
                source_url=page.url,
                raw_content=page.markdown_content,
            ),
        )
        return DocumentSection(
            title=title,
            heading_level=2,
            source_url=page.url,
            content=response.content,
        )

    def _process_chunked_page(self, page, max_input: int) -> DocumentSection:
        """Process a page that exceeds the context window by chunking."""
        title = page.title or page.url
        chunks = self._split_content(page.markdown_content, max_input)
        processed_chunks = []

        for chunk in chunks:
            self._check_cancelled()
            response = self.provider.generate(
                system_prompt=CONTENT_ORGANIZATION_SYSTEM,
                user_prompt=CONTENT_ORGANIZATION_USER.format(
                    section_title=title,
                    heading_level=2,
                    source_url=page.url,
                    raw_content=chunk,
                ),
            )
            processed_chunks.append(response.content)

        # Try to merge via LLM if total fits
        merged_text = "\n\n".join(processed_chunks)
        if self.provider.estimate_tokens(merged_text) <= max_input:
            merge_response = self.provider.generate(
                system_prompt=MERGE_CHUNKS_SYSTEM,
                user_prompt=MERGE_CHUNKS_USER.format(
                    chunk_count=len(processed_chunks),
                    section_title=title,
                    chunks_text=merged_text,
                ),
            )
            content = merge_response.content
        else:
            content = merged_text

        return DocumentSection(
            title=title,
            heading_level=2,
            source_url=page.url,
            content=content,
        )

    def _split_content(self, content: str, max_tokens: int) -> list[str]:
        """Split content into chunks that fit within max_tokens."""
        # First try splitting by ## headings
        sections = re.split(r"\n(?=## )", content)

        chunks = []
        current_chunk = ""

        for section in sections:
            combined = (
                current_chunk + "\n\n" + section if current_chunk else section
            )
            if self.provider.estimate_tokens(combined) <= max_tokens:
                current_chunk = combined
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                if self.provider.estimate_tokens(section) > max_tokens:
                    chunks.extend(
                        self._split_by_paragraphs(section, max_tokens)
                    )
                    current_chunk = ""
                else:
                    current_chunk = section

        if current_chunk:
            chunks.append(current_chunk)

        if chunks:
            return chunks
        # Fallback: content could not be split by headings, force paragraph split
        return self._split_by_paragraphs(content, max_tokens)

    def _split_by_paragraphs(self, text: str, max_tokens: int) -> list[str]:
        """Split text by paragraph boundaries with overlap."""
        paragraphs = text.split("\n\n")
        chunks = []
        current = ""

        for para in paragraphs:
            candidate = current + "\n\n" + para if current else para
            if self.provider.estimate_tokens(candidate) <= max_tokens:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                    # Keep last ~200 tokens as overlap
                    words = current.split()
                    overlap = " ".join(words[-50:])
                    current = overlap + "\n\n" + para
                else:
                    # Single paragraph exceeds limit - hard split by characters
                    for sub in self._hard_split(para, max_tokens):
                        chunks.append(sub)
                    current = ""
                    continue

                # Check if current (overlap + para) still exceeds limit
                if self.provider.estimate_tokens(current) > max_tokens:
                    for sub in self._hard_split(current, max_tokens):
                        chunks.append(sub)
                    current = ""

        if current:
            chunks.append(current)

        return chunks if chunks else [text]

    def _hard_split(self, text: str, max_tokens: int) -> list[str]:
        """Last-resort split: cut text by character count based on token estimate."""
        # Approximate chars per token ratio (~4 chars/token)
        chars_per_token = max(1, len(text) // max(1, self.provider.estimate_tokens(text)))
        chunk_size = max(100, max_tokens * chars_per_token)
        parts = []
        for start in range(0, len(text), chunk_size):
            parts.append(text[start:start + chunk_size])
        return parts
