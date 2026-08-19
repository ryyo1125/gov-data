#!/usr/bin/env bash
# build.py を編集したら、その検査が今も効くかを確かめる（PostToolUse / Edit|Write）。
#
# 台帳の規律はすべて build.py の検査に依存している。検査を壊すと、規律を破った
# エントリが黙って通るようになり、しかも通ってしまうので誰も気づけない。
# 編集した直後に、落ちるべき条件で実際に落ちることを確かめる。
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

file="$(jq -r '.tool_response.filePath // .tool_input.file_path // empty')"
case "${file#"$REPO_ROOT"/}" in
  registry/build.py) ;;
  *) exit 0 ;;
esac

[ -x "$REPO_ROOT/.work/toolvenv/bin/python" ] || exit 0

output="$(bash "$REPO_ROOT/registry/test_build.sh" 2>&1)"
if [ $? -eq 0 ]; then
  jq -n '{systemMessage: "build.py の検査は引き続き期待どおり動いています（registry/test_build.sh）"}'
else
  jq -n --arg out "$output" '{
    decision: "block",
    reason: ("build.py の検査が期待どおり動かなくなりました。registry/test_build.sh の結果:\n" + $out)
  }'
fi
