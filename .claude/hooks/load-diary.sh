#!/usr/bin/env bash
# 前回セッションの引き継ぎを読み込む（SessionStart）。
#
# コンテナは毎回作り直されるため、前回の文脈はリポジトリに書かれたものしか残らない。
# 読むかどうかを判断に委ねると読み飛ばされるので、開始時に機械的に流し込む。
# ただし diary は「書かれた時点のスナップショット」であって現在の状態ではない。
# 鵜呑みにさせないための注意書きを必ず添える。
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DIARY_DIR="$REPO_ROOT/.claude/diary"
# 開始時に流し込む量の上限。長すぎる引き継ぎは読まれないし、毎回の文脈を圧迫する。
MAX_LINES=200

# 前セッションの handoff 催促フラグを落とす（催促はセッションごとに一度だけ）。
rm -f "$REPO_ROOT/.work/handoff-reminded" 2>/dev/null || true

latest="$(ls -1 "$DIARY_DIR"/*.md 2>/dev/null | sort | tail -1)"
[ -n "$latest" ] || exit 0

name="$(basename "$latest")"
body="$(head -n "$MAX_LINES" "$latest")"
total="$(wc -l < "$latest" | tr -d ' ')"
if [ "$total" -gt "$MAX_LINES" ]; then
  body="$body

（$MAX_LINES 行までを表示。全文は $latest を読むこと）"
fi

jq -n --arg name "$name" --arg body "$body" '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: ("前回セッションの引き継ぎ（.claude/diary/" + $name + "）:\n\n" + $body +
      "\n\n---\nこれは書かれた時点のスナップショットであり、現在の状態ではない。着手前に git log と git status で実測して確かめること。より遡って読むには /activate を使う。作業を終えるときは /handoff で次への引き継ぎを残す。")
  }
}'
