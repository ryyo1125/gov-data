#!/usr/bin/env bash
# .work/toolvenv を用意する（SessionStart）。
#
# 検証もビルドもこの venv の python で動く。システムの python には httpx も
# PyYAML も入っていないため、無い状態では文書に書かれたコマンドが軒並み失敗する。
# コンテナは毎回作り直されるので、セッション開始時に必ず整える。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOL_VENV="$REPO_ROOT/.work/toolvenv"

command -v uv >/dev/null 2>&1 || exit 0

mkdir -p "$REPO_ROOT/.work"
[ -x "$TOOL_VENV/bin/python" ] || uv venv "$TOOL_VENV" >/dev/null 2>&1
uv pip install --python "$TOOL_VENV/bin/python" -q \
  -r "$REPO_ROOT/registry/requirements.txt" \
  -r "$REPO_ROOT/verify/requirements.txt" httpx >/dev/null 2>&1 || exit 0

jq -n '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: "検証とビルドには .work/toolvenv/bin/python を使うこと（システムの python には httpx も PyYAML も無い）。この venv はセッション開始時に用意済み。"
  }
}'
