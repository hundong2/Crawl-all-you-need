#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_FILE="${ROOT_DIR}/README.md"

LANG_NAV='[English](./README.md) | [한국어](./README.kr.md) | [日本語](./README.jp.md) | [中文](./README.zh.md) | [Français](./README.fr.md)'

usage() {
  cat <<USAGE
Usage:
  scripts/readme_i18n_sync.sh --engine <codex|claude|copilot|gemini>

Default commands by engine:
  codex   -> codex
  claude  -> claude
  copilot -> copilot
  gemini  -> gemini

Optional override env vars:
  codex   -> README_I18N_CODEX_CMD
  claude  -> README_I18N_CLAUDE_CMD
  copilot -> README_I18N_COPILOT_CMD
  gemini  -> README_I18N_GEMINI_CMD

Contract:
- The configured command must read prompt text from stdin.
- It must print translated markdown to stdout.
USAGE
}

ENGINE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --engine)
      ENGINE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "${ENGINE}" ]]; then
  echo "--engine is required." >&2
  usage
  exit 1
fi

if [[ ! -f "${SOURCE_FILE}" ]]; then
  echo "Missing source file: ${SOURCE_FILE}" >&2
  exit 1
fi

case "${ENGINE}" in
  codex)
    CMD="${README_I18N_CODEX_CMD:-codex}"
    ;;
  claude)
    CMD="${README_I18N_CLAUDE_CMD:-claude}"
    ;;
  copilot)
    CMD="${README_I18N_COPILOT_CMD:-copilot}"
    ;;
  gemini)
    CMD="${README_I18N_GEMINI_CMD:-gemini}"
    ;;
  *)
    echo "Unsupported engine: ${ENGINE}" >&2
    exit 1
    ;;
esac

SOURCE_CONTENT="$(cat "${SOURCE_FILE}")"

translate_one() {
  local language="$1"
  local outfile="$2"
  local prompt

  read -r -d '' prompt <<PROMPT || true
You are translating markdown documentation.

Rules:
- Preserve markdown structure exactly.
- Keep links, URLs, file paths, code blocks, inline code, and table structure unchanged.
- Translate prose only.
- Do not add or remove sections.

Target language: ${language}
Target file: ${outfile}

Return markdown only.

---BEGIN SOURCE README---
${SOURCE_CONTENT}
---END SOURCE README---
PROMPT

  local tmpfile
  tmpfile="$(mktemp)"

  if ! printf '%s\n' "${prompt}" | bash -lc "${CMD}" > "${tmpfile}"; then
    rm -f "${tmpfile}"
    echo "Translation command failed for ${language}." >&2
    exit 1
  fi

  if [[ ! -s "${tmpfile}" ]]; then
    rm -f "${tmpfile}"
    echo "Empty translation output for ${language}." >&2
    exit 1
  fi

  {
    echo "${LANG_NAV}"
    echo
    cat "${tmpfile}"
  } > "${ROOT_DIR}/${outfile}"

  rm -f "${tmpfile}"
}

translate_one "Korean" "README.kr.md"
translate_one "Japanese" "README.jp.md"
translate_one "Chinese (Simplified)" "README.zh.md"
translate_one "French" "README.fr.md"

# Ensure navigation line is present and normalized in all README files.
for f in "${ROOT_DIR}/README.md" "${ROOT_DIR}/README.kr.md" "${ROOT_DIR}/README.jp.md" "${ROOT_DIR}/README.zh.md" "${ROOT_DIR}/README.fr.md"; do
  if [[ -f "$f" ]]; then
    awk -v nav="${LANG_NAV}" 'NR==1{print nav; if ($0 != "") print ""; next} {print}' "$f" > "$f.tmp"
    mv "$f.tmp" "$f"
  fi
done

echo "README translations synced with engine: ${ENGINE}"
