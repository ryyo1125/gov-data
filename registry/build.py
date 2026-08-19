#!/usr/bin/env python3
"""台帳エントリを検証し、検証結果とマージして registry.json と REGISTRY.md を生成する。

台帳の設計上の要は「検証ステータスを人が書けない」ことにある。
registry/sources/*.yaml には事実と、検証を再現するためのポインタだけを書く。
合否・検証日・所要時間は results/ の JSON からこのスクリプトが導出する。

    python registry/build.py            # 生成する
    python registry/build.py --check    # 生成物が最新かだけを確認する（CI 用）
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = REPO_ROOT / "registry" / "sources"
SCHEMA_PATH = REPO_ROOT / "registry" / "schema.json"
REGISTRY_JSON = REPO_ROOT / "registry" / "registry.json"
REGISTRY_MD = REPO_ROOT / "docs" / "REGISTRY.md"

# 検証結果がこれより古ければ stale。政府 API の仕様変更に気づける程度の間隔。
STALE_AFTER = timedelta(days=90)

# 人が書いてはいけないキー。書かれていたら台帳の前提が壊れているので即エラーにする。
GENERATED_KEYS = ("verification", "status", "verified_at")

STATUS_LABEL = {
    "verified": "検証済",
    "stale": "要再検証",
    "failed": "失敗あり",
    "unverified": "未検証",
}


def load_entries() -> tuple[list[dict], list[str]]:
    """sources/*.yaml を読み、スキーマ検証を通してエントリ一覧とエラー一覧を返す。"""
    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    entries: list[dict] = []
    errors: list[str] = []

    for path in sorted(SOURCES_DIR.glob("*.yaml")):
        rel = path.relative_to(REPO_ROOT)
        entry = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(entry, dict):
            errors.append(f"{rel}: YAML のトップレベルがマッピングではない")
            continue

        for key in GENERATED_KEYS:
            if key in entry:
                errors.append(
                    f"{rel}: '{key}' は build.py が生成するキーであり、手で書いてはいけない"
                )

        for error in sorted(validator.iter_errors(entry), key=lambda e: list(e.path)):
            location = ".".join(str(p) for p in error.path) or "(root)"
            errors.append(f"{rel}: {location}: {error.message}")

        if entry.get("id") != path.stem:
            errors.append(f"{rel}: id '{entry.get('id')}' がファイル名 '{path.stem}' と一致しない")

        script = REPO_ROOT / entry.get("verify", {}).get("script", "")
        if not script.is_file():
            errors.append(f"{rel}: verify.script が存在しない: {entry.get('verify', {}).get('script')}")

        entries.append(entry)

    return entries, errors


def derive_verification(entry: dict, now: datetime) -> dict:
    """results/ の JSON から検証ステータスを導出する。台帳の合否はここでしか決まらない。"""
    rel = entry["verify"]["result"]
    path = REPO_ROOT / rel
    if not path.is_file():
        return {"status": "unverified", "reason": f"検証結果が存在しない: {rel}"}

    result = json.loads(path.read_text(encoding="utf-8"))
    summary = result.get("summary", {})
    generated_at = result.get("generated_at")

    if result.get("source_id") != entry["id"]:
        return {
            "status": "unverified",
            "reason": f"{rel} の source_id '{result.get('source_id')}' がエントリ id と一致しない",
        }

    if summary.get("failed", 0) > 0:
        status = "failed"
    elif not generated_at:
        status = "unverified"
    elif now - datetime.fromisoformat(generated_at) > STALE_AFTER:
        status = "stale"
    else:
        status = "verified"

    return {
        "status": status,
        "verified_at": generated_at,
        "environment": result.get("environment"),
        "summary": summary,
        "steps": [
            {
                "step": s["step"],
                "outcome": "skipped" if s.get("skipped") else ("ok" if s.get("ok") else "failed"),
                "elapsed_ms": s.get("elapsed_ms"),
                "note": s.get("note") or s.get("error"),
            }
            for s in result.get("steps", [])
        ],
        "result_file": rel,
    }


def build_registry(entries: list[dict], now: datetime) -> dict:
    return {
        "generated_at": now.isoformat(timespec="seconds"),
        "generated_by": "registry/build.py",
        "stale_after_days": STALE_AFTER.days,
        "sources": [{**entry, "verification": derive_verification(entry, now)} for entry in entries],
    }


def render_markdown(registry: dict) -> str:
    lines = [
        "# 情報源台帳",
        "",
        "**このファイルは `registry/build.py` が生成する。直接編集しても次回のビルドで失われる。**",
        "内容を変えるときは `registry/sources/*.yaml` を編集し、検証結果を更新するときは",
        "各エントリの再現コマンドを実行して `results/` を更新する。",
        "",
        f"- 生成日時: {registry['generated_at']}",
        f"- 再検証の目安: 最終検証から {registry['stale_after_days']} 日",
        "",
        "## 一覧",
        "",
        "| ID | 名称 | 提供元 | 権威性 | 方式 | 認証 | 出典表示 | 状態 | 最終検証 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for s in registry["sources"]:
        v = s["verification"]
        summary = v.get("summary") or {}
        state = STATUS_LABEL.get(v["status"], v["status"])
        if summary:
            state += f" ({summary.get('ok', 0)}/{summary.get('total', 0)})"
        lines.append(
            f"| `{s['id']}` | {s['name']} | {s['data_source']['provider']} "
            f"| {s['data_source']['authority']} | {s['access']['method']} "
            f"| {s['requirements']['auth']} | {s['requirements']['attribution_required']} "
            f"| {state} | {(v.get('verified_at') or '-')[:10]} |"
        )

    for s in registry["sources"]:
        lines += _render_entry(s)

    return "\n".join(lines) + "\n"


def _render_entry(s: dict) -> list[str]:
    v = s["verification"]
    req = s["requirements"]
    lines = [
        "",
        f"## {s['name']} (`{s['id']}`)",
        "",
        s["summary"],
        "",
        "### 提供と経路",
        "",
        f"- 提供元: {s['data_source']['provider']}（権威性: `{s['data_source']['authority']}`）",
        f"- 一次情報: {s['data_source']['primary_source_url']}",
        f"- 方式: `{s['access']['method']}` / エンドポイント: `{s['access']['endpoint']}`",
    ]
    if s["access"].get("spec_url"):
        version = s["access"].get("spec_version")
        lines.append(f"- 仕様: {s['access']['spec_url']}" + (f"（{version}）" if version else ""))
    impl = s["access"].get("implementation")
    if impl:
        lines.append(
            f"- 実装: {impl['name']}（保守: {impl['maintainer']}"
            + (f" / {impl['license']}" if impl.get("license") else "")
            + (f" / 検証時 {impl['version_verified']}" if impl.get("version_verified") else "")
            + "）"
        )

    lines += [
        "",
        "### 提供される情報",
        "",
        f"- 種類: {' / '.join(s['content']['categories'])}",
        f"- 形式: {' / '.join(s['content']['formats'])}",
        f"- 更新頻度: {s['content']['update_frequency']}",
        f"- 収録範囲: {s['content']['coverage']}",
        "",
        "### 接続要件",
        "",
        f"- 認証: `{req['auth']}`" + (f" — {req['auth_note']}" if req.get("auth_note") else ""),
        f"- レート制限: {req['rate_limit']}",
        f"- 利用規約: {req['terms_url'] or '未確認'}",
        f"- 出典表示: `{req['attribution_required']}`"
        + (f" — {req['attribution_text']}" if req.get("attribution_text") else ""),
    ]
    if req.get("credential_env"):
        lines.append(f"- 必要な環境変数: {', '.join(f'`{e}`' for e in req['credential_env'])}")

    if s["stability"]["notes"]:
        lines += ["", "### 安定性（一次資料の記述）", ""]
        lines += [f"- {n}" for n in s["stability"]["notes"]]

    lines += ["", "### 到達性", "", "| ホスト | 役割 | 備考 |", "|---|---|---|"]
    lines += [
        f"| `{h['host']}` | {h['role']} | {h.get('note', '')} |" for h in s["reachability"]["hosts"]
    ]

    lines += [
        "",
        "### 検証",
        "",
        f"- 状態: **{STATUS_LABEL.get(v['status'], v['status'])}**"
        + (f" — {v['reason']}" if v.get("reason") else ""),
        f"- 最終検証: {v.get('verified_at') or '-'}",
        f"- 再現コマンド: `{s['verify']['command']}`",
        f"- 検証スクリプト: `{s['verify']['script']}` / 結果: `{s['verify']['result']}`",
    ]
    if v.get("environment"):
        lines.append(f"- 検証環境: Python {v['environment'].get('python')} / {v['environment'].get('platform')}")
    if v.get("steps"):
        lines += ["", "| ステップ | 結果 | 所要 | 備考 |", "|---|---|---|---|"]
        mark = {"ok": "OK", "skipped": "SKIP", "failed": "FAIL"}
        lines += [
            f"| `{st['step']}` | {mark[st['outcome']]} "
            f"| {str(st['elapsed_ms']) + ' ms' if st.get('elapsed_ms') is not None else '-'} "
            f"| {st.get('note') or ''} |"
            for st in v["steps"]
        ]

    lines += ["", "### 実行して分かったこと", ""]
    for f in s["findings"]:
        lines += [f"- **{f['claim']}**", f"  - 根拠: {f['evidence']}"]
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="生成せず、生成物が最新かだけ確認する")
    args = parser.parse_args()

    entries, errors = load_entries()
    if errors:
        print("台帳エントリの検証に失敗:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    registry = build_registry(entries, datetime.now(timezone.utc))
    markdown = render_markdown(registry)
    # generated_at は毎回変わるため、最新かどうかの比較からは外す。
    comparable = {k: v for k, v in registry.items() if k != "generated_at"}

    if args.check:
        stale = []
        if not REGISTRY_JSON.is_file():
            stale.append(str(REGISTRY_JSON.relative_to(REPO_ROOT)))
        else:
            current = json.loads(REGISTRY_JSON.read_text(encoding="utf-8"))
            if {k: v for k, v in current.items() if k != "generated_at"} != comparable:
                stale.append(str(REGISTRY_JSON.relative_to(REPO_ROOT)))
        if not REGISTRY_MD.is_file() or _strip_generated_at(REGISTRY_MD.read_text(encoding="utf-8")) != _strip_generated_at(markdown):
            stale.append(str(REGISTRY_MD.relative_to(REPO_ROOT)))
        if stale:
            print("生成物が最新ではない: " + ", ".join(stale), file=sys.stderr)
            print("registry/build.py を実行して更新すること", file=sys.stderr)
            return 1
        print(f"{len(entries)} 件のエントリ、生成物は最新")
        return 0

    REGISTRY_JSON.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    REGISTRY_MD.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_MD.write_text(markdown, encoding="utf-8")

    for s in registry["sources"]:
        v = s["verification"]
        print(f"  {s['id']}: {v['status']}" + (f" ({v['reason']})" if v.get("reason") else ""))
    print(f"{len(entries)} 件 -> {REGISTRY_JSON.relative_to(REPO_ROOT)}, {REGISTRY_MD.relative_to(REPO_ROOT)}")
    return 0


def _strip_generated_at(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.startswith("- 生成日時:"))


if __name__ == "__main__":
    sys.exit(main())
