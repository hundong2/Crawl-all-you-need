---
name: readme-i18n-sync
description: Automatically sync README.md translations into README.kr.md, README.jp.md, README.zh.md, and README.fr.md while preserving Markdown structure and language navigation links. Use when a user asks to translate README updates across Korean, Japanese, Chinese, and French or keep localized README files aligned with the English source.
---

# README I18N Sync

## Execute Workflow

1. Read `README.md` as the source of truth.
2. Translate into Korean, Japanese, Chinese, and French.
3. Preserve Markdown structure, links, code blocks, tables, badges, and file paths.
4. Write outputs to:
- `README.kr.md`
- `README.jp.md`
- `README.zh.md`
- `README.fr.md`
5. Ensure every README file starts with this navigation row:
`[English](./README.md) | [한국어](./README.kr.md) | [日本語](./README.jp.md) | [中文](./README.zh.md) | [Français](./README.fr.md)`
6. Verify section ordering remains identical across all language files.

## Apply Translation Rules

- Translate prose only.
- Keep commands, code snippets, URLs, and file paths unchanged.
- Keep heading levels and list/table layout unchanged.
- Keep tool and product names unchanged unless explicitly requested.
- Do not add or remove sections.

## Use Automation

- Run `scripts/readme_i18n_sync.sh --engine <codex|claude|copilot|gemini>`.
- Configure one environment variable for the selected engine:
- `README_I18N_CODEX_CMD`
- `README_I18N_CLAUDE_CMD`
- `README_I18N_COPILOT_CMD`
- `README_I18N_GEMINI_CMD`

## Read Reference

- Prompt contract: `references/prompt-template.md`
