#!/usr/bin/env bash
# 台帳に載っている全情報源を再検証し、台帳を再生成する。
# 定期実行して差分が出たら、提供側の仕様変更を疑う。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="${WORK_DIR:-$REPO_ROOT/.work}"
TOOL_VENV="$WORK_DIR/toolvenv"
# 項目抽出のあいだだけ Jグランツ MCP を起動する。検証用の PORT とは別にして衝突を避ける。
FIELDS_PORT="${FIELDS_PORT:-8321}"

mkdir -p "$WORK_DIR"
[ -d "$TOOL_VENV" ] || uv venv "$TOOL_VENV"
uv pip install --python "$TOOL_VENV/bin/python" -q \
  -r "$REPO_ROOT/registry/requirements.txt" -r "$REPO_ROOT/verify/requirements.txt" httpx

echo "== 到達性 =="
"$TOOL_VENV/bin/python" "$REPO_ROOT/verify/verify_reachability.py" \
  --out "$REPO_ROOT/results/reachability.json"

echo "== egov-hourei-api =="
"$TOOL_VENV/bin/python" "$REPO_ROOT/verify/verify_egov_hourei.py" \
  --out "$REPO_ROOT/results/egov-hourei-api.json"

echo "== egov-data-catalog =="
"$TOOL_VENV/bin/python" "$REPO_ROOT/verify/verify_egov_data_catalog.py" \
  --out "$REPO_ROOT/results/egov-data-catalog.json"

echo "== jma-xml =="
"$TOOL_VENV/bin/python" "$REPO_ROOT/verify/verify_jma_xml.py" \
  --out "$REPO_ROOT/results/jma-xml.json"

echo "== jgrants-mcp =="
"$REPO_ROOT/verify/run_jgrants_verification.sh"

# 項目一覧の抽出。Jグランツだけ MCP サーバーが要るので、ここで一時的に起動する。
echo "== 取得できる項目の抽出 =="
JGRANTS_DIR="$WORK_DIR/jgrants-mcp-server"
if [ -d "$JGRANTS_DIR" ]; then
  # -m はパッケージをリポジトリ直下から解決するため、サーバーの clone 先で実行する。
  (
    cd "$JGRANTS_DIR" &&
    JGRANTS_FILES_DIR="$WORK_DIR/jgrants_files" \
      .venv/bin/python -m jgrants_mcp_server.core \
      --host 127.0.0.1 --port "$FIELDS_PORT"
  ) > "$WORK_DIR/fields-server.log" 2>&1 &
  FIELDS_PID=$!
  trap 'pkill -P "$FIELDS_PID" 2>/dev/null; kill "$FIELDS_PID" 2>/dev/null || true' EXIT
  for _ in $(seq 30); do
    if curl -s -o /dev/null --noproxy '*' "http://127.0.0.1:$FIELDS_PORT/mcp"; then break; fi
    sleep 1
  done
  "$TOOL_VENV/bin/python" "$REPO_ROOT/verify/extract_fields.py" \
    --jgrants-url "http://127.0.0.1:$FIELDS_PORT/mcp" --out "$REPO_ROOT/results/fields.json"
else
  "$TOOL_VENV/bin/python" "$REPO_ROOT/verify/extract_fields.py" \
    --out "$REPO_ROOT/results/fields.json"
fi

echo "== 台帳の再生成 =="
"$TOOL_VENV/bin/python" "$REPO_ROOT/registry/build.py"
