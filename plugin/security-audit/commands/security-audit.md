---
allowed-tools: Bash(git ls-files:*), Bash(git rm --cached:*), Bash(git log:*), Bash(git diff:*), Bash(truncate:*), Bash(grep:*), Glob, Grep, Read, Edit, Write
description: Scan the project for security vulnerabilities (secrets, CORS, SSRF, tracked logs, etc.) and auto-fix safe issues
---

Perform a 4-phase security audit on the current project.

## Phase 1 — Scan

Search the entire project for the following categories:

### A. Secrets & Credentials (HIGH)
Search source files for hardcoded secrets using these patterns:
- API key prefixes: `sk-`, `AIza`, `ghp_`, `xoxb-`, `AKIA`
- Assignment patterns: `api_key\s*=\s*["'][^"']{8,}`, `password\s*=\s*["'][^"']{4,}`, `secret\s*=\s*["'][^"']{8,}`, `token\s*=\s*["'][^"']{8,}`
- Bearer tokens in code: `Bearer [A-Za-z0-9\-._~+/]{20,}`

Also check log files: use `git ls-files` to find any `*.log`, `*.out`, `nohup.out` files tracked in git, then grep them for the above patterns.

Check git history for `.env` files: `git log --all --oneline -- "*.env" ".env"`

### B. Tracked Files That Should Be Ignored (MEDIUM)
Run `git ls-files` and check for:
- Log files: `*.log`, `*.out`, `nohup.out`
- Environment files: `.env`, `.env.local`, `.env.production`
- Compiled artifacts: `*.pyc`, `__pycache__/`
- OS files: `.DS_Store`, `Thumbs.db`
- IDE configs: `.idea/`, `.vscode/` (unless it contains approved shared settings)
- Secret files: `*.pem`, `*.key`, `*.p12`, `*.pfx`

### C. Code Vulnerabilities (HIGH/MEDIUM)
Search source files for:
- **CORS wildcard + credentials**: `allow_origins=\["?\*"?\]` combined with `allow_credentials=True`
- **Exception leakage**: `raise HTTPException.*detail=str\(e\)` or `return.*str(e)` in error handlers
- **SSRF**: user-supplied URL passed directly to HTTP client without validation (look for `request.url` or `url` param going to `requests.get`, `aiohttp`, `httpx`, `AsyncWebCrawler` without `_is_valid_url` or Pydantic `HttpUrl`)
- **Traceback in UI**: `traceback.format_exc()` passed to `st.code()`, `st.write()`, or returned in API response
- **unsafe_allow_html**: `unsafe_allow_html=True` with a variable (not a pure string literal)
- **Public API key attribute**: `self\.api_key\s*=` (should be `self._api_key`)

### D. Network Exposure (MEDIUM)
- Server bound to `0.0.0.0` without auth: `server_name="0.0.0.0"` or `host="0.0.0.0"`
- HTTP endpoints where HTTPS should be used

## Phase 2 — Report

Print a findings table:

```
| # | File:Line | Issue | Severity | Auto-fixable |
|---|-----------|-------|----------|--------------|
```

Then list PRIORITY ACTIONS — issues requiring manual intervention (e.g., rotating a leaked key at the provider console).

## Phase 3 — Auto-Fix

For each auto-fixable issue, apply the fix and note the change. Apply ALL of the following that are relevant:

1. **Clear log files containing secrets** — overwrite with empty content using `truncate -s 0 <file>`. Do NOT delete.

2. **Remove tracked log/temp files from git** — for each file found in Phase 1B:
   ```
   git rm --cached <file>
   ```

3. **Update .gitignore** — add missing patterns to the nearest appropriate `.gitignore`:
   - `*.log` and any specific log file names
   - `.env`, `.env.*`
   - `__pycache__/`, `*.pyc`
   - `.DS_Store`

4. **Mask exception details in API responses** — replace:
   ```python
   raise HTTPException(status_code=500, detail=str(e))
   ```
   with:
   ```python
   logger.exception("Unexpected error")
   raise HTTPException(status_code=500, detail="Internal server error")
   ```
   Add `import logging` and `logger = logging.getLogger(__name__)` if not present.

5. **Fix CORS wildcard** — replace `allow_origins=["*"]` with a comment:
   ```python
   allow_origins=["http://localhost:3000"],  # TODO: set to production origin before deploying
   ```

6. **Suppress framework debug logging** — for Gradio apps, add before `demo.launch()`:
   ```python
   logging.getLogger("gradio").setLevel(logging.WARNING)
   ```
   For FastAPI/Uvicorn, add `log_level="warning"` to uvicorn.run() if debug logs are too verbose.

7. **Privatize API key attribute** — rename `self.api_key` → `self._api_key` throughout the affected file.

8. **Remove static `unsafe_allow_html=True`** — rewrite pure HTML strings as Markdown where possible.

Do NOT auto-fix:
- Rotating leaked API keys (must be done at provider's console)
- Production CORS origins (requires knowing the deployment URL)
- Adding authentication to endpoints (architectural decision)
- URL validation for SSRF (requires understanding of business logic)

## Phase 4 — Summary

After applying all fixes:

1. List every file changed with a one-line description of what was fixed
2. List manual actions still required, numbered and actionable:
   - e.g., "1. Rotate the Google API key at https://console.cloud.google.com → Credentials"
3. Recommend installing a pre-commit hook:
   ```bash
   pip install detect-secrets
   detect-secrets scan > .secrets.baseline
   echo '.secrets.baseline' >> .gitignore
   ```
