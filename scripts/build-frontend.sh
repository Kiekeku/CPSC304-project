#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"

if ! command -v npm >/dev/null 2>&1; then
  echo "[build-frontend] npm is not installed on this machine."
  exit 1
fi

echo "[build-frontend] Installing frontend dependencies..."
(
  cd "$FRONTEND_DIR"
  npm install
)

echo "[build-frontend] Building frontend bundle..."
(
  cd "$FRONTEND_DIR"
  npm run build
)

echo "[build-frontend] Done: $FRONTEND_DIR/dist"
