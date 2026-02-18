# Security Audit

Perform a comprehensive security audit of the current project and automatically fix all issues found.

## Phase 1: Scan

Search the entire project for the following issues:

### Secrets & Credentials (HIGH)
- Hardcoded API keys, tokens, passwords in source files (patterns: `sk-`, `AIza`, `ghp_`, `Bearer `, `password =`, `api_key =`, `secret =`)
- Real credentials in log files (`*.log`, `*.out`, `nohup.out`)
- `.env` files tracked by git (`git ls-files | grep -E '\.env'`)
- Secrets in git history: `git log --all --oneline -- "*.env" "*.key" "*.pem"`

### Tracked files that should be ignored (MEDIUM)
- Log files: `git ls-files | grep -E '\.(log|out)$'`
- Compiled artifacts: `*.pyc`, `__pycache__`, `dist/`, `build/`
- IDE configs: `.idea/`, `.vscode/` (if no standard content)
- OS files: `.DS_Store`, `Thumbs.db`

### Code vulnerabilities (HIGH/MEDIUM)
- CORS wildcard + credentials: `allow_origins=["*"]` with `allow_credentials=True`
- Raw exception details in API responses: `raise HTTPException(..., detail=str(e))`
- No URL validation before crawling/fetching user-supplied URLs (SSRF risk)
- Full stack traces shown in UI (Streamlit `st.code(traceback.format_exc())`)
- `unsafe_allow_html=True` with variable content
- Public instance attributes storing secrets: `self.api_key =` (should be `self._api_key`)

### Network exposure (MEDIUM)
- Server bound to `0.0.0.0` without authentication
- HTTP used where HTTPS should be

### Deprecated/unmaintained packages (MEDIUM)
- `google-generativeai` (deprecated 2025, use `google-genai`)
- Any package with known CVEs in requirements.txt / pyproject.toml

## Phase 2: Report

Output a table like this:

| # | File:Line | Issue | Severity | Auto-fixable |
|---|-----------|-------|----------|--------------|
| 1 | path/file.py:42 | Description | HIGH | Yes/No |

Then list PRIORITY ACTIONS (issues that require manual intervention, e.g., rotating a leaked key).

## Phase 3: Fix

After reporting, automatically apply all auto-fixable issues:

### Auto-fixes to apply:
1. **Clear log files containing secrets** — overwrite with empty content (do NOT delete, preserve file)
2. **Remove tracked log/temp files from git** — run `git rm --cached <file>` for each
3. **Update .gitignore** — add missing patterns (`*.log`, `output.log`, `.env`, `__pycache__/`, etc.)
4. **Fix exception leakage** — replace `detail=str(e)` with `detail="Internal server error"` and add `logger.exception(...)` before it
5. **Fix CORS wildcard** — replace `allow_origins=["*"]` with a TODO comment: `allow_origins=["http://localhost:3000"]  # TODO: set production origin`
6. **Suppress framework debug logging** — for Gradio: add `logging.getLogger("gradio").setLevel(logging.WARNING)` before `demo.launch()`; for other frameworks, apply equivalent
7. **Privatize API key attributes** — rename `self.api_key` → `self._api_key` in provider/client classes
8. **Remove `unsafe_allow_html=True`** where content is static and HTML is not needed

### Do NOT auto-fix (require user action):
- Rotating leaked API keys (must be done at provider console)
- Setting production CORS origins (requires knowing the deployment URL)
- Adding authentication to endpoints (architectural decision)
- Fixing SSRF (requires understanding of the URL validation requirements)

## Phase 4: Summary

After fixes, show:
- List of files changed with brief description
- Manual actions still required (numbered, actionable)
- Recommended next step: add `detect-secrets` or `gitleaks` pre-commit hook
