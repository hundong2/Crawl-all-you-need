# Document Crawling Web Project

[English](./README.md) | [한국어](./README.kr.md) | [日本語](./README.jp.md) | [中文](./README.zh.md) | [Français](./README.fr.md)

> An experimental project using `codex`, `gemini-cli`, `claude-code`, and `copilot-cli`
> to crawl documents and organize them into web pages.

## Model Ranking (Current)

- Speed, Accuracy 

| Rank | Model | Spec |
|---|---|---|
| 🥇 1st | **codex** |  gpt-5.3-codex medium|
| 🥈 2nd | **copilot** |  claude-sonnet-4.5 |
| 🥉 3rd | **gemini-cli** | gemini-2.5-pro |
| 4th | **antigravity** | gemini-3.0-preview |
| 5th | **claude code** | Opus 4.6 using teams |

## Project at a Glance

- Goal: Collect and analyze documents with multiple AI coding agents, then present the results as user-friendly web pages.
- Focus: Run the same topic with different models and compare output quality and productivity.
- Workflow: Iterative improvement (crawl accuracy, UI/UX, automation pipeline).

## Quick Link

- Codex: Core code and usage guide: [`codex/README.md`](./codex/README.md)
- Copilot: Core code and usage guide: [ copilot/README.md](./copilot/README.md)

---

## Claude Code Plugin — `security-audit`

This repo ships a reusable Claude Code plugin for security auditing.
It works in **any project** — not just this one.

### What it does

- `/security-audit` slash command — 4-phase scan, report, and auto-fix
- Real-time hook that **blocks file writes** containing API keys or passwords

### Install in another project

#### Option A — Claude Code Plugin System (recommended)

Open Claude Code in any project and run:

```
/plugin marketplace add hundong2/Crawl-all-you-need
/plugin install security-audit
```

The hook activates automatically after installation.

#### Option B — Command only (no hook), single project

```bash
mkdir -p .claude/commands
curl -o .claude/commands/security-audit.md \
  https://raw.githubusercontent.com/hundong2/Crawl-all-you-need/main/plugin/security-audit/commands/security-audit.md
```

#### Option C — Command only, global (all projects on this machine)

```bash
mkdir -p ~/.claude/commands
curl -o ~/.claude/commands/security-audit.md \
  https://raw.githubusercontent.com/hundong2/Crawl-all-you-need/main/plugin/security-audit/commands/security-audit.md
```

### Usage

```
/security-audit
```

Runs automatically: scan → severity report → auto-fix → manual action list.

See [`plugin/security-audit/README.md`](./plugin/security-audit/README.md) for full documentation.
