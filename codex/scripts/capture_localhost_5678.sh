#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
URL="${1:-http://localhost:5678}"
OUTPUT_PATH="${2:-$ROOT_DIR/docs/images/localhost-5678.png}"

if ! command -v node >/dev/null 2>&1; then
  echo "Error: node is required."
  echo "Install Node.js first, then retry."
  exit 1
fi

if ! command -v npx >/dev/null 2>&1; then
  echo "Error: npx is required."
  echo "Install npm (includes npx) first, then retry."
  exit 1
fi

if ! curl -fsS --max-time 5 "$URL" >/dev/null; then
  echo "Error: cannot reach $URL"
  echo "Start SiteBooker on port 5678 and retry."
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT_PATH")"

echo "Capturing $URL -> $OUTPUT_PATH"
npx --yes playwright@1.54.2 screenshot --full-page "$URL" "$OUTPUT_PATH"
echo "Done."

