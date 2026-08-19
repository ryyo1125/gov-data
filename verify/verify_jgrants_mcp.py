#!/usr/bin/env python3
"""デジタル庁「Jグランツ MCP Server」への接続・利用検証スクリプト。

Streamable-HTTP で起動済みの MCP サーバーに接続し、
initialize / tools・resources・prompts の列挙 / 各ツールの実行を順に試して
結果を results/ に書き出す。

使い方:
    python -m jgrants_mcp_server.core --host 127.0.0.1 --port 8000   # 別プロセスで起動
    python verify/verify_jgrants_mcp.py --url http://127.0.0.1:8000/mcp \
        --out results/jgrants-mcp.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from fastmcp import Client

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _report import Reporter  # noqa: E402

SOURCE_ID = "jgrants-mcp"
# 検索結果の先頭が添付ファイルを持たないことが多いため、何件まで詳細を引き直すか。
FILE_PROBE_LIMIT = 5


async def verify(url: str, keyword: str) -> Reporter:
    reporter = Reporter(SOURCE_ID, url)
    client = Client(url)

    async with client:
        await reporter.step("initialize", _initialize(client))

        tools = await reporter.step("list_tools", _list_tools(client))
        await reporter.step("list_resources", _list_resources(client))
        await reporter.step("list_prompts", _list_prompts(client))

        await reporter.step("call:ping", _call(client, "ping", {}))

        search = await reporter.step(
            "call:search_subsidies", _call(client, "search_subsidies", {"keyword": keyword})
        )

        subsidy_id = _first_subsidy_id(search)
        detail = None
        if subsidy_id:
            detail = await reporter.step(
                "call:get_subsidy_detail",
                _call(client, "get_subsidy_detail", {"subsidy_id": subsidy_id}),
            )
        else:
            reporter.skip(
                "call:get_subsidy_detail",
                "search_subsidies の戻り値から補助金 ID を取得できなかった",
            )

        await reporter.step(
            "call:get_subsidy_overview",
            _call(client, "get_subsidy_overview", {"output_format": "json"}),
        )

        target = await _find_downloaded_file(client, search, detail, subsidy_id)
        if target:
            file_owner, filename = target
            await reporter.step(
                "call:get_file_content",
                _call(
                    client,
                    "get_file_content",
                    {"subsidy_id": file_owner, "filename": filename, "return_format": "markdown"},
                ),
            )
        else:
            reporter.skip(
                "call:get_file_content",
                f"検索結果の先頭 {FILE_PROBE_LIMIT} 件に添付ファイルが無かった",
            )

    reporter.extra["keyword"] = keyword
    reporter.extra["tools"] = sorted(t.name for t in (tools or []))
    return reporter


async def _initialize(client: Client) -> dict:
    result = client.initialize_result
    server = result.serverInfo
    return {
        "server_name": server.name,
        "server_version": server.version,
        "protocol_version": result.protocolVersion,
        "capabilities": json.loads(result.capabilities.model_dump_json()),
    }


async def _list_tools(client: Client) -> list:
    return await client.list_tools()


async def _list_resources(client: Client) -> list[str]:
    return [str(r.uri) for r in await client.list_resources()]


async def _list_prompts(client: Client) -> list[str]:
    return [p.name for p in await client.list_prompts()]


async def _call(client: Client, tool: str, args: dict) -> Any:
    return _unwrap(await client.call_tool(tool, args))


def _unwrap(result: Any) -> Any:
    """CallToolResult から人間/機械が読める形を取り出す。"""
    data = getattr(result, "data", None)
    if data is not None:
        return data
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        return structured
    blocks = getattr(result, "content", None) or []
    texts = [t for t in (getattr(b, "text", None) for b in blocks) if t]
    return texts[0] if len(texts) == 1 else texts


def _subsidy_ids(search_result: Any) -> list[str]:
    """search_subsidies の戻り値から補助金 ID を列挙する。"""
    payload = search_result
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return []
    if isinstance(payload, dict):
        for key in ("result", "subsidies", "data", "items"):
            if isinstance(payload.get(key), list):
                payload = payload[key]
                break
    if not isinstance(payload, list):
        return []
    ids = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        for key in ("id", "subsidy_id", "subsidyId"):
            if item.get(key):
                ids.append(str(item[key]))
                break
    return ids


def _first_subsidy_id(search_result: Any) -> str | None:
    ids = _subsidy_ids(search_result)
    return ids[0] if ids else None


def _first_saved_filename(detail_result: Any) -> str | None:
    """get_subsidy_detail が保存した添付ファイル名を 1 件拾う。"""
    payload = detail_result
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return None
    if not isinstance(payload, dict):
        return None
    files = payload.get("files")
    if not isinstance(files, dict):
        return None
    for entries in files.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, dict) and entry.get("name") and not entry.get("error"):
                return str(entry["name"])
    return None


async def _find_downloaded_file(
    client: Client, search_result: Any, detail_result: Any, detail_id: str | None
) -> tuple[str, str] | None:
    """get_file_content に渡せる (補助金 ID, ファイル名) を探す。

    まず取得済みの詳細を見て、無ければ検索結果の先頭から数件だけ詳細を引き直す。
    """
    filename = _first_saved_filename(detail_result)
    if detail_id and filename:
        return detail_id, filename

    for candidate in _subsidy_ids(search_result)[:FILE_PROBE_LIMIT]:
        if candidate == detail_id:
            continue
        try:
            detail = await _call(client, "get_subsidy_detail", {"subsidy_id": candidate})
        except Exception:  # noqa: BLE001 - 候補探索なので個別の失敗は無視する
            continue
        filename = _first_saved_filename(detail)
        if filename:
            return candidate, filename
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000/mcp", help="MCP エンドポイント")
    parser.add_argument("--keyword", default="IT導入", help="search_subsidies に渡すキーワード")
    parser.add_argument("--out", default="results/jgrants-mcp.json", help="結果 JSON の出力先")
    args = parser.parse_args()

    reporter = asyncio.run(verify(args.url, args.keyword))
    reporter.write(args.out)
    print(f"tools: {', '.join(reporter.extra['tools']) or '(none)'}")
    return reporter.print_console(args.out)


if __name__ == "__main__":
    sys.exit(main())
