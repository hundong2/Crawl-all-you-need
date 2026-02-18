#!/usr/bin/env python3
"""
Secret Scan Hook for Claude Code — security-audit plugin
Intercepts file writes/edits and warns if potential secrets are detected.
Exit code 2 = block the tool call and show warning to user.
Exit code 0 = allow the tool call to proceed.
"""

import json
import os
import re
import sys

# Secret patterns: (rule_name, regex, description)
SECRET_PATTERNS = [
    (
        "openai_api_key",
        re.compile(r'sk-[A-Za-z0-9]{20,}'),
        "OpenAI API key (sk-...)",
    ),
    (
        "anthropic_api_key",
        re.compile(r'sk-ant-[A-Za-z0-9\-]{20,}'),
        "Anthropic API key (sk-ant-...)",
    ),
    (
        "google_api_key",
        re.compile(r'AIza[0-9A-Za-z\-_]{30,}'),
        "Google API key (AIza...)",
    ),
    (
        "github_token",
        re.compile(r'ghp_[A-Za-z0-9]{36,}'),
        "GitHub personal access token (ghp_...)",
    ),
    (
        "aws_access_key",
        re.compile(r'AKIA[0-9A-Z]{16}'),
        "AWS access key ID (AKIA...)",
    ),
    (
        "slack_token",
        re.compile(r'xox[baprs]-[0-9A-Za-z\-]{10,}'),
        "Slack token (xox[b/a/p/r/s]-...)",
    ),
    (
        "bearer_token",
        re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]{30,}'),
        "Bearer token in Authorization header",
    ),
    (
        "hardcoded_password",
        re.compile(
            r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']{6,}["\']',
            re.IGNORECASE,
        ),
        "Hardcoded password assignment",
    ),
    (
        "hardcoded_secret",
        re.compile(
            r'(?:secret|api_secret|client_secret)\s*=\s*["\'][^"\']{8,}["\']',
            re.IGNORECASE,
        ),
        "Hardcoded secret assignment",
    ),
]

# Files/paths to skip (test fixtures, example configs, etc.)
SKIP_PATHS = [
    ".git/",
    "node_modules/",
    "venv/",
    ".venv/",
    "__pycache__/",
    ".env.example",
    ".env.sample",
    ".env.template",
    "test_",
    "_test.",
    "spec_",
    "_spec.",
]

# Placeholder patterns — safe to ignore
PLACEHOLDER_PATTERNS = [
    re.compile(r'your[_-]?(?:api[_-]?)?key[_-]?here', re.IGNORECASE),
    re.compile(r'<YOUR[_-]?[A-Z_]+>', re.IGNORECASE),
    re.compile(r'xxx+', re.IGNORECASE),
    re.compile(r'\*{3,}'),
    re.compile(r'\.\.\.'),
    re.compile(r'example|placeholder|dummy|fake|test|sample|replace.me', re.IGNORECASE),
]


def is_placeholder(value: str) -> bool:
    return any(p.search(value) for p in PLACEHOLDER_PATTERNS)


def should_skip_path(file_path: str) -> bool:
    return any(skip in file_path for skip in SKIP_PATHS)


def scan_content(content: str, file_path: str) -> list[tuple[str, str]]:
    """Return list of (rule_name, description) for each match found."""
    if should_skip_path(file_path):
        return []

    findings = []
    for rule_name, pattern, description in SECRET_PATTERNS:
        for match in pattern.finditer(content):
            matched_value = match.group(0)
            if not is_placeholder(matched_value):
                findings.append((rule_name, description))
                break  # one finding per rule per file

    return findings


def extract_content(tool_name: str, tool_input: dict) -> tuple[str, str]:
    """Return (file_path, content) from tool input."""
    file_path = tool_input.get("file_path", "")
    if tool_name == "Write":
        return file_path, tool_input.get("content", "")
    elif tool_name == "Edit":
        return file_path, tool_input.get("new_string", "")
    elif tool_name == "MultiEdit":
        edits = tool_input.get("edits", [])
        combined = " ".join(e.get("new_string", "") for e in edits)
        return file_path, combined
    return file_path, ""


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        sys.exit(0)  # allow on parse error

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)

    file_path, content = extract_content(tool_name, tool_input)
    if not content:
        sys.exit(0)

    findings = scan_content(content, file_path)
    if not findings:
        sys.exit(0)

    # Block and warn
    warning_lines = [
        "⚠️  SECRET DETECTED — Write blocked by security-audit plugin",
        "",
        f"File: {file_path}",
        "",
        "Potential secrets found:",
    ]
    for _, description in findings:
        warning_lines.append(f"  • {description}")

    warning_lines += [
        "",
        "Actions:",
        "  1. Use environment variables instead of hardcoded values",
        "  2. Add the file to .gitignore if it must contain secrets",
        "  3. If this is a placeholder/example value, make it more clearly fake",
        "     (e.g., use 'your-api-key-here' or '<YOUR_API_KEY>')",
        "",
        "To bypass this check for intentional writes, set:",
        "  SECURITY_AUDIT_SKIP=1 in your environment",
    ]

    if os.environ.get("SECURITY_AUDIT_SKIP") == "1":
        sys.exit(0)

    print("\n".join(warning_lines), file=sys.stderr)
    sys.exit(2)  # block the tool call


if __name__ == "__main__":
    main()
