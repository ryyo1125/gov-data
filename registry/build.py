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
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = REPO_ROOT / "registry" / "sources"
SCHEMA_PATH = REPO_ROOT / "registry" / "schema.json"
BLOCKED_PATH = REPO_ROOT / "registry" / "blocked.yaml"
REACHABILITY_PATH = REPO_ROOT / "results" / "reachability.json"
FIELDS_PATH = REPO_ROOT / "results" / "fields.json"
SURVEY_PATH = REPO_ROOT / "results" / "catalog-survey.json"
REGISTRY_JSON = REPO_ROOT / "registry" / "registry.json"
REGISTRY_MD = REPO_ROOT / "docs" / "REGISTRY.md"
FIELDS_MD = REPO_ROOT / "docs" / "FIELDS.md"
SURVEY_MD = REPO_ROOT / "docs" / "SURVEY.md"
MACHINE_MD = REPO_ROOT / "docs" / "MACHINE_READABLE.md"

# 検証結果がこれより古ければ stale。政府 API の仕様変更に気づける程度の間隔。
STALE_AFTER = timedelta(days=90)

# 人が書いてはいけないキー。書かれていたら台帳の前提が壊れているので即エラーにする。
GENERATED_KEYS = ("verification", "status", "verified_at")

STATUS_LABEL = {
    "verified": "検証済",
    "stale": "要再検証",
    "failed": "失敗あり",
    "blocked": "到達不可（自環境）",
    "unverified": "未検証",
}


def load_entries() -> tuple[list[dict], list[str]]:
    """sources/*.yaml を読み、スキーマ検証を通してエントリ一覧とエラー一覧を返す。"""
    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    runner_scripts = _runner_scripts()
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

        script_rel = entry.get("verify", {}).get("script", "")
        script = REPO_ROOT / script_rel
        if not script.is_file():
            errors.append(f"{rel}: verify.script が存在しない: {script_rel}")
        elif script_rel not in runner_scripts:
            # 再検証の一括実行から漏れると、そのエントリだけ黙って腐る。
            errors.append(
                f"{rel}: verify.script が verify/run_all.sh から実行されない: {script_rel}"
            )

        errors.extend(_result_errors(rel, entry))
        errors.extend(_measured_errors(rel, entry))

        entries.append(entry)

    return entries, errors


def _runner_scripts() -> set[str]:
    """run_all.sh と、そこから呼ばれるシェルスクリプトが実行する検証スクリプトを集める。"""
    text = ""
    pending = [REPO_ROOT / "verify" / "run_all.sh"]
    seen: set[Path] = set()
    while pending:
        path = pending.pop()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        content = path.read_text(encoding="utf-8")
        text += content
        for sibling in (REPO_ROOT / "verify").glob("*.sh"):
            if sibling.name in content:
                pending.append(sibling)
    return {
        f"verify/{path.name}" for path in (REPO_ROOT / "verify").glob("*.py") if path.name in text
    }


def _result_errors(rel: Path, entry: dict) -> list[str]:
    """結果ファイルがあるのに、それがこのエントリのものでない場合はエラーにする。

    結果が「まだ無い」のは未検証という正当な状態だが、別のエントリの結果を
    指してしまうのは設定ミスなので、unverified で流さず気づけるようにする。
    """
    result_rel = entry.get("verify", {}).get("result", "")
    path = REPO_ROOT / result_rel
    if not path.is_file():
        return []
    source_id = json.loads(path.read_text(encoding="utf-8")).get("source_id")
    if source_id != entry.get("id"):
        return [f"{rel}: {result_rel} の source_id '{source_id}' がエントリ id と一致しない"]
    return []


