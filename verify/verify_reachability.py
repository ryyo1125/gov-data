#!/usr/bin/env python3
"""台帳と保留リストに載る全ホストの到達性を実測する。

到達性は実行環境ごとに変わり、しかも黙って変わる。egress の許可リストが
広がれば保留中の候補が検証可能になり、狭まれば検証済みのエントリが動かなくなる。
どちらも気づけないと台帳が嘘になるので、ホストの状態そのものを検証対象にする。

    python verify/verify_reachability.py --out results/reachability.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

import httpx
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _report import Reporter  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ID = "reachability"


def collect_hosts() -> list[dict]:
    """台帳エントリと保留リストから、実測すべきホストを重複なく集める。"""
    hosts: dict[str, dict] = {}

    for path in sorted((REPO_ROOT / "registry" / "sources").glob("*.yaml")):
        entry = yaml.safe_load(path.read_text(encoding="utf-8"))
        for host in entry.get("reachability", {}).get("hosts", []):
            hosts.setdefault(host["host"], {"host": host["host"], "used_by": [], "role": host.get("role", "")})
            hosts[host["host"]]["used_by"].append(entry["id"])

    candidates_path = REPO_ROOT / "registry" / "candidates.yaml"
    if candidates_path.is_file():
        candidates = yaml.safe_load(candidates_path.read_text(encoding="utf-8")) or {}
        for candidate in candidates.get("candidates", []):
            for host in candidate.get("hosts", []):
                hosts.setdefault(host, {"host": host, "used_by": [], "role": "candidate"})
                hosts[host]["used_by"].append(f"candidate:{candidate['id']}")

    # 俯瞰が見つけた実ファイルの置き場も含める。台帳と待避所だけを見ていると、
    # そのとき到達できていたホストは記録されず、後から塞がれても気づけない。
    # 実際に www.e-stat.go.jp（機械可読データ 503 件分）がこの穴から漏れた。
    survey_path = REPO_ROOT / "results" / "catalog-survey.json"
    if survey_path.is_file():
        survey = json.loads(survey_path.read_text(encoding="utf-8"))
        for host in (survey.get("machine_readable", {}).get("resource_hosts") or {}):
            hosts.setdefault(host, {"host": host, "used_by": [], "role": "catalog-resource"})
            hosts[host]["used_by"].append("survey:catalog")

    return [hosts[k] for k in sorted(hosts)]


async def probe(host: str) -> dict:
    """1 ホストに GET し、到達可・egress 拒否・その他不達を区別して返す。

    プロキシ拒否は httpx.ProxyError、先方の 403 は status_code 403 として現れる。
    この 2 つを混同すると「先方が塞いだ」と誤診するため、必ず分けて記録する。
    """
    async with httpx.AsyncClient(timeout=30.0, trust_env=True, follow_redirects=False) as client:
        try:
            response = await client.get(f"https://{host}/")
        except httpx.ProxyError as exc:
            raise BlockedByEgress(f"プロキシが拒否: {exc}") from exc
        return {"status_code": response.status_code, "final_url": str(response.url)}


class BlockedByEgress(Exception):
    """自環境の egress ポリシーによる拒否。先方の問題ではない。"""


async def verify() -> Reporter:
    reporter = Reporter(SOURCE_ID, "egress reachability")
    entries = collect_hosts()

    for entry in entries:
        host = entry["host"]
        label = f"{host} ({', '.join(entry['used_by'])})"
        try:
            result = await probe(host)
        except BlockedByEgress as exc:
            reporter.blocked(label, str(exc))
            continue
        except Exception as exc:  # noqa: BLE001 - 不達の理由をそのまま残す
            reporter.steps.append(
                {"step": label, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
            )
            continue
        reporter.steps.append({"step": label, "ok": True, "result": result})

    reporter.extra["hosts"] = entries
    return reporter


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="results/reachability.json", help="結果 JSON の出力先")
    args = parser.parse_args()

    reporter = asyncio.run(verify())
    reporter.write(args.out)
    # ここでは blocked も想定内の結果なので、失敗として終了コードを立てない。
    reporter.print_console(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
