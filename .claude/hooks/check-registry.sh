#!/usr/bin/env bash
# 台帳の生成物が最新かを確かめ、古ければ作業を続けさせる（Stop）。
#
# 「エントリを直したがビルドし忘れた」は静かに起きる。台帳が実測と食い違ったまま
# コミットされると、この台帳が防ごうとしている「腐ったことに気づけない」状態に
# そのまま落ちる。ターンを終える前に機械で気づかせる。
#
# 台帳に関係ない作業まで止めないよう、対象ディレクトリに変更があるときだけ見る。
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON="$REPO_ROOT/.work/toolvenv/bin/python"
cd "$REPO_ROOT" || exit 0

[ -x "$PYTHON" ] || exit 0
git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1 || exit 0

# 台帳まわりを触っていないターンでは何も言わない。
changed="$(git -C "$REPO_ROOT" status --porcelain -- registry verify results docs 2>/dev/null)"
[ -n "$changed" ] || exit 0

output="$("$PYTHON" registry/build.py --check 2>&1)"
status=$?
[ "$status" -eq 0 ] && exit 0

jq -n --arg out "$output" '{
  decision: "block",
  reason: ("台帳の生成物が最新ではありません。registry/build.py を実行してから終えてください。\n" + $out)
}'
