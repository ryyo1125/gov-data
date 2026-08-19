#!/usr/bin/env bash
# 台帳に載っている全情報源を再検証し、台帳を再生成する。
# 定期実行して差分が出たら、提供側の仕様変更を疑う。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="${WORK_DIR:-$REPO_ROOT/.work}"
TOOL_VENV="$WORK_DIR/toolvenv"

mkdir -p "$WORK_DIR"
[ -d "$TOOL_VENV" ] || uv venv "$TOOL_VENV"
uv pip install --python "$TOOL_VENV/bin/python" -q \
  -r "$REPO_ROOT/registry/requirements.txt" httpx

echo "== egov-hourei-api =="
"$TOOL_VENV/bin/python" "$REPO_ROOT/verify/verify_egov_hourei.py" \
  --out "$REPO_ROOT/results/egov-hourei-api.json"

echo "== jgrants-mcp =="
"$REPO_ROOT/verify/run_jgrants_verification.sh"

echo "== 台帳の再生成 =="
"$TOOL_VENV/bin/python" "$REPO_ROOT/registry/build.py"
