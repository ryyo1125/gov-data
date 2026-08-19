#!/usr/bin/env bash
# 引き継ぎを残さずセッションを終えそうなときに一度だけ知らせる（Stop）。
#
# コンテナが作り直されると、diary に書かれなかった経緯は失われる。ただし毎ターン
# 催促すると邪魔なので、セッション中に一度だけ、かつ最新の diary より後に
# コミットが進んでいるときに限る。ブロックはしない — 引き継ぎを書くかどうかは
# 作業の区切り方の問題で、機械が決めることではない。
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SENTINEL="$REPO_ROOT/.work/handoff-reminded"
cd "$REPO_ROOT" || exit 0

[ -f "$SENTINEL" ] && exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

head_commit="$(git rev-parse --short HEAD 2>/dev/null)" || exit 0
latest="$(ls -1 "$REPO_ROOT/.claude/diary"/*.md 2>/dev/null | sort | tail -1)"

if [ -n "$latest" ]; then
  recorded="$(sed -n 's/^commit: *//p' "$latest" | head -1)"
  # 最新の diary が現在の HEAD を指しているなら、引き継ぎは追いついている。
  [ "$recorded" = "$head_commit" ] && exit 0
  message="最新の引き継ぎ（$(basename "$latest")）は $recorded 時点のものですが、HEAD は $head_commit まで進んでいます。区切りがついたら /handoff で引き継ぎを更新してください。"
else
  message="このリポジトリにはまだ引き継ぎ（.claude/diary/）がありません。区切りがついたら /handoff で残してください。コンテナは作り直されるので、書かれなかった経緯は失われます。"
fi

mkdir -p "$(dirname "$SENTINEL")" && touch "$SENTINEL"
jq -n --arg m "$message" '{systemMessage: $m}'
