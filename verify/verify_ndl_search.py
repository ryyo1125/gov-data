#!/usr/bin/env python3
"""国立国会図書館サーチ（NDLサーチ）外部提供インタフェースの接続・利用検証。

検索用 3 経路（SRU / OpenSearch / OpenURL）とハーベスト用 1 経路（OAI-PMH）を
すべて叩く。認証情報は不要。

同時リクエスト数に制限があり、大量アクセスは遮断される旨が一次資料に明記されている。
この検証は逐次・少数のリクエストに留めてあり、件数を稼ぐ用途に広げてはいけない。

    python verify/verify_ndl_search.py --out results/ndl-search.json
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _report import Reporter  # noqa: E402

SOURCE_ID = "ndl-search"
BASE_URL = "https://ndlsearch.ndl.go.jp/api"
SRU = "{http://www.loc.gov/zing/srw/}"
DIAG = "{http://www.loc.gov/zing/srw/diagnostic/}"
# 一次資料が同時リクエスト数の制限と大量アクセスの遮断を明記している。実際に
# 連続実行で 429 を返された。件数を稼ぐ用途ではないので、間隔を空けて逐次に叩く。
REQUEST_INTERVAL = 5.0
# 429 は先方が明記している制限に当たっただけで、障害ではない。1 回だけ長めに
# 待って引き直す。それでも駄目なら制限として記録する（叩き続けない）。
RETRY_AFTER_429 = 30.0
OAI = "{http://www.openarchives.org/OAI/2.0/}"


async def verify(base_url: str) -> Reporter:
    reporter = Reporter(SOURCE_ID, base_url)

    async with httpx.AsyncClient(base_url=base_url, timeout=90.0, trust_env=True) as client:
        steps = [
            ("SRU: explain", _sru_explain(client)),
            ("SRU: searchRetrieve", _sru_search(client)),
            ("OpenSearch: 検索", _opensearch(client)),
            ("OpenURL: 検索", _openurl(client)),
            ("OAI-PMH: Identify", _oai(client, {"verb": "Identify"})),
            ("OAI-PMH: ListMetadataFormats", _oai(client, {"verb": "ListMetadataFormats"})),
            ("OAI-PMH: ListSets", _oai(client, {"verb": "ListSets"})),
        ]
        for index, (name, coro) in enumerate(steps):
            if index:
                await asyncio.sleep(REQUEST_INTERVAL)
            await reporter.step(name, coro)

    return reporter


async def _get(client: httpx.AsyncClient, path: str, **kwargs) -> httpx.Response:
    """429 を 1 回だけ待って引き直す。制限は先方の仕様であって障害ではない。"""
    response = await client.get(path, **kwargs)
    if response.status_code == 429:
        await asyncio.sleep(RETRY_AFTER_429)
        response = await client.get(path, **kwargs)
    response.raise_for_status()
    return response


async def _sru_explain(client: httpx.AsyncClient) -> dict:
    """SRU の explain。サーバーが自分の対応機能を宣言する経路。"""
    response = await _get(client, "/sru", params={"operation": "explain"})
    root = ET.fromstring(response.text)
    digest = {
        "status": response.status_code,
        "content_type": response.headers.get("content-type"),
        "root_tag": _local(root.tag),
        "child_tags": [_local(c.tag) for c in root][:6],
    }
    # explain が診断を返すなら、その経路は使えない。何が返ったかを残す。
    diagnostics = root.findall(f".//{DIAG}diagnostic")
    if diagnostics:
        digest["diagnostics"] = [
            {_local(c.tag): c.text for c in d} for d in diagnostics[:3]
        ]
    return digest


async def _sru_search(client: httpx.AsyncClient) -> dict:
    """CQL による検索。一次資料のリクエスト例と同じ形にしてある。"""
    response = await _get(
        client,
        "/sru",
        params={
            "operation": "searchRetrieve",
            "maximumRecords": 1,
            "query": 'title="桜" AND from="2018"',
        },
    )
    root = ET.fromstring(response.text)
    record = root.find(f".//{SRU}recordData")
    return {
        "status": response.status_code,
        "numberOfRecords": _text(root.find(f"{SRU}numberOfRecords")),
        "recordSchema": _text(root.find(f".//{SRU}recordSchema")),
        # 返るのは DC-NDL（RDF）。要素名まで見ておくと利用側の想定が立つ。
        "record_child_tags": [_local(c.tag) for c in list(record)[:1][0]][:8] if record is not None and len(record) else [],
    }


async def _opensearch(client: httpx.AsyncClient) -> dict:
    """OpenSearch。RSS で返るため、チャンネルと item の骨格を見る。"""
    response = await _get(client, "/opensearch", params={"cnt": 1, "title": "桜"})
    root = ET.fromstring(response.text)
    channel = root.find("channel")
    item = channel.find("item") if channel is not None else None
    return {
        "status": response.status_code,
        "content_type": response.headers.get("content-type"),
        "root_tag": _local(root.tag),
        "channel_children": [_local(c.tag) for c in channel][:8] if channel is not None else [],
        "item_children": [_local(c.tag) for c in item][:10] if item is not None else [],
    }


async def _openurl(client: httpx.AsyncClient) -> dict:
    """OpenURL は HTML を返す。機械可読ではないので形だけ確かめる。

    仕様に載る /api/openurl は画面側の /openurl へ 301 する。追従先まで
    記録しておかないと、利用側が「API が消えた」と誤読する。
    """
    response = await _get(client, "/openurl", params={"au": "夏目漱石"}, follow_redirects=True)
    return {
        "requested": "/api/openurl",
        "final_url": str(response.url),
        "redirects": [str(r.url) for r in response.history],
        "status": response.status_code,
        "content_type": response.headers.get("content-type"),
        "bytes": len(response.content),
    }


async def _oai(client: httpx.AsyncClient, params: dict) -> dict:
    """OAI-PMH。verb ごとに返る要素が違うので、骨格と件数を残す。"""
    response = await _get(client, "/oaipmh", params=params)
    root = ET.fromstring(response.text)
    body = [c for c in root if _local(c.tag) not in ("responseDate", "request")]
    digest = {
        "status": response.status_code,
        "content_type": response.headers.get("content-type"),
        "verb": params["verb"],
        "body_tag": _local(body[0].tag) if body else None,
    }
    if body:
        children = list(body[0])
        digest["entries"] = len(children)
        digest["first_entry_tags"] = [_local(c.tag) for c in children[0]][:8] if children else []
        if params["verb"] == "Identify":
            digest["identify"] = {_local(c.tag): (c.text or "")[:60] for c in children[:8]}
    return digest


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _text(element) -> str | None:
    return element.text if element is not None else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=BASE_URL, help="NDLサーチ API のベース URL")
    parser.add_argument("--out", default="results/ndl-search.json", help="結果 JSON の出力先")
    args = parser.parse_args()

    reporter = asyncio.run(verify(args.base_url))
    reporter.write(args.out)
    return reporter.print_console(args.out)


if __name__ == "__main__":
    sys.exit(main())
