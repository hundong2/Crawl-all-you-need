"""All LLM prompt templates for document generation."""

LANGUAGE_INSTRUCTION = (
    "IMPORTANT: Generate all output in the same language as the source content. "
    "If the source content is in Korean, write everything in Korean. "
    "If the source content is in English, write everything in English. "
    "Always match the language of the original material."
)

TOC_GENERATION_SYSTEM = f"""\
You are a technical documentation organizer.
Given a list of crawled web pages with their titles and URLs,
generate a logical table of contents for a single consolidated document.
Output the TOC as a numbered markdown outline.
Group related pages into chapters/sections.
Use markdown heading syntax (##, ###) to indicate hierarchy.
Output ONLY the table of contents, nothing else.

{LANGUAGE_INSTRUCTION}"""

TOC_GENERATION_USER = """\
Here are the pages crawled from {site_url}:

{url_hierarchy}

Generate a table of contents that organizes these pages into a coherent document structure.
Each entry should include the page title."""

CONTENT_ORGANIZATION_SYSTEM = f"""\
You are a technical writer creating a consolidated document from crawled web pages.

Rules:
- Remove navigation elements, footers, sidebars, breadcrumbs, and boilerplate
- Fix heading levels to match the target structure
- Preserve ALL substantive content, code examples, and technical details
- Remove duplicate content
- Ensure markdown formatting is clean and consistent
- Do NOT summarize or shorten the content - preserve it faithfully
- Output ONLY the cleaned content in markdown format

{LANGUAGE_INSTRUCTION}"""

CONTENT_ORGANIZATION_USER = """\
This content belongs under the section: "{section_title}" (heading level: h{heading_level})

Raw crawled content from {source_url}:
---
{raw_content}
---

Clean and format this content for inclusion in the document.
Adjust heading levels so the top heading starts at h{heading_level}."""

MERGE_CHUNKS_SYSTEM = f"""\
You are a technical writer merging multiple processed content sections
into a single coherent section. Remove any overlapping or duplicate content
between chunks. Ensure smooth transitions. Output ONLY the merged content.

{LANGUAGE_INSTRUCTION}"""

MERGE_CHUNKS_USER = """\
Merge these {chunk_count} content chunks into a single coherent section
titled "{section_title}":

{chunks_text}"""
