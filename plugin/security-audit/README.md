# security-audit — Claude Code Plugin

A Claude Code plugin that scans your project for security vulnerabilities and auto-fixes common issues.

## Features

| Feature | Description |
|---------|-------------|
| `/security-audit` command | 4-phase scan → report → auto-fix → summary |
| Real-time secret detection hook | Blocks file writes containing API keys / passwords |
| Auto-fix | Clears log files, updates `.gitignore`, masks exception leakage, fixes CORS |

## What It Scans

- Hardcoded API keys & tokens (`sk-`, `AIza`, `ghp_`, `AKIA`, `xoxb-`, `Bearer ...`)
- Log files tracked in git that may contain secrets
- `.env` files in git history
- CORS wildcard + credentials misconfiguration
- Raw exception details leaked in API responses (SSRF, stack traces)
- Server bound to `0.0.0.0` without authentication
- `unsafe_allow_html=True` with dynamic content

## Installation

### Option A — Via Claude Code Plugin System (recommended)

```
/plugin marketplace add hundong2/Crawl-all-you-need
/plugin install security-audit
```

### Option B — Manual (single project)

```bash
# From the root of any project
mkdir -p .claude/commands
curl -o .claude/commands/security-audit.md \
  https://raw.githubusercontent.com/hundong2/Crawl-all-you-need/main/plugin/security-audit/commands/security-audit.md
```

### Option C — Global install (all projects on this machine)

```bash
mkdir -p ~/.claude/commands
curl -o ~/.claude/commands/security-audit.md \
  https://raw.githubusercontent.com/hundong2/Crawl-all-you-need/main/plugin/security-audit/commands/security-audit.md
```

## Usage

### Run security audit
```
/security-audit
```

The command runs 4 phases automatically:
1. **Scan** — finds secrets, bad patterns, tracked files
2. **Report** — severity table with auto-fixable classification
3. **Fix** — applies all safe auto-fixes
4. **Summary** — lists remaining manual actions

### Secret detection hook

Once installed as a plugin (Option A), the hook activates automatically.
It intercepts every `Edit`/`Write`/`MultiEdit` tool call and blocks writes
that contain real API keys or passwords.

To bypass for intentional writes (e.g., writing test fixtures):
```bash
export SECURITY_AUDIT_SKIP=1
```

## Auto-fixed Issues

| Issue | Fix Applied |
|-------|-------------|
| Log files with secrets | Content cleared with `truncate -s 0` |
| Log/temp files tracked in git | `git rm --cached` |
| Missing `.gitignore` patterns | `*.log`, `.env`, `__pycache__/` added |
| `raise HTTPException(detail=str(e))` | Replaced with generic message + logger |
| `allow_origins=["*"]` | Replaced with TODO comment |
| Gradio debug logging API key leakage | `logging.getLogger("gradio").setLevel(WARNING)` added |
| `self.api_key` public attribute | Renamed to `self._api_key` |

## Issues Requiring Manual Action

| Issue | Why Manual |
|-------|-----------|
| Leaked API key rotation | Must be done at provider console |
| Production CORS origin | Requires knowing deployment URL |
| Authentication on endpoints | Architectural decision |
| SSRF URL validation | Requires business logic understanding |
