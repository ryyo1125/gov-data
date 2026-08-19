#!/usr/bin/env bash
# 生成物への手編集を拒否する（PreToolUse / Edit|Write）。
#
# 台帳の設計は「生成物は results と sources からしか作られない」という一点に
# 依存している。生成物を手で直すと、次のビルドで消えるだけでなく、消えるまでの
# あいだ台帳が実測と食い違った内容を主張する。人の注意力ではなく機械で止める。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
GENERATED="docs/REGISTRY.md docs/FIELDS.md registry/registry.json"

file="$(jq -r '.tool_input.file_path // empty')"
[ -n "$file" ] || exit 0

# 絶対パス・相対パスのどちらで来ても比較できるようにリポジトリ相対へ寄せる。
rel="${file#"$REPO_ROOT"/}"
rel="${rel#./}"

for generated in $GENERATED; do
  if [ "$rel" = "$generated" ]; then
    jq -n --arg f "$rel" '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: ($f + " は registry/build.py の生成物です。手で編集しても次のビルドで失われます。内容を変えるには registry/sources/*.yaml か results/ を直してから registry/build.py を実行してください。")
      }
    }'
    exit 0
  fi
done
exit 0
