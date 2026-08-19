#!/usr/bin/env python3
"""デジタル庁「Jグランツ MCP Server」への接続・利用検証スクリプト。

Streamable-HTTP で起動済みの MCP サーバーに接続し、
initialize / tools・resources・prompts の列挙 / 各ツールの実行を順に試して
結果を JSON で書き出す。

使い方:
    python -m jgrants_mcp_server.core --host 127.0.0.1 --port 8000   # 別プロセスで起動
    python verify/verify_jgrants_mcp.py --url http://127.0.0.1:8000/mcp \
        --out results/jgrants-verification.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
import traceback
from typing import Any

from fastmcp import Client

FILE_PROBE_LIMIT = 5


def _unwrap(result: Any) -> Any:
    """CallToolResult から人間/機械が読める形を取り出す。"""
    data = getattr(result, "data", None)
    if data is not None:
        return data
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        return structured
    blocks = getattr(result, "content", None) or []
    texts = [getattr(b, "text", None) for b in blocks]
    texts = [t for t in texts if t]
    return texts[0] if len(texts) == 1 else texts


def _preview(value: Any, limit: int = 1500) -> Any:
    """レポートに載せるため大きな戻り値を切り詰める。"""
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    if len(text) <= limit:
        return value
    return {"_truncated": True, "_original_chars": len(text), "_head": text[:limit]}


async def run_step(report: list[dict], name: str, coro) -> Any:
    """1 ステップ実行し、成功/失敗と所要時間を report に記録する。"""
    started = time.monotonic()
    try:
        value = await coro
    except Exception as exc:  # noqa: BLE001 - 検証目的なので全例外を記録する
        report.append(
            {
                "step": name,
                "ok": False,
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(limit=3),
            }
        )
        return None
    report.append(
        {
            "step": name,
            "ok": True,
            "elapsed_ms": round((time.monotonic() - started) * 1000),
            "result": _preview(value),
        }
    )
    return value


async def verify(url: str, keyword: str) -> dict:
    report: list[dict] = []
    client = Client(url)

    async with client:
        await run_step(report, "initialize", _initialize(client))

        tools = await run_step(report, "list_tools", _list_tools(client))
        await run_step(report, "list_resources", _list_resources(client))
        await run_step(report, "list_prompts", _list_prompts(client))

        await run_step(report, "call:ping", _call(client, "ping", {}))

        search = await run_step(
            report,
            "call:search_subsidies",
            _call(client, "search_subsidies", {"keyword": keyword}),
        )

        subsidy_id = _first_subsidy_id(search)
        detail = None
        if subsidy_id:
            detail = await run_step(
                report,
                "call:get_subsidy_detail",
                _call(client, "get_subsidy_detail", {"subsidy_id": subsidy_id}),
            )
        else:
            report.append(
                {
                    "step": "call:get_subsidy_detail",
                    "ok": False,
                    "error": "search_subsidies の戻り値から補助金 ID を取得できなかったため未実行",
                }
            )

        await run_step(
            report,
            "call:get_subsidy_overview",
            _call(client, "get_subsidy_overview", {"output_format": "json"}),
        )

        target = await _find_downloaded_file(client, search, detail, subsidy_id)
        if target:
            file_owner, filename = target
            await run_step(
                report,
                "call:get_file_content",
                _call(
                    client,
                    "get_file_content",
                    {"subsidy_id": file_owner, "filename": filename, "return_format": "markdown"},
                ),
            )
        else:
            report.append(
                {
                    "step": "call:get_file_content",
                    "ok": True,
                    "skipped": True,
                    "note": f"検索結果の先頭 {FILE_PROBE_LIMIT} 件に添付ファイルが無かったため未実行",
                }
            )

    tool_names = sorted(t.name for t in (tools or []))
    return {
        "url": url,
        "keyword": keyword,
        "tools": tool_names,
        "steps": report,
        "summary": {
            "total": len(report),
            "ok": sum(1 for s in report if s.get("ok") and not s.get("skipped")),
            "skipped": sum(1 for s in report if s.get("skipped")),
            "failed": sum(1 for s in report if not s.get("ok")),
        },
    }


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
    parser.add_argument("--out", default="results/jgrants-verification.json", help="結果 JSON の出力先")
    args = parser.parse_args()

    result = asyncio.run(verify(args.url, args.keyword))

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)

    summary = result["summary"]
    print(f"tools: {', '.join(result['tools']) or '(none)'}")
    for step in result["steps"]:
        if step.get("skipped"):
            print(f"  [SKIP] {step['step']} - {step.get('note')}")
        elif step.get("ok"):
            print(f"  [OK  ] {step['step']}")
        else:
            print(f"  [FAIL] {step['step']} - {step.get('error')}")
    print(
        f"{summary['ok']} ok / {summary['skipped']} skipped / {summary['failed']} failed"
        f" (total {summary['total']}) -> {args.out}"
    )
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
