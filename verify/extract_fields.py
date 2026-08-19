#!/usr/bin/env python3
"""台帳に載る各情報源から、実際に取得できる項目（フィールド）の一覧を抽出する。

台帳は「どこから何が取れるか」をエンドポイント粒度で記録するが、それだけでは
「取ってきた結果にどの項目が入っているか」が分からない。ここではその 1 段下を埋める。

項目の出所は情報源ごとに違い、確度も違う。どちらなのかを origin として必ず残す。

- 仕様由来（OpenAPI の schema、MCP のツール定義）: 提供側が定義した正式な項目
- 実データ由来（レスポンスを実際に読んで列挙）: 仕様が無い場合の実測。
  サンプルに含まれなかった項目は落ちるので、網羅の保証は無い

    python verify/extract_fields.py --out results/fields.json
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

LAW_SPEC_URL = "https://laws.e-gov.go.jp/api/2/swagger-ui/lawapi-v2.yaml"
CKAN_BASE = "https://data.e-gov.go.jp/data/api/3/action"
JMA_FEED_BASE = "https://www.data.jma.go.jp/developer/xml/feed"
ATOM = "{http://www.w3.org/2005/Atom}"

# 気象庁は電文種別ごとに Body の構造が違うため、系統の異なるフィードから拾う。
JMA_SAMPLE_FEEDS = ["regular", "extra", "eqvol", "other"]


async def extract_law_fields(client: httpx.AsyncClient) -> dict:
    """e-Gov 法令 API: OpenAPI の components/schemas から項目定義を取る。"""
    response = await client.get(LAW_SPEC_URL)
    response.raise_for_status()
    spec = yaml.safe_load(response.text)
    schemas = spec.get("components", {}).get("schemas", {})

    objects, enums = [], []
    for name, schema in sorted(schemas.items()):
        if schema.get("enum"):
            enums.append({"name": name, "values": schema["enum"]})
            continue
        properties = schema.get("properties")
        if not properties:
            continue
        objects.append(
            {
                "name": name,
                "fields": [
                    {
                        "name": field,
                        "type": _schema_type(definition),
                        "description": _first_line(definition.get("description")),
                    }
                    for field, definition in properties.items()
                ],
            }
        )

    return {
        "origin": "spec",
        "origin_detail": f"OpenAPI {spec.get('info', {}).get('version')} の components/schemas",
        "source_url": LAW_SPEC_URL,
        "objects": objects,
        "enums": enums,
    }


def _schema_type(definition: dict) -> str:
    """$ref や配列を、読める型名 1 つに畳む。"""
    if "$ref" in definition:
        return definition["$ref"].rsplit("/", 1)[-1]
    if definition.get("type") == "array":
        return f"{_schema_type(definition.get('items', {}))}[]"
    for key in ("allOf", "oneOf", "anyOf"):
        if definition.get(key):
            return _schema_type(definition[key][0])
    return definition.get("type", "unknown")


def _first_line(text: str | None) -> str:
    if not text:
        return ""
    for line in text.splitlines():
        cleaned = line.strip().lstrip("> ").strip()
        if cleaned:
            return cleaned[:120]
    return ""


async def extract_ckan_fields(client: httpx.AsyncClient) -> dict:
    """CKAN: 仕様ではなく実データから。複数件の和を取って欠損項目を拾う。"""
    response = await client.get(f"{CKAN_BASE}/package_search", params={"rows": 20})
    response.raise_for_status()
    packages = response.json()["result"]["results"]

    dataset_fields: dict[str, set[str]] = {}
    resource_fields: dict[str, set[str]] = {}
    for package in packages:
        _collect(package, dataset_fields)
        for resource in package.get("resources") or []:
            _collect(resource, resource_fields)

    return {
        "origin": "observed",
        "origin_detail": f"package_search で取得した {len(packages)} 件のデータセットに現れた項目の和",
        "source_url": f"{CKAN_BASE}/package_search",
        "objects": [
            {"name": "package（データセット）", "fields": _as_fields(dataset_fields, len(packages))},
            {"name": "resource（データセットに紐づくファイル）", "fields": _as_fields(resource_fields, None)},
        ],
        "enums": [],
    }


def _collect(record: dict, into: dict[str, set[str]]) -> None:
    for key, value in record.items():
        into.setdefault(key, set()).add(_value_type(value))


def _value_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"


def _as_fields(collected: dict[str, set[str]], sample_size: int | None) -> list[dict]:
    fields = []
    for name, types in sorted(collected.items()):
        # null しか観測できなかった項目は、値の入り方が分からないことを明示する。
        note = "サンプル内では常に null" if types == {"null"} else ""
        concrete = sorted(types - {"null"}) or ["null"]
        fields.append({"name": name, "type": " | ".join(concrete), "description": note})
    return fields


async def extract_jma_fields(client: httpx.AsyncClient) -> dict:
    """気象庁: Atom フィードと電文本体を実際に読み、要素の階層を列挙する。"""
    feed_fields: dict[str, set[str]] = {}
    documents: list[dict] = []

    for feed in JMA_SAMPLE_FEEDS:
        response = await client.get(f"{JMA_FEED_BASE}/{feed}.xml")
        response.raise_for_status()
        root = ET.fromstring(response.text)
        for child in root:
            feed_fields.setdefault(_local(child.tag), set()).add("string")
        entries = root.findall(f"{ATOM}entry")
        if not entries:
            continue
        for child in entries[0]:
            feed_fields.setdefault(f"entry/{_local(child.tag)}", set()).add("string")

        link = entries[0].find(f"{ATOM}link")
        title = entries[0].find(f"{ATOM}title")
        if link is None:
            continue
        document = await client.get(link.get("href"))
        document.raise_for_status()
        documents.append(
            {
                "name": f"電文: {title.text if title is not None else feed}（{feed} フィードより）",
                "fields": [
                    {"name": path, "type": "element", "description": ""}
                    for path in _element_paths(ET.fromstring(document.text))
                ],
            }
        )

    return {
        "origin": "observed",
        "origin_detail": (
            f"{len(JMA_SAMPLE_FEEDS)} 本のフィードと、それぞれの先頭 entry が指す電文 "
            f"{len(documents)} 通を実際に読んで列挙。電文種別は多数あり、ここに出るのはその一部"
        ),
        "source_url": JMA_FEED_BASE,
        "objects": [
            {"name": "Atom フィード", "fields": _as_fields(feed_fields, None)},
            *documents,
        ],
        "enums": [],
    }


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _element_paths(root: ET.Element, max_depth: int = 3) -> list[str]:
    """電文の要素ツリーを、深さを切って重複なくパス表記で返す。"""
    paths: list[str] = []
    seen: set[str] = set()

    def walk(element: ET.Element, prefix: str, depth: int) -> None:
        for child in element:
            path = f"{prefix}/{_local(child.tag)}" if prefix else _local(child.tag)
            if path not in seen:
                seen.add(path)
                paths.append(path)
            if depth < max_depth:
                walk(child, path, depth + 1)

    walk(root, _local(root.tag), 1)
    return paths


async def extract_jgrants_fields(url: str) -> dict:
    """Jグランツ: MCP のツール定義（入力スキーマ）と、実レスポンスの項目を併記する。"""
    from fastmcp import Client

    client = Client(url)
    async with client:
        tools = await client.list_tools()
        objects = [
            {
                "name": f"{tool.name}（入力）",
                "fields": [
                    {
                        "name": field,
                        "type": _schema_type(definition),
                        "description": "必須" if field in (tool.inputSchema.get("required") or []) else "",
                    }
                    for field, definition in (tool.inputSchema.get("properties") or {}).items()
                ],
            }
            for tool in tools
        ]

        search = await client.call_tool("search_subsidies", {"keyword": "IT導入"})
        payload = getattr(search, "data", None) or {}
        subsidies = payload.get("subsidies") or []
        if subsidies:
            collected: dict[str, set[str]] = {}
            for subsidy in subsidies:
                _collect(subsidy, collected)
            objects.append(
                {"name": "search_subsidies の戻り値（subsidies[]）", "fields": _as_fields(collected, None)}
            )
        if subsidies:
            detail = await client.call_tool("get_subsidy_detail", {"subsidy_id": subsidies[0]["id"]})
            detail_payload = getattr(detail, "data", None) or {}
            collected = {}
            _collect(detail_payload, collected)
            objects.append({"name": "get_subsidy_detail の戻り値", "fields": _as_fields(collected, None)})

    return {
        "origin": "spec+observed",
        "origin_detail": "入力項目は MCP のツール定義、戻り値の項目は実レスポンスから列挙",
        "source_url": url,
        "objects": objects,
        "enums": [],
    }


async def extract_all(jgrants_url: str | None) -> dict:
    sources: dict[str, Any] = {}
    async with httpx.AsyncClient(timeout=90.0, trust_env=True) as client:
        for source_id, extractor in [
            ("egov-hourei-api", extract_law_fields),
            ("egov-data-catalog", extract_ckan_fields),
            ("jma-xml", extract_jma_fields),
        ]:
            try:
                sources[source_id] = await extractor(client)
            except Exception as exc:  # noqa: BLE001 - 抽出できなかった理由をそのまま残す
                sources[source_id] = {"error": f"{type(exc).__name__}: {exc}"}

    if jgrants_url:
        try:
            sources["jgrants-mcp"] = await extract_jgrants_fields(jgrants_url)
        except Exception as exc:  # noqa: BLE001
            sources["jgrants-mcp"] = {"error": f"{type(exc).__name__}: {exc}"}
    else:
        sources["jgrants-mcp"] = {
            "error": "MCP サーバーの URL が指定されなかったため未抽出（--jgrants-url を渡す）"
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generated_by": "verify/extract_fields.py",
        "sources": sources,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jgrants-url", default=None, help="起動済み Jグランツ MCP の URL")
    parser.add_argument("--out", default="results/fields.json", help="結果 JSON の出力先")
    args = parser.parse_args()

    import json

    result = asyncio.run(extract_all(args.jgrants_url))
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)

    failed = 0
    for source_id, data in result["sources"].items():
        if "error" in data:
            print(f"  [FAIL ] {source_id} - {data['error']}")
            failed += 1
        else:
            count = sum(len(o["fields"]) for o in data["objects"])
            print(f"  [OK   ] {source_id} - {len(data['objects'])} オブジェクト / {count} 項目 ({data['origin']})")
    print(f"-> {args.out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
