#!/usr/bin/env python3
"""e-Gov データポータルのカタログから、日本政府に「何があるか」の俯瞰を作る。

台帳（registry/）は検証済みの情報源だけを載せる。一方この俯瞰は、まだ検証して
いないものも含めて全体像を掴むためのもの。役割が違うので混ぜない。

手書きの一覧を作らないこと。カタログは動くので、書いた瞬間から古くなる。
ここで作るのは毎回引き直せる生成物であり、docs/SURVEY.md はこの結果から作られる。

    python verify/survey_catalog.py --out results/catalog-survey.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone

import httpx

BASE_URL = "https://data.e-gov.go.jp/data/api/3/action"

# 機械で読める形式。台帳に昇格させる候補はここから探す。
MACHINE_READABLE = ["CSV", "XML", "JSON", "RDF", "GeoJSON", "TSV", "JSON-LD", "API"]
# 表計算は機械で読めなくはないが、体裁が自由すぎて安定して解釈できない。別枠にする。
SEMI_STRUCTURED = ["XLSX", "XLS"]

FACET_LIMIT = 100
SAMPLES_PER_ORG = 3
# 全件取得のページサイズ。機械可読データは全体の 1 割に満たないので全部引ける。
PAGE_SIZE = 100


async def survey(base_url: str) -> dict:
    async with httpx.AsyncClient(base_url=base_url, timeout=120.0, trust_env=True) as client:
        total = await _count(client, None)
        formats = await _facet(client, "res_format", None)
        organizations = await _facet(client, "organization", None)
        frequencies = await _facet(client, "frequency_of_update", None)

        machine_query = _or_query(MACHINE_READABLE)
        machine_total = await _count(client, machine_query)
        machine_by_org = await _facet(client, "organization", machine_query)

        # 形式ごとの内訳。どの形式がどれだけ出回っているかは候補選びに直結する。
        machine_by_format = {}
        for fmt in MACHINE_READABLE:
            machine_by_format[fmt] = await _count(client, f"res_format:{fmt}")

        machine_tags = await _facet(client, "tags", machine_query)

        samples = []
        for org in sorted(machine_by_org, key=lambda o: -o["count"])[:5]:
            samples.append(
                {
                    "organization": org["label"],
                    "datasets": await _samples(client, machine_query, org["name"]),
                }
            )

        # 母集団が小さいので全件引ける。候補選びは一覧を見ないと始まらない。
        machine_datasets = await _all_datasets(client, machine_query)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generated_by": "verify/survey_catalog.py",
        "source": {
            "name": "e-Gov データポータル（CKAN API）",
            "endpoint": base_url,
            "registry_entry": "egov-data-catalog",
        },
        "totals": {
            "datasets": total,
            "organizations": len(organizations),
            "machine_readable_datasets": machine_total,
        },
        "by_organization": sorted(organizations, key=lambda o: -o["count"]),
        "by_format": sorted(formats, key=lambda f: -f["count"]),
        "by_update_frequency": sorted(frequencies, key=lambda f: -f["count"]),
        "machine_readable": {
            "query": machine_query,
            "by_format": machine_by_format,
            "by_organization": sorted(machine_by_org, key=lambda o: -o["count"]),
            "by_tag": sorted(machine_tags, key=lambda t: -t["count"]),
            "samples": samples,
            "datasets": machine_datasets,
        },
        "definitions": {
            "machine_readable": MACHINE_READABLE,
            "semi_structured": SEMI_STRUCTURED,
        },
    }


def _or_query(formats: list[str]) -> str:
    return "res_format:(" + " OR ".join(formats) + ")"


async def _count(client: httpx.AsyncClient, query: str | None) -> int:
    params = {"rows": 0}
    if query:
        params["fq"] = query
    response = await client.get("/package_search", params=params)
    response.raise_for_status()
    return response.json()["result"]["count"]


async def _facet(client: httpx.AsyncClient, field: str, query: str | None) -> list[dict]:
    """ファセットが数えるのは「その値を持つデータセット数」であってリソース数ではない。

    1 つのデータセットが PDF と CSV を両方持てば両方に数えられるため、
    形式ごとの合計はデータセット総数を超える。この点を取り違えると
    「全リソースの何割が CSV か」という誤った読み方をしてしまう。
    """
    params = {"rows": 0, "facet.field": json.dumps([field]), "facet.limit": FACET_LIMIT}
    if query:
        params["fq"] = query
    response = await client.get("/package_search", params=params)
    response.raise_for_status()
    items = (response.json()["result"].get("search_facets") or {}).get(field, {}).get("items", [])
    return [
        {"name": i["name"], "label": i.get("display_name") or i["name"], "count": i["count"]}
        for i in items
    ]


async def _samples(client: httpx.AsyncClient, query: str, organization: str) -> list[dict]:
    """候補を選ぶときに中身が想像できるよう、代表例をいくつか残す。"""
    response = await client.get(
        "/package_search",
        params={"rows": SAMPLES_PER_ORG, "fq": f"{query} AND organization:{organization}"},
    )
    response.raise_for_status()
    return [
        {
            "title": p.get("title"),
            "name": p.get("name"),
            "url": f"https://data.e-gov.go.jp/data/dataset/{p.get('name')}",
            "formats": sorted({r.get("format") for r in (p.get("resources") or []) if r.get("format")}),
            "frequency_of_update": p.get("frequency_of_update"),
        }
        for p in response.json()["result"]["results"]
    ]


async def _all_datasets(client: httpx.AsyncClient, query: str) -> list[dict]:
    """条件に合うデータセットを全件返す。件数が多い条件には使わないこと。"""
    datasets, start = [], 0
    while True:
        response = await client.get(
            "/package_search", params={"rows": PAGE_SIZE, "start": start, "fq": query}
        )
        response.raise_for_status()
        result = response.json()["result"]
        page = result["results"]
        if not page:
            break
        for p in page:
            datasets.append(
                {
                    "title": p.get("title"),
                    "name": p.get("name"),
                    "organization": (p.get("organization") or {}).get("title"),
                    "formats": sorted(
                        {r.get("format") for r in (p.get("resources") or []) if r.get("format")}
                    ),
                    "frequency_of_update": p.get("frequency_of_update"),
                    "tags": sorted(t.get("display_name") or t.get("name") for t in (p.get("tags") or [])),
                }
            )
        start += PAGE_SIZE
        if start >= result["count"]:
            break
    return datasets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=BASE_URL, help="CKAN API のベース URL")
    parser.add_argument("--out", default="results/catalog-survey.json", help="結果 JSON の出力先")
    args = parser.parse_args()

    result = asyncio.run(survey(args.base_url))
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)

    totals = result["totals"]
    machine = totals["machine_readable_datasets"]
    print(f"  データセット {totals['datasets']:,} 件 / {totals['organizations']} 組織")
    print(f"  機械可読を含むもの {machine:,} 件（{machine / totals['datasets'] * 100:.1f}%）")
    print(f"  うち一覧を取得できたもの {len(result['machine_readable']['datasets']):,} 件")
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
