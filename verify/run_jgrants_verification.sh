#!/usr/bin/env bash
# デジタル庁 Jグランツ MCP Server を取得・起動し、接続検証を実行する。
#
#   ./verify/run_jgrants_verification.sh [作業ディレクトリ]
#
# 既定の作業ディレクトリは ./.work（.gitignore 済み）。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="${1:-$REPO_ROOT/.work}"
SERVER_DIR="$WORK_DIR/jgrants-mcp-server"
PORT="${PORT:-8000}"
KEYWORD="${KEYWORD:-IT導入}"
OUT="${OUT:-$REPO_ROOT/results/jgrants-mcp.json}"

mkdir -p "$WORK_DIR" "$(dirname "$OUT")"

if [ ! -d "$SERVER_DIR" ]; then
  git clone --depth 1 https://github.com/digital-go-jp/jgrants-mcp-server.git "$SERVER_DIR"
fi

cd "$SERVER_DIR"
[ -d .venv ] || uv venv
uv pip install -r requirements.txt -r "$REPO_ROOT/verify/requirements.txt"

# MCP サーバーは 127.0.0.1 で待ち受けるため、プロキシ経由にならないよう除外する。
export NO_PROXY="${NO_PROXY:-},127.0.0.1,localhost"
export no_proxy="$NO_PROXY"
export JGRANTS_FILES_DIR="$WORK_DIR/jgrants_files"

.venv/bin/python -m jgrants_mcp_server.core --host 127.0.0.1 --port "$PORT" > "$WORK_DIR/server.log" 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT

for _ in $(seq 30); do
  if curl -s -o /dev/null --noproxy '*' "http://127.0.0.1:$PORT/mcp"; then break; fi
  sleep 1
done

.venv/bin/python "$REPO_ROOT/verify/verify_jgrants_mcp.py" \
  --url "http://127.0.0.1:$PORT/mcp" --keyword "$KEYWORD" --out "$OUT"
