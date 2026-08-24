#!/usr/bin/env python3
"""統計 LOD（e-Stat）SPARQL エンドポイントの接続・利用検証。

SPARQL 1.1 準拠とされる 4 種のクエリ（SELECT / ASK / CONSTRUCT / DESCRIBE）と、
Accept ヘッダによる出力形式の切り替えを実際に確かめる。認証情報は不要。

同じ e-Stat でも、appId が要る e-Stat API（候補 estat-api）とは別系統である。

    python verify/verify_estat_lod.py --out results/estat-lod.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _report import Reporter  # noqa: E402

SOURCE_ID = "estat-lod"
ENDPOINT = "https://data.e-stat.go.jp/lod/sparql/alldata/query"

MEASURE = "<http://data.e-stat.go.jp/lod/ontology/measure/index>"
TIME = "<http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/timePeriod>"
GYEARMONTH = '"2015-06"^^<http://www.w3.org/2001/XMLSchema#gYearMonth>'

# 一次資料のサンプルと同じ「2015 年 6 月の消費者物価指数」を使う。
SELECT_QUERY = f"select ?cpi where {{ ?s {MEASURE} ?cpi ; {TIME} {GYEARMONTH} . }} limit 3"
ASK_QUERY = f"ask {{ ?s {MEASURE} ?cpi ; {TIME} {GYEARMONTH} . }}"
CONSTRUCT_QUERY = f"construct {{ ?s {MEASURE} ?cpi }} where {{ ?s {MEASURE} ?cpi ; {TIME} {GYEARMONTH} . }} limit 3"
DESCRIBE_QUERY = f"describe ?s where {{ ?s {MEASURE} ?cpi ; {TIME} {GYEARMONTH} . }} limit 1"

# 一次資料が CONSTRUCT / DESCRIBE 用に挙げている形式（* は既定と書かれているもの）。
RDF_ACCEPTS = ["application/rdf+xml", "text/turtle", "application/n-triples", "text/plain", None]
# 形式によって応答の重さが大きく違う。待ち続けず、返らないことを結果として記録する。
NEGOTIATION_TIMEOUT = 60.0


async def verify(endpoint: str) -> Reporter:
    reporter = Reporter(SOURCE_ID, endpoint)

    async with httpx.AsyncClient(timeout=120.0, trust_env=True, follow_redirects=True) as client:
        await reporter.step(
            "SELECT (JSON)", _query(client, endpoint, SELECT_QUERY, "application/sparql-results+json")
        )
        await reporter.step(
            "SELECT (CSV)", _query(client, endpoint, SELECT_QUERY, "text/csv")
        )
        await reporter.step(
            "SELECT (XML)", _query(client, endpoint, SELECT_QUERY, "application/sparql-results+xml")
        )
        await reporter.step(
            "ASK", _query(client, endpoint, ASK_QUERY, "application/sparql-results+json")
        )
        # CONSTRUCT / DESCRIBE は一次資料が挙げる形式の一部が通らない。どれが通り
        # どれが拒否されるかを測ること自体を検証にする。406 は結果であって失敗ではない。
        await reporter.step(
            "CONSTRUCT: 出力形式のネゴシエーション", _negotiate(client, endpoint, CONSTRUCT_QUERY)
        )
        await reporter.step(
            "DESCRIBE: 出力形式のネゴシエーション", _negotiate(client, endpoint, DESCRIBE_QUERY)
        )
        await reporter.step("POST での照会", _query(client, endpoint, SELECT_QUERY, "application/sparql-results+json", method="POST"))

    return reporter


async def _query(
    client: httpx.AsyncClient, endpoint: str, query: str, accept: str, method: str = "GET"
) -> dict:
    """1 クエリ投げて、返った形式と中身の骨格を残す。

    出力形式は Accept ヘッダで決まると一次資料にあるため、要求した形式と
    実際に返った Content-Type の両方を記録する。食い違えば利用側が壊れる。
    """
    headers = {"Accept": accept}
    if method == "POST":
        response = await client.post(endpoint, params={"query": query}, headers=headers)
    else:
        response = await client.get(endpoint, params={"query": query}, headers=headers)
    response.raise_for_status()
    digest = {
        "method": method,
        "accept_requested": accept,
        "content_type": response.headers.get("content-type"),
        "status": response.status_code,
        "bytes": len(response.content),
    }
    body = response.text
    if "json" in (response.headers.get("content-type") or ""):
        payload = json.loads(body)
        if "boolean" in payload:
            digest["boolean"] = payload["boolean"]
        else:
            results = (payload.get("results") or {}).get("bindings") or []
            digest["vars"] = (payload.get("head") or {}).get("vars")
            digest["rows"] = len(results)
            digest["first_row"] = results[0] if results else None
    else:
        digest["head"] = body[:200]
    return digest


async def _negotiate(client: httpx.AsyncClient, endpoint: str, query: str) -> dict:
    """一次資料が挙げる各形式を Accept に指定し、通るものと拒否されるものを分ける。"""
    results = {}
    for accept in RDF_ACCEPTS:
        key = accept or "(Accept なし)"
        try:
            response = await client.get(
                endpoint,
                params={"query": query},
                headers={"Accept": accept} if accept else {},
                timeout=NEGOTIATION_TIMEOUT,
            )
        except httpx.TimeoutException:
            # 応答しないことも結果。形式によって重さが違うのは利用側が知るべき事実。
            results[key] = {"status": None, "error": f"{NEGOTIATION_TIMEOUT} 秒でタイムアウト"}
            continue
        results[key] = {
            "status": response.status_code,
            "content_type": response.headers.get("content-type"),
            "bytes": len(response.content),
        }
    return {
        "documented_formats": RDF_ACCEPTS,
        "by_accept": results,
        "accepted": [a or "(Accept なし)" for a, r in results.items() if r["status"] == 200],
        "rejected": [a or "(Accept なし)" for a, r in results.items() if r["status"] != 200],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", default=ENDPOINT, help="SPARQL エンドポイント")
    parser.add_argument("--out", default="results/estat-lod.json", help="結果 JSON の出力先")
    args = parser.parse_args()

    reporter = asyncio.run(verify(args.endpoint))
    reporter.write(args.out)
    return reporter.print_console(args.out)


if __name__ == "__main__":
    sys.exit(main())
