#!/usr/bin/env python3
"""e-Gov データポータル（CKAN API）への接続・利用検証スクリプト。

日本政府のオープンデータカタログ。台帳に載せる候補を機械的に洗い出す用途で使うため、
検索・一覧・組織・タグ・個別データセットの取得までを一通り確認する。

    python verify/verify_egov_data_catalog.py --out results/egov-data-catalog.json
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _report import Reporter  # noqa: E402

SOURCE_ID = "egov-data-catalog"
# www.data.go.jp/api/3/action/* は 404。実体はこのパスにある。
BASE_URL = "https://data.e-gov.go.jp/data/api/3/action"


async def verify(base_url: str) -> Reporter:
    reporter = Reporter(SOURCE_ID, base_url)

    async with httpx.AsyncClient(base_url=base_url, timeout=60.0, trust_env=True) as client:
        await reporter.step("site_read", _call(client, "site_read", {}))
        search = await reporter.step("package_search", _call(client, "package_search", {"rows": 3}))
        await reporter.step("package_list", _call(client, "package_list", {"limit": 5}))
        await reporter.step("organization_list", _call(client, "organization_list", {"limit": 5}))
        await reporter.step("group_list", _call(client, "group_list", {"limit": 5}))
        await reporter.step("tag_list", _call(client, "tag_list", {}))

        package_id = _first_package_id(search)
        if package_id:
            await reporter.step("package_show", _call(client, "package_show", {"id": package_id}))
        else:
            reporter.skip("package_show", "package_search の戻り値からデータセット ID を取得できなかった")

    return reporter


async def _call(client: httpx.AsyncClient, action: str, params: dict) -> Any:
    response = await client.get(f"/{action}", params=params)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise RuntimeError(f"{action} が success=false を返した: {payload.get('error')}")
    return _digest(action, payload.get("result"))


def _digest(action: str, result: Any) -> Any:
    """カタログ全体は巨大なので、件数と代表要素の骨格だけを残す。"""
    if isinstance(result, bool):
        return {"result": result}
    if isinstance(result, list):
        return {"len": len(result), "sample": result[:3]}
    if not isinstance(result, dict):
        return result

    digest: dict[str, Any] = {"count": result.get("count")}
    packages = result.get("results")
    if isinstance(packages, list):
        digest["results_len"] = len(packages)
        digest["results_sample"] = [_package_digest(p) for p in packages[:3]]
    elif result.get("id"):
        digest = _package_digest(result)
    return digest


def _package_digest(package: dict) -> dict:
    """データセット 1 件から、台帳の候補判断に使う項目だけを抜く。"""
    return {
        "id": package.get("id"),
        "title": package.get("title"),
        "organization": (package.get("organization") or {}).get("title"),
        "license_id": package.get("license_id"),
        "license_title": package.get("license_title"),
        "frequency_of_update": package.get("frequency_of_update"),
        "num_resources": package.get("num_resources"),
        "resource_formats": sorted(
            {r.get("format") for r in (package.get("resources") or []) if r.get("format")}
        ),
    }


def _first_package_id(search_result: Any) -> str | None:
    if not isinstance(search_result, dict):
        return None
    for sample in search_result.get("results_sample") or []:
        if sample.get("id"):
            return str(sample["id"])
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=BASE_URL, help="CKAN API のベース URL")
    parser.add_argument("--out", default="results/egov-data-catalog.json", help="結果 JSON の出力先")
    args = parser.parse_args()

    reporter = asyncio.run(verify(args.base_url))
    reporter.write(args.out)
    return reporter.print_console(args.out)


if __name__ == "__main__":
    sys.exit(main())
