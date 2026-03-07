#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_DIR="$ROOT_DIR/backend"
ROOT_ENV_FILE="$ROOT_DIR/.env"
BACKEND_ENV_FILE="$BACKEND_DIR/.env"
RUNTIME_DIR="$ROOT_DIR/.runtime"
PID_FILE="$RUNTIME_DIR/backend.pid"
LOG_FILE="$RUNTIME_DIR/backend.log"
VENV_DIR="$BACKEND_DIR/.venv"
FRONTEND_DIST_DIR="$FRONTEND_DIR/dist"

mkdir -p "$RUNTIME_DIR"

if [[ -f "$BACKEND_ENV_FILE" ]]; then
  ENV_FILE="$BACKEND_ENV_FILE"
elif [[ -f "$ROOT_ENV_FILE" ]]; then
  ENV_FILE="$ROOT_ENV_FILE"
else
  echo "No .env found at $BACKEND_ENV_FILE or $ROOT_ENV_FILE"
  exit 1
fi

PORT="$(awk -F= '$1=="PORT" {print $2}' "$ENV_FILE" | tr -d '[:space:]' | tail -n 1)"
PORT="${PORT:-8000}"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  PYTHON_BIN="python"
fi

if ! "$PYTHON_BIN" -m venv --help >/dev/null 2>&1; then
  echo "[deploy] Python venv module is unavailable. Install it with: sudo apt install python3-venv"
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "[deploy] Creating backend virtual environment at $VENV_DIR..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

VENV_PYTHON="$VENV_DIR/bin/python"

echo "[deploy] Checking frontend build..."
if [[ ! -f "$FRONTEND_DIST_DIR/index.html" ]]; then
  echo "[deploy] Missing frontend build at $FRONTEND_DIST_DIR"
  echo "[deploy] Build it on a machine with npm using: ./scripts/build-frontend.sh"
  exit 1
fi
echo "[deploy] Using prebuilt frontend from $FRONTEND_DIST_DIR"

echo "[deploy] Installing backend dependencies..."
(
  cd "$BACKEND_DIR"
  "$VENV_PYTHON" -m pip install --upgrade pip
  "$VENV_PYTHON" -m pip install -r requirements.txt
)

if [[ -f "$PID_FILE" ]]; then
  OLD_PID="$(cat "$PID_FILE")"
  if kill -0 "$OLD_PID" >/dev/null 2>&1; then
    echo "[deploy] Stopping existing backend process (pid $OLD_PID)..."
    kill "$OLD_PID"
    sleep 1
    if kill -0 "$OLD_PID" >/dev/null 2>&1; then
      kill -9 "$OLD_PID"
    fi
  fi
fi

echo "[deploy] Starting backend on port $PORT..."
(
  cd "$BACKEND_DIR"
  set -a
  source "$ENV_FILE"
  set +a

  if ! getent hosts "${ORACLE_HOST:-}" >/dev/null 2>&1; then
    echo "[deploy][warn] Cannot resolve ORACLE_HOST='${ORACLE_HOST:-}'."
    echo "[deploy][warn] If you are off-campus/WSL, create a DB tunnel first (e.g. scripts/mac/db-tunnel.sh)."
  fi

  nohup "$VENV_PYTHON" -m uvicorn main:app --host 0.0.0.0 --port "$PORT" >"$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
)

echo "[deploy] Done"
echo "[deploy] Backend PID: $(cat "$PID_FILE")"
echo "[deploy] Log file: $LOG_FILE"
echo "[deploy] URL: http://<server-host>:$PORT"