def _measured_errors(rel: Path, entry: dict) -> list[str]:
    """measured に書いた数値が、対応する検証結果に現れるかを確かめる。

    件数を手で書くと必ず腐り、しかも腐っても誰も気づかない。検証していない
    数値を書くことも防ぎたい。ただし自然文から数値を拾うと「4 系統」のような
    件数でない数値まで拾ってしまうため、実測値は measured に隔離して検査する。

    結果ファイルがまだ無いのは未検証という正当な状態なので、ここでは何も言わない。
    """
    measured = entry.get("content", {}).get("measured") or []
    numbers = [n for item in measured for n in re.findall(r"\d[\d,]*", item)]
    path = REPO_ROOT / entry.get("verify", {}).get("result", "")
    if not numbers or not path.is_file():
        return []
    blob = path.read_text(encoding="utf-8")
    missing = [n for n in numbers if n.replace(",", "") not in blob]
    if missing:
        return [
            f"{rel}: measured の数値が検証結果に見当たらない（未検証か陳腐化）: {', '.join(missing)}"
        ]
    return []


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
    elif summary.get("blocked", 0) > 0 and summary.get("ok", 0) == 0:
        # 自環境の egress で 1 つも実行できなかった。先方の問題ではないので failed と分ける。
        status = "blocked"
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


def load_reachability() -> dict[str, dict]:
    """実測した到達性を host -> 結果 の辞書で返す。未実測なら空。"""
    if not REACHABILITY_PATH.is_file():
        return {}
    result = json.loads(REACHABILITY_PATH.read_text(encoding="utf-8"))
    reachability = {}
    for step in result.get("steps", []):
        host = step["step"].split(" ")[0]
        reachability[host] = {
            "reachable": bool(step.get("ok")),
            "blocked_by_egress": bool(step.get("blocked")),
            "detail": step.get("note") or step.get("error") or step.get("result"),
        }
    return {"_generated_at": result.get("generated_at"), **reachability}


def load_blocked(reachability: dict) -> list[dict]:
    """到達不能で保留中の候補を読み、いま昇格可能になっていないかを判定する。"""
    if not BLOCKED_PATH.is_file():
        return []
    blocked = yaml.safe_load(BLOCKED_PATH.read_text(encoding="utf-8")) or {}
    candidates = []
    for candidate in blocked.get("candidates", []):
        hosts = candidate.get("hosts", [])
        measured = [reachability.get(h) for h in hosts]
        # 実測済みで、どのホストも egress に塞がれていなければ検証に進める。
        promotable = bool(measured) and all(
            m is not None and not m["blocked_by_egress"] for m in measured
        )
        candidates.append({**candidate, "promotable": promotable})
    return candidates


