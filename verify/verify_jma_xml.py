#!/usr/bin/env python3
"""気象庁防災情報XML（PULL型 Atom フィード）への接続・利用検証スクリプト。

https://xml.kishou.go.jp/xmlpull.html に掲載された 8 本の Atom フィードを取得し、
そのうち 1 件の電文本体まで辿って結果を results/ に書き出す。認証は不要。

気象庁は「1 日 10GB 以上のダウンロードを伴うアクセス」でアクセス元 IP を遮断すると
明記している。この検証は 9 リクエスト・数 MB に収まる範囲に意図的に留めてあり、
全フィードの電文を舐めるような使い方に広げてはいけない。

    python verify/verify_jma_xml.py --out results/jma-xml.json
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

SOURCE_ID = "jma-xml"
FEED_BASE = "https://www.data.jma.go.jp/developer/xml/feed"
ATOM = "{http://www.w3.org/2005/Atom}"

# xmlpull.html に掲載されている 8 本。高頻度は毎分更新、_l 付きの長期は毎時更新。
FEEDS = {
    "regular": "定時・高頻度",
    "extra": "随時・高頻度",
    "eqvol": "地震火山・高頻度",
    "other": "その他・高頻度",
    "regular_l": "定時・長期",
    "extra_l": "随時・長期",
    "eqvol_l": "地震火山・長期",
    "other_l": "その他・長期",
}


async def verify(feed_base: str) -> Reporter:
    reporter = Reporter(SOURCE_ID, feed_base)

    async with httpx.AsyncClient(timeout=60.0, trust_env=True) as client:
        entry_link = None
        for name, label in FEEDS.items():
            feed = await reporter.step(
                f"GET /{name}.xml ({label})", _get_feed(client, f"{feed_base}/{name}.xml")
            )
            # 最初に見つかった電文リンクだけを使う。全フィードから辿ると転送量が増える。
            if entry_link is None and feed:
                entry_link = feed.get("first_entry_link")

        if entry_link:
            await reporter.step("GET 電文本体", _get_document(client, entry_link))
        else:
            reporter.skip("GET 電文本体", "どのフィードにも entry が無かった（入電が無い時間帯）")

    reporter.extra["feeds"] = list(FEEDS)
    return reporter


async def _get_feed(client: httpx.AsyncClient, url: str) -> dict:
    """Atom フィードを取得し、件数と先頭 entry の骨格だけを残す。"""
    response = await client.get(url)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    entries = root.findall(f"{ATOM}entry")

    digest = {
        "status": response.status_code,
        "content_type": response.headers.get("content-type"),
        "bytes": len(response.content),
        "feed_title": _text(root.find(f"{ATOM}title")),
        "feed_updated": _text(root.find(f"{ATOM}updated")),
        "entry_count": len(entries),
    }
    if entries:
        first = entries[0]
        link = first.find(f"{ATOM}link")
        digest["first_entry"] = {
            "title": _text(first.find(f"{ATOM}title")),
            "updated": _text(first.find(f"{ATOM}updated")),
            "id": _text(first.find(f"{ATOM}id")),
        }
        digest["first_entry_link"] = link.get("href") if link is not None else None
    return digest


async def _get_document(client: httpx.AsyncClient, url: str) -> dict:
    """電文本体を取得し、XML として解釈できることまで確認する。"""
    response = await client.get(url)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    return {
        "url": url,
        "status": response.status_code,
        "content_type": response.headers.get("content-type"),
        "bytes": len(response.content),
        "root_tag": root.tag,
        "child_tags": [child.tag for child in root][:5],
    }


def _text(element) -> str | None:
    return element.text if element is not None else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feed-base", default=FEED_BASE, help="Atom フィードのベース URL")
    parser.add_argument("--out", default="results/jma-xml.json", help="結果 JSON の出力先")
    args = parser.parse_args()

    reporter = asyncio.run(verify(args.feed_base))
    reporter.write(args.out)
    return reporter.print_console(args.out)


if __name__ == "__main__":
    sys.exit(main())
