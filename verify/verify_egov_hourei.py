#!/usr/bin/env python3
"""e-Gov 法令 API Version 2 への接続・利用検証スクリプト。

OpenAPI 仕様（/api/2/swagger-ui/lawapi-v2.yaml）に定義された 6 エンドポイントを
実際に叩き、結果を results/ に書き出す。認証は不要なため事前準備は要らない。

使い方:
    python verify/verify_egov_hourei.py --out results/egov-hourei-api.json
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

SOURCE_ID = "egov-hourei-api"
BASE_URL = "https://laws.e-gov.go.jp/api/2"
SPEC_PATH = "/swagger-ui/lawapi-v2.yaml"
# 日本国憲法。改正が無く ID が変わらないため、検証の固定入力として使う。
SAMPLE_LAW_ID = "321CONSTITUTION"
# 憲法は添付ファイルを持たないため、/attachment 用に添付を持つ法令を別に固定する。
# （明治三十三年大蔵省令第五号。PDF 添付を 1 件持つ）
SAMPLE_ATTACHMENT_LAW_ID = "133M10000040005"


async def verify(base_url: str) -> Reporter:
    reporter = Reporter(SOURCE_ID, base_url)

    # trust_env=True でプロキシ設定と CA バンドルを環境から引き継ぐ。
    async with httpx.AsyncClient(base_url=base_url, timeout=60.0, trust_env=True) as client:
        spec = await reporter.step("fetch_openapi_spec", _fetch_spec(client))

        # 収録全件数。台帳の coverage に書く数値はこのステップの実測から取る。
        await reporter.step("GET /laws（全件数）", _get_json(client, "/laws", {"limit": 1}))

        laws = await reporter.step(
            "GET /laws", _get_json(client, "/laws", {"limit": 3, "law_type": "Constitution"})
        )

        law_id = _first_law_id(laws) or SAMPLE_LAW_ID
        await reporter.step(
            f"GET /law_revisions/{{law_id}}", _get_json(client, f"/law_revisions/{law_id}", {})
        )
        law_data = await reporter.step(
            f"GET /law_data/{{law_id}}",
            _get_json(client, f"/law_data/{law_id}", {"response_format": "json", "limit": 1}),
        )
        await reporter.step(
            "GET /keyword", _get_json(client, "/keyword", {"keyword": "個人情報", "limit": 3})
        )
        await reporter.step(
            f"GET /law_file/xml/{{law_id}}", _get_raw(client, f"/law_file/xml/{law_id}", {})
        )

        # 改正で law_revision_id は変わるため、ハードコードせず都度引き直す。
        revision_id = await _attachment_revision_id(client, SAMPLE_ATTACHMENT_LAW_ID)
        if revision_id:
            await reporter.step(
                "GET /attachment/{law_revision_id}",
                _get_raw(client, f"/attachment/{revision_id}", {}),
            )
        else:
            reporter.skip(
                "GET /attachment/{law_revision_id}",
                f"{SAMPLE_ATTACHMENT_LAW_ID} から添付ファイルの law_revision_id を取得できなかった",
            )

    reporter.extra["spec"] = spec
    reporter.extra["sample_law_id"] = law_id
    return reporter


async def _fetch_spec(client: httpx.AsyncClient) -> dict:
    """OpenAPI 仕様を取得し、版数・エンドポイント・認証定義の有無を記録する。"""
    response = await client.get(SPEC_PATH)
    response.raise_for_status()
    text = response.text
    paths = sorted(
        line.strip().rstrip(":")
        for line in text.splitlines()
        if line.startswith("  /") and line.rstrip().endswith(":")
    )
    version = next(
        (line.split(":", 1)[1].strip() for line in text.splitlines() if line.startswith("  version:")),
        None,
    )
    return {
        "url": str(response.request.url),
        "spec_version": version,
        "paths": paths,
        # security セクションが無いことは「認証不要」を示す一次情報として重要。
        "declares_security_scheme": "securitySchemes" in text,
        "bytes": len(response.content),
    }


async def _get_json(client: httpx.AsyncClient, path: str, params: dict) -> Any:
    response = await client.get(path, params=params)
    response.raise_for_status()
    payload = response.json()
    return _digest(path, payload)


async def _get_raw(client: httpx.AsyncClient, path: str, params: dict) -> dict:
    """ファイル返却系エンドポイントは中身ではなく形だけを記録する。"""
    response = await client.get(path, params=params)
    response.raise_for_status()
    return {
        "status": response.status_code,
        "content_type": response.headers.get("content-type"),
        "bytes": len(response.content),
    }


def _digest(path: str, payload: Any) -> Any:
    """レスポンス全体は巨大になるため、件数と先頭要素の骨格だけを残す。"""
    if not isinstance(payload, dict):
        return payload
    digest: dict[str, Any] = {"top_level_keys": sorted(payload.keys())}
    for key in ("total_count", "count", "next_offset"):
        if key in payload:
            digest[key] = payload[key]
    for key in ("laws", "revisions", "items"):
        items = payload.get(key)
        if isinstance(items, list):
            digest[f"{key}_len"] = len(items)
            if items:
                digest[f"{key}_first"] = items[0]
            break
    if "law_info" in payload:
        digest["law_info"] = payload["law_info"]
    if "attached_files_info" in payload:
        attached = payload["attached_files_info"] or {}
        digest["attached_files_len"] = len(attached.get("attached_files") or [])
    if "law_full_text" in payload:
        text = payload["law_full_text"]
        digest["law_full_text_type"] = type(text).__name__
    return digest


def _first_law_id(laws_result: Any) -> str | None:
    if not isinstance(laws_result, dict):
        return None
    first = laws_result.get("laws_first")
    if isinstance(first, dict):
        info = first.get("law_info")
        if isinstance(info, dict) and info.get("law_id"):
            return str(info["law_id"])
    return None


async def _attachment_revision_id(client: httpx.AsyncClient, law_id: str) -> str | None:
    """添付ファイルを持つ法令から、/attachment に渡す law_revision_id を取得する。"""
    response = await client.get(f"/law_data/{law_id}", params={"response_format": "json"})
    response.raise_for_status()
    info = response.json().get("attached_files_info") or {}
    for entry in info.get("attached_files") or []:
        if entry.get("law_revision_id"):
            return str(entry["law_revision_id"])
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=BASE_URL, help="法令 API のベース URL")
    parser.add_argument("--out", default="results/egov-hourei-api.json", help="結果 JSON の出力先")
    args = parser.parse_args()

    reporter = asyncio.run(verify(args.base_url))
    reporter.write(args.out)
    return reporter.print_console(args.out)


if __name__ == "__main__":
    sys.exit(main())