def build_registry(entries: list[dict], now: datetime) -> dict:
    reachability = load_reachability()
    return {
        "generated_at": now.isoformat(timespec="seconds"),
        "generated_by": "registry/build.py",
        "stale_after_days": STALE_AFTER.days,
        "sources": [{**entry, "verification": derive_verification(entry, now)} for entry in entries],
        "blocked_candidates": load_blocked(reachability),
        "reachability": reachability,
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

    lines += _render_blocked(registry["blocked_candidates"])
    lines += _render_reachability(registry["reachability"])

    return "\n".join(lines) + "\n"


def _render_blocked(candidates: list[dict]) -> list[str]:
    """到達不能で登録できなかった候補。調査の重複を防ぐために残す。"""
    if not candidates:
        return []
    lines = [
        "",
        "## 保留中の候補（到達不能で未登録）",
        "",
        "検証環境の egress ポリシーで到達できず、事実を書く根拠が得られなかったもの。",
        "台帳に載せていないのは提供が終わっているからではない。",
        "実体は `registry/blocked.yaml`。",
        "",
    ]
    for c in candidates:
        state = "**いま到達可能 — 検証して昇格できる**" if c["promotable"] else "到達不可のまま"
        lines += [
            f"### {c['name']} (`{c['id']}`)",
            "",
            f"- 状態: {state}",
            f"- 調べた理由: {c['why']}",
            f"- 対象ホスト: {', '.join(f'`{h}`' for h in c['hosts'])}",
            f"- 到達できない理由: {c['blocked_reason'].strip()}",
            f"- 次の一手: {c['next_step'].strip()}",
            "",
        ]
    return lines


def _render_reachability(reachability: dict) -> list[str]:
    """ホスト単位の実測。egress の許可リストが変われば、ここが最初に変わる。"""
    hosts = {k: v for k, v in reachability.items() if not k.startswith("_")}
    if not hosts:
        return []
    lines = [
        "",
        "## 到達性の実測",
        "",
        f"`verify/verify_reachability.py` の実測結果（{reachability.get('_generated_at', '-')}）。",
        "到達できないことは、そのサービスが存在しないことを意味しない。",
        "",
        "| ホスト | 結果 | 詳細 |",
        "|---|---|---|",
    ]
    for host, info in sorted(hosts.items()):
        if info["blocked_by_egress"]:
            state = "egress で拒否"
        elif info["reachable"]:
            state = "到達可"
        else:
            state = "不達"
        detail = info["detail"]
        if isinstance(detail, dict):
            detail = f"HTTP {detail.get('status_code')}"
        lines.append(f"| `{host}` | {state} | {detail or ''} |")
    return lines


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
    ]
    if s["content"].get("measured"):
        lines += [f"- 実測値: {m}" for m in s["content"]["measured"]]
    lines += [
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


ORIGIN_LABEL = {
    "spec": "仕様由来（提供側が定義した正式な項目）",
    "observed": "実データ由来（レスポンスを読んで列挙。網羅の保証は無い）",
    "spec+observed": "入力は仕様由来、戻り値は実データ由来",
}


def render_fields(fields: dict, entry_names: dict[str, str]) -> str:
    """取得できる項目の一覧。台帳がエンドポイント粒度で止まる 1 段下を埋める。"""
    lines = [
        "# 取得できる項目の一覧",
        "",
        "**このファイルは `registry/build.py` が `results/fields.json` から生成する。**",
        "更新するには `verify/extract_fields.py` を実行してからビルドし直す。",
        "",
        f"- 生成日時: {fields.get('generated_at', '-')}",
        "",
        "項目の出所は情報源ごとに違う。**仕様由来**は提供側が定義した正式な項目、",
        "**実データ由来**はレスポンスを実際に読んで列挙したもので、サンプルに現れなかった",
        "項目は落ちている可能性がある。どちらなのかを各節の冒頭に示す。",
        "",
        "説明と例はすべて提供側の資料から引いたもので、こちらで補ったものは無い。",
        "説明が空欄の項目は、提供側が定義を公開していないか、まだ見つけられていないもの。",
        "",
    ]

    for source_id, data in fields.get("sources", {}).items():
        name = entry_names.get(source_id, source_id)
        lines += ["", f"## {name} (`{source_id}`)", ""]
        if "error" in data:
            lines += [f"抽出できていない: {data['error']}", ""]
            continue
        lines += [
            f"- 出所: {ORIGIN_LABEL.get(data['origin'], data['origin'])}",
            f"- 抽出方法: {data['origin_detail']}",
            f"- 参照元: {data['source_url']}",
        ]
        for obj in data["objects"]:
            lines += ["", f"### {obj['name']}", ""]
            if obj.get("description"):
                lines += [obj["description"], ""]
            # 例が 1 つも無いオブジェクトで空の列を出すと読みにくいので、あるときだけ列を足す。
            has_example = any(f.get("example") for f in obj["fields"])
            header = "| 項目 | 型 | 説明 | 例 |" if has_example else "| 項目 | 型 | 説明 |"
            lines += [header, "|---|---|---|---|" if has_example else "|---|---|---|"]
            for f in obj["fields"]:
                row = f"| `{f['name']}` | {f['type']} | {f['description']} |"
                if has_example:
                    example = f.get("example") or ""
                    row += f" {'`' + example + '`' if example else ''} |"
                lines.append(row)

        for enum in data["enums"]:
            title = f"{enum['name']}" + (f" — {enum['description']}" if enum.get("description") else "")
            lines += ["", f"### 取りうる値: `{title}`", "", "| 値 | 意味 |", "|---|---|"]
            lines += [f"| `{v['value']}` | {v['meaning']} |" for v in enum["values"]]

    return "\n".join(lines) + "\n"


def render_survey(survey: dict) -> str:
    """カタログ俯瞰。台帳が「検証済みで取れるもの」なら、これは「存在するもの」。"""
    totals = survey["totals"]
    machine = survey["machine_readable"]
    ratio = totals["machine_readable_datasets"] / totals["datasets"] * 100

    lines = [
        "# カタログ俯瞰（何が存在するか）",
        "",
        "**このファイルは `registry/build.py` が `results/catalog-survey.json` から生成する。**",
        "更新するには `verify/survey_catalog.py` を実行してからビルドし直す。",
        "",
        f"- 生成日時: {survey.get('generated_at', '-')}",
        f"- 出所: {survey['source']['name']}（台帳エントリ `{survey['source']['registry_entry']}`）",
        "",
        "台帳（[REGISTRY.md](REGISTRY.md)）が「検証済みで実際に取れるもの」を載せるのに対し、",
        "ここは「存在するが、まだ検証していないもの」も含めた全体像を示す。役割が違うので混ぜない。",
        "",
        "## 規模",
        "",
        f"| データセット | {totals['datasets']:,} 件 |",
        "|---|---|",
        f"| 公開組織 | {totals['organizations']} 組織 |",
        f"| 機械可読な形式を含むもの | {totals['machine_readable_datasets']:,} 件（**{ratio:.1f}%**） |",
    ]
    reachable = machine.get("reachable_datasets")
    hosts = machine.get("resource_hosts") or {}
    if reachable is not None and hosts:
        blocked = {h: i for h, i in hosts.items() if not i["reachable"]}
        lines += [
            f"| うち実ファイルに到達できるもの | {reachable:,} 件 |",
            "",
            "**カタログに載っていることと、実際に取れることは別。** 実ファイルは省庁ごとの",
            f"ホストに置かれており、{len(hosts)} ホスト中 {len(blocked)} ホストへ到達できない。",
            "これは提供が止まっているという意味ではなく、この環境の egress ポリシーで",
            "許可されていないだけなので、許可すれば取得できるようになる。",
            "",
            "| 実ファイルの置き場 | データセット数 | 到達 |",
            "|---|---|---|",
        ]
        lines += [
            f"| `{host}` | {info['datasets']:,} | {'可' if info['reachable'] else '**不可**'} |"
            for host, info in hosts.items()
        ]
    lines += [
        "",
        "**読み方の注意。** 以下の形式別の数はリソース数ではなく、その形式を 1 つ以上持つ",
        "**データセット数**である。1 つのデータセットが PDF と CSV を両方持てば両方に数えられるため、",
        "形式別の合計はデータセット総数を超える。「全リソースの何割が CSV か」とは読めない。",
        "",
        "## 提供形式",
        "",
        "| 形式 | データセット数 | 機械可読 |",
        "|---|---|---|",
    ]
    machine_formats = set(survey["definitions"]["machine_readable"])
    semi = set(survey["definitions"]["semi_structured"])
    for f in survey["by_format"]:
        if f["count"] < 10:
            continue
        kind = "◎" if f["label"] in machine_formats else ("△ 表計算" if f["label"] in semi else "")
        lines.append(f"| {f['label'] or '(空)'} | {f['count']:,} | {kind} |")
    lines += ["", "10 件未満の形式は省略している。全量は `results/catalog-survey.json` を参照。", ""]

    lines += [
        "## 機械可読データの所在",
        "",
        "台帳に昇格させる候補はここから探す。母集団が全体の 1 割に満たないので扱える大きさ。",
        "",
        "| 形式 | データセット数 |",
        "|---|---|",
    ]
    lines += [f"| {fmt} | {count:,} |" for fmt, count in machine["by_format"].items()]
    lines += [
        "",
        "| 組織 | 機械可読を含むデータセット数 |",
        "|---|---|",
    ]
    lines += [f"| {o['label']} | {o['count']:,} |" for o in machine["by_organization"]]

    lines += [
        "",
        "### 話題の内訳",
        "",
        "機械可読データを含むデータセットに付いているタグ（上位 25 件）。",
        "1 つのデータセットが複数のタグを持つため、合計は件数を超える。",
        "",
        "| タグ | データセット数 |",
        "|---|---|",
    ]
    lines += [f"| {t['label']} | {t['count']:,} |" for t in machine.get("by_tag", [])[:25]]
    lines += [
        "",
        f"**全 {len(machine.get('datasets', [])):,} 件の一覧は "
        "[MACHINE_READABLE.md](MACHINE_READABLE.md) にある。**",
        "",
        "### 代表例",
        "",
    ]
    for sample in machine["samples"]:
        lines += [f"**{sample['organization']}**", ""]
        for d in sample["datasets"]:
            formats = " / ".join(d["formats"]) or "-"
            lines.append(
                f"- [{d['title']}]({d['url']}) — {formats}"
                + (f"（更新: {d['frequency_of_update']}）" if d.get("frequency_of_update") else "")
            )
        lines.append("")

    lines += [
        "## 組織別の全体件数",
        "",
        "| 組織 | データセット数 |",
        "|---|---|",
    ]
    lines += [f"| {o['label']} | {o['count']:,} |" for o in survey["by_organization"]]

    lines += [
        "",
        "## 更新頻度",
        "",
        "自由記述のため表記が揺れる（全角と半角、「1年」と「１年」など）。",
        "機械処理するなら正規化が要る。上位 20 件のみ。",
        "",
        "| 記載値 | データセット数 |",
        "|---|---|",
    ]
    lines += [f"| {f['label'] or '(空)'} | {f['count']:,} |" for f in survey["by_update_frequency"][:20]]

    lines += [
        "",
        "## この俯瞰で分からないこと",
        "",
        "- **再配布の可否。** カタログはライセンス情報を実質的に持たない（台帳の",
        "  `egov-data-catalog` の findings を参照）。個々の提供元に当たる必要がある。",
        "- **API かどうか。** 形式に `API` を持つデータセットは存在しない。ここに載るのは",
        "  ファイルの所在であって、機械で叩ける口があるという意味ではない。",
        "- **実際に取得できるか。** 未検証。取れることを確かめたものだけが台帳に載る。",
        "",
    ]
    return "\n".join(lines) + "\n"


def render_machine_readable(survey: dict) -> str:
    """機械可読データを含むデータセットの全件一覧。台帳に昇格させる候補はここから選ぶ。

    SURVEY.md に混ぜると分布が読めなくなるので分けている。こちらは通読するもの
    ではなく、組織を決めてから絞り込んで見るための索引。
    """
    machine = survey["machine_readable"]
    datasets = machine.get("datasets") or []
    by_org: dict[str, list[dict]] = {}
    for d in datasets:
        by_org.setdefault(d.get("organization") or "(組織不明)", []).append(d)

    lines = [
        "# 機械可読データを含むデータセット一覧",
        "",
        "**このファイルは `registry/build.py` が `results/catalog-survey.json` から生成する。**",
        "更新するには `verify/survey_catalog.py` を実行してからビルドし直す。",
        "",
        f"- 生成日時: {survey.get('generated_at', '-')}",
        f"- 対象: {machine['query']}",
        f"- 件数: {len(datasets):,} 件 / 全 {survey['totals']['datasets']:,} 件",
        "",
        f"- 実ファイルに到達できるもの: {machine.get('reachable_datasets', 0):,} 件",
        "",
        "これは**存在の一覧であって、取得できることの保証ではない**。",
        "「実ファイル」の列は置き場のホストへ到達できるかを見ているだけで、",
        "個々のファイルが取れることまでは確かめていない。到達不可は提供停止ではなく、",
        "この環境の egress ポリシーで許可されていないことを意味する。",
        "実際に取れることを確かめたものだけが台帳（[REGISTRY.md](REGISTRY.md)）に載る。",
        "ライセンスはカタログが持っていないため、再配布の可否は個々の提供元に当たること。",
        "",
        "## 組織別",
        "",
    ]
    for org in sorted(by_org, key=lambda o: -len(by_org[o])):
        entries = by_org[org]
        reachable_count = sum(1 for d in entries if d.get("reachable"))
        lines += [
            f"### {org}（{len(entries):,} 件 / うち実ファイルに到達できるもの {reachable_count:,} 件）",
            "",
            "| データセット | 形式 | 更新頻度 | 実ファイル |",
            "|---|---|---|---|",
        ]
        for d in sorted(entries, key=lambda x: x.get("title") or ""):
            url = f"https://data.e-gov.go.jp/data/dataset/{d['name']}"
            formats = " / ".join(f for f in d["formats"] if f) or "-"
            reach = "到達可" if d.get("reachable") else "**到達不可**"
            lines.append(
                f"| [{d['title']}]({url}) | {formats} | {d.get('frequency_of_update') or '-'} | {reach} |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def load_survey() -> dict:
    if not SURVEY_PATH.is_file():
        return {}
    return json.loads(SURVEY_PATH.read_text(encoding="utf-8"))


def load_fields() -> dict:
    if not FIELDS_PATH.is_file():
        return {}
    return json.loads(FIELDS_PATH.read_text(encoding="utf-8"))


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
    fields = load_fields()
    entry_names = {e["id"]: e["name"] for e in entries}
    fields_markdown = render_fields(fields, entry_names) if fields else None
    survey = load_survey()
    survey_markdown = render_survey(survey) if survey else None
    machine_markdown = render_machine_readable(survey) if survey else None
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
        if fields_markdown and (
            not FIELDS_MD.is_file() or FIELDS_MD.read_text(encoding="utf-8") != fields_markdown
        ):
            stale.append(str(FIELDS_MD.relative_to(REPO_ROOT)))
        if survey_markdown and (
            not SURVEY_MD.is_file() or SURVEY_MD.read_text(encoding="utf-8") != survey_markdown
        ):
            stale.append(str(SURVEY_MD.relative_to(REPO_ROOT)))
        if machine_markdown and (
            not MACHINE_MD.is_file() or MACHINE_MD.read_text(encoding="utf-8") != machine_markdown
        ):
            stale.append(str(MACHINE_MD.relative_to(REPO_ROOT)))
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
    if fields_markdown:
        FIELDS_MD.write_text(fields_markdown, encoding="utf-8")
    if survey_markdown:
        SURVEY_MD.write_text(survey_markdown, encoding="utf-8")
    if machine_markdown:
        MACHINE_MD.write_text(machine_markdown, encoding="utf-8")

    for s in registry["sources"]:
        v = s["verification"]
        print(f"  {s['id']}: {v['status']}" + (f" ({v['reason']})" if v.get("reason") else ""))
    outputs = (
        [REGISTRY_JSON, REGISTRY_MD]
        + ([FIELDS_MD] if fields_markdown else [])
        + ([SURVEY_MD] if survey_markdown else [])
        + ([MACHINE_MD] if machine_markdown else [])
    )
    print(f"{len(entries)} 件 -> " + ", ".join(str(p.relative_to(REPO_ROOT)) for p in outputs))
    return 0


def _strip_generated_at(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.startswith("- 生成日時:"))


if __name__ == "__main__":
    sys.exit(main())
