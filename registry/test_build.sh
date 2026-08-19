#!/usr/bin/env bash
# build.py が落ちるべき条件で落ち、落ちてはいけない条件で落ちないことを確かめる。
#
# 台帳の規律はすべて build.py の検査に依存している。検査が壊れると、
# 規律を破ったエントリが黙って通ってしまい、台帳が嘘をつき始める。
# 文書に「こうすると落ちる」と書いた条件は、ここで実際に壊して確かめる。
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-$REPO_ROOT/.work/toolvenv/bin/python}"
BACKUP="$(mktemp -d)"
TARGET="registry/sources/jma-xml.yaml"
cd "$REPO_ROOT"

cp -r registry/sources "$BACKUP/sources"
cp -r results "$BACKUP/results"
cp verify/run_all.sh "$BACKUP/run_all.sh"
restore() {
  rm -rf registry/sources results
  cp -r "$BACKUP/sources" registry/sources
  cp -r "$BACKUP/results" results
  cp "$BACKUP/run_all.sh" verify/run_all.sh
}
trap 'restore; rm -rf "$BACKUP"' EXIT

failures=0
expect() {
  local want="$1" desc="$2"; shift 2
  "$@" >/dev/null 2>&1
  "$PYTHON" registry/build.py >/dev/null 2>&1
  local got=$?
  restore
  if { [ "$want" = fail ] && [ "$got" -ne 0 ]; } || { [ "$want" = pass ] && [ "$got" -eq 0 ]; }; then
    printf "  [OK  ] %s\n" "$desc"
  else
    printf "  [FAIL] %s（期待 %s / 実際 exit=%s）\n" "$desc" "$want" "$got"
    failures=$((failures + 1))
  fi
}

echo "落ちるべき条件:"
expect fail "スキーマ違反（列挙値）" sed -i 's/  auth: not_required/  auth: bogus/' "$TARGET"
expect fail "status の手書き" bash -c "printf '\nstatus: verified\n' >> $TARGET"
expect fail "id とファイル名の不一致" sed -i 's/^id: jma-xml/id: jma-xml-x/' "$TARGET"
expect fail "verify.script が存在しない" sed -i 's|verify/verify_jma_xml.py|verify/absent.py|' "$TARGET"
expect fail "run_all.sh から呼ばれない" sed -i 's|verify_jma_xml.py|verify_absent.py|' verify/run_all.sh
expect fail "結果の source_id 不一致" "$PYTHON" -c "
import json; p='results/jma-xml.json'; d=json.load(open(p)); d['source_id']='WRONG'
json.dump(d, open(p,'w'), ensure_ascii=False)"
expect fail "measured の数値が結果に無い" "$PYTHON" -c "
import pathlib; p=pathlib.Path('$TARGET'); p.write_text(p.read_text().replace('  measured: []','  measured: [\"99999 件\"]'))"

echo "落ちてはいけない条件:"
expect pass "結果ファイルがまだ無い（未検証）" rm results/jma-xml.json
expect pass "coverage の自然文に数値がある" "$PYTHON" -c "
import pathlib; p=pathlib.Path('$TARGET'); p.write_text(p.read_text().replace('4 系統','4 系統・2 種類・10 区分'))"
expect pass "無変更" true

[ "$failures" -eq 0 ] && echo "すべて期待どおり" || echo "$failures 件が期待と違う"
exit "$failures"
