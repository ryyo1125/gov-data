#!/usr/bin/env python3
"""台帳に載る各情報源から、取得できる項目とその意味・取りうる値を抽出する。

台帳は「どこから何が取れるか」をエンドポイント粒度で記録するが、それだけでは
「取ってきた結果のこの項目は何か」に答えられない。ここではその 1 段下を埋める。

説明は自分で書かず、必ず提供側の資料から引く。出所と確度は情報源ごとに違うので、
どれなのかを origin として必ず残す。

- spec        : 提供側が定義した正式な項目（OpenAPI の schema、XML Schema など）
- observed    : レスポンスを実際に読んで列挙したもの。サンプルに現れなかった項目は落ちる
- spec+observed: 両方を組み合わせたもの

    python verify/extract_fields.py --out results/fields.json
"""

from __future__ import annotations

import argparse
import asyncio
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any

import httpx
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

LAW_SPEC_URL = "https://laws.e-gov.go.jp/api/2/swagger-ui/lawapi-v2.yaml"
CKAN_BASE = "https://data.e-gov.go.jp/data/api/3/action"
CKAN_DATASET_PAGE = "https://data.e-gov.go.jp/data/dataset"
JMA_FEED_BASE = "https://www.data.jma.go.jp/developer/xml/feed"
JMA_XSD_ZIP = "https://xml.kishou.go.jp/jmaxml_20241031_Schema%28xsd%29.zip"
# Jグランツの公式 OpenAPI。デジタル庁の開発者サイトではなく microCMS の
# アセット CDN にホストされているため、政府ドメインの許可だけでは到達できない。
JGRANTS_SPEC_URL = (
    "https://files.microcms-assets.io/assets/"
    "7c793323a46a46b7bb9a2ac7d0023301/2bad5ef79255448f8381d9cf2a14dbfc/jgrants-api.yaml"
)
ATOM = "{http://www.w3.org/2005/Atom}"
XS = "{http://www.w3.org/2001/XMLSchema}"

# 気象庁は電文種別ごとに Body の構造が違うため、系統の異なるフィードから拾う。
JMA_SAMPLE_FEEDS = ["regular", "extra", "eqvol", "other"]
# CKAN は項目の説明を API で返さないため、画面のラベルと値で突き合わせて補う。
CKAN_LABEL_SAMPLES = 15


# --------------------------------------------------------------------------
# e-Gov 法令 API: OpenAPI の schema から項目・説明・例・取りうる値を取る
# --------------------------------------------------------------------------

async def extract_law_fields(client: httpx.AsyncClient) -> dict:
    response = await client.get(LAW_SPEC_URL)
    response.raise_for_status()
    spec = yaml.safe_load(response.text)
    schemas = spec.get("components", {}).get("schemas", {})

    objects, enums = [], []
    for name, schema in sorted(schemas.items()):
        if schema.get("enum"):
            enums.append(
                {
                    "name": name,
                    "description": _enum_summary(schema.get("description")),
                    "values": _enum_values(schema),
                }
            )
            continue
        properties = schema.get("properties")
        if not properties:
            continue
        objects.append(
            {
                "name": name,
                "description": _clean(schema.get("description")),
                "fields": [
                    {
                        "name": field,
                        "type": _schema_type(definition),
                        "description": _clean(definition.get("description")),
                        "example": _clean(str(definition.get("example", ""))),
                    }
                    for field, definition in properties.items()
                ],
            }
        )

    return {
        "origin": "spec",
        "origin_detail": f"OpenAPI {spec.get('info', {}).get('version')} の components/schemas。説明・例・取りうる値はすべて仕様に書かれているもの",
        "source_url": LAW_SPEC_URL,
        "objects": objects,
        "enums": enums,
    }


def _enum_summary(description: str | None) -> str:
    """enum の説明から、値の一覧が始まる前の見出し部分だけを取る。"""
    head = re.split(r"\n\s*\*", description or "")[0]
    return _clean(head).rstrip(":：").strip()


def _enum_values(schema: dict) -> list[dict]:
    """enum の description に書かれた「値 - 意味」の対応を拾う。

    法令 API は `* \\`Act\\` - 法律` の形式で意味を書いているため、
    値だけを並べるより遥かに使える一覧になる。
    """
    meanings = dict(re.findall(r"\*\s+`([^`]+)`\s*-\s*([^\n<]+)", schema.get("description") or ""))
    return [
        {"value": value, "meaning": _clean(meanings.get(value, ""))}
        for value in schema.get("enum", [])
    ]


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


def _clean(text: str | None) -> str:
    """HTML タグと改行を落として 1 行にする。表のセルに収めるため。"""
    if not text:
        return ""
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(unescape(text).split())


# --------------------------------------------------------------------------
# e-Gov データポータル: API は説明を返さないので、画面のラベルを値で突き合わせる
# --------------------------------------------------------------------------

async def extract_ckan_fields(client: httpx.AsyncClient) -> dict:
    response = await client.get(f"{CKAN_BASE}/package_search", params={"rows": 20})
    response.raise_for_status()
    packages = response.json()["result"]["results"]

    labels = await _ckan_labels(client, packages[:CKAN_LABEL_SAMPLES])

    dataset_fields: dict[str, set[str]] = {}
    resource_fields: dict[str, set[str]] = {}
    for package in packages:
        _collect(package, dataset_fields)
        for resource in package.get("resources") or []:
            _collect(resource, resource_fields)

    return {
        "origin": "observed",
        "origin_detail": (
            f"package_search で取得した {len(packages)} 件に現れた項目の和。"
            f"説明は先頭 {CKAN_LABEL_SAMPLES} 件のデータセット画面に出る日本語ラベルを、"
            "同じ値を持つ API の項目と突き合わせて対応付けたもの（値が一意に一致したものだけ採用）"
        ),
        "source_url": f"{CKAN_BASE}/package_search",
        "objects": [
            {
                "name": "package（データセット）",
                "description": "1 件のデータセットを表す。resources に実ファイルがぶら下がる。",
                "fields": _as_fields(dataset_fields, labels),
            },
            {
                "name": "resource（データセットに紐づくファイル）",
                "description": "データセットが提供する個々のファイルや API のエンドポイント。",
                "fields": _as_fields(resource_fields, labels),
            },
        ],
        "enums": [],
    }


async def _ckan_labels(client: httpx.AsyncClient, packages: list[dict]) -> dict[str, str]:
    """データセット画面の th/td から、API の項目名に対応する日本語ラベルを推定する。

    CKAN の API は項目の説明を返さないが、画面には日本語ラベルが出ている。
    同じデータセットの同じ値を手掛かりに対応付ければ、推測せずにラベルを得られる。
    値が複数の項目とぶつかったものは曖昧なので捨てる。
    """
    candidates: dict[str, set[str]] = {}
    for package in packages:
        name = package.get("name")
        if not name:
            continue
        try:
            page = await client.get(f"{CKAN_DATASET_PAGE}/{name}")
            page.raise_for_status()
        except Exception:  # noqa: BLE001 - 画面が無い/変わっただけなのでラベル無しで続行
            continue

        pairs = re.findall(
            r"<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>", page.text, re.S
        )
        by_value: dict[str, set[str]] = {}
        for label, value in pairs:
            value = _clean(value)
            if value:
                by_value.setdefault(value, set()).add(_clean(label))

        # 同じ値を持つ項目が複数あると、どのラベルが誰のものか決められない。
        # ラベル側・項目側の両方で値が一意なときだけ対応付ける。
        keys_by_value: dict[str, set[str]] = {}
        for key, value in package.items():
            text = _clean(value) if isinstance(value, str) else ""
            if text:
                keys_by_value.setdefault(text, set()).add(key)

        for value, keys in keys_by_value.items():
            matched = by_value.get(value)
            if len(keys) == 1 and matched and len(matched) == 1:
                candidates.setdefault(next(iter(keys)), set()).update(matched)

    return {key: next(iter(labels)) for key, labels in candidates.items() if len(labels) == 1}


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


def _as_fields(collected: dict[str, set[str]], labels: dict[str, str]) -> list[dict]:
    fields = []
    for name, types in sorted(collected.items()):
        notes = []
        if labels.get(name):
            notes.append(labels[name])
        if types == {"null"}:
            # null しか観測できなかった項目は、値の入り方が分からないことを明示する。
            notes.append("サンプル内では常に null")
        concrete = sorted(types - {"null"}) or ["null"]
        fields.append(
            {
                "name": name,
                "type": " | ".join(concrete),
                "description": " / ".join(notes),
                "example": "",
            }
        )
    return fields


# --------------------------------------------------------------------------
# 気象庁: XML Schema から全電文共通の構造を、実データから電文ごとの構造を取る
# --------------------------------------------------------------------------

async def extract_jma_fields(client: httpx.AsyncClient) -> dict:
    objects = await _jma_schema_objects(client)
    feed_fields, documents = await _jma_observed(client)

    return {
        "origin": "spec+observed",
        "origin_detail": (
            "全電文共通の Report / Control / Head は公式の XML Schema（jmx.xsd, jmx_ib.xsd）から。"
            f"Atom フィードと電文 {len(documents)} 通の構造は実データから列挙。"
            "電文種別は多数あり、ここに出るのはその一部"
        ),
        "source_url": JMA_XSD_ZIP,
        "objects": [
            *objects,
            {
                "name": "Atom フィード（実データ由来）",
                "description": "電文の入電を知らせるフィード。entry の link から電文本体を取得する。",
                "fields": _as_fields(feed_fields, {}),
            },
            *documents,
        ],
        "enums": [],
    }


async def _jma_schema_objects(client: httpx.AsyncClient) -> list[dict]:
    """XSD を取得し、Report / Control / Head の要素定義を組み立てる。

    Body は電文種別ごとに構造が違って巨大なため、ここでは全電文に共通する
    管理部・ヘッダ部だけを扱う。どの電文でも必ず現れるので実用上の価値が高い。
    """
    response = await client.get(JMA_XSD_ZIP)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        sources = {
            Path(name).name: archive.read(name).decode("utf-8")
            for name in archive.namelist()
            if name.endswith(".xsd")
        }

    objects = []
    for filename, type_names in [("jmx.xsd", ["type.report", "type.control"]), ("jmx_ib.xsd", None)]:
        if filename not in sources:
            continue
        root = ET.fromstring(sources[filename])
        for complex_type in root.findall(f"{XS}complexType"):
            name = complex_type.get("name")
            if type_names is not None and name not in type_names:
                continue
            if type_names is None and name != "type.head":
                continue
            objects.append(
                {
                    "name": f"{name}（XML Schema 由来 / {filename}）",
                    "description": _xsd_doc(complex_type),
                    "fields": _xsd_fields(complex_type),
                }
            )
    return objects


def _xsd_fields(complex_type: ET.Element) -> list[dict]:
    fields = []
    for element in complex_type.iter(f"{XS}element"):
        name = element.get("name") or element.get("ref", "").rsplit(":", 1)[-1]
        if not name:
            continue
        min_occurs = element.get("minOccurs", "1")
        max_occurs = element.get("maxOccurs", "1")
        required = "必須" if min_occurs != "0" else "任意"
        repeats = "" if max_occurs == "1" else f" / 繰り返し {min_occurs}..{max_occurs}"
        fields.append(
            {
                "name": name,
                "type": (element.get("type") or "要素").rsplit(":", 1)[-1],
                "description": (_xsd_doc(element) + f"（{required}{repeats}）").strip(),
                "example": "",
            }
        )
    return fields


def _xsd_doc(element: ET.Element) -> str:
    documentation = element.find(f"{XS}annotation/{XS}documentation")
    return _clean(documentation.text) if documentation is not None else ""


async def _jma_observed(client: httpx.AsyncClient) -> tuple[dict[str, set[str]], list[dict]]:
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
                "name": f"電文 Body: {title.text if title is not None else feed}（実データ由来 / {feed} フィード）",
                "description": "この電文種別に固有の Body 構造。種別ごとに異なるため、他の電文には当てはまらない。",
                "fields": [
                    {"name": path, "type": "要素", "description": "", "example": ""}
                    for path in _element_paths(ET.fromstring(document.text))
                ],
            }
        )

    return feed_fields, documents


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


# --------------------------------------------------------------------------
# Jグランツ: MCP のツール定義と実レスポンスから
# --------------------------------------------------------------------------

async def extract_jgrants_fields(url: str) -> dict:
    from fastmcp import Client

    spec, spec_objects, descriptions = await _jgrants_spec()

    client = Client(url)
    async with client:
        tools = await client.list_tools()
        objects = [
            {
                "name": f"{tool.name}（入力）",
                "description": _clean((tool.description or "").split("\n")[0]),
                "fields": [
                    {
                        "name": field,
                        "type": _schema_type(definition),
                        "description": _clean(definition.get("description"))
                        or ("必須" if field in (tool.inputSchema.get("required") or []) else ""),
                        "example": _clean(str(definition.get("default", ""))),
                    }
                    for field, definition in (tool.inputSchema.get("properties") or {}).items()
                ],
            }
            for tool in sorted(tools, key=lambda t: t.name)
        ]

        search = await client.call_tool("search_subsidies", {"keyword": "IT導入"})
        subsidies = (getattr(search, "data", None) or {}).get("subsidies") or []
        if subsidies:
            collected: dict[str, set[str]] = {}
            for subsidy in subsidies:
                _collect(subsidy, collected)
            objects.append(
                {
                    "name": "search_subsidies の戻り値（subsidies[]）",
                    "description": "検索にヒットした補助金 1 件分。説明は公式 OpenAPI の同名項目から引いている。",
                    "fields": _as_fields(collected, descriptions),
                }
            )

            detail = await client.call_tool("get_subsidy_detail", {"subsidy_id": subsidies[0]["id"]})
            collected = {}
            _collect(getattr(detail, "data", None) or {}, collected)
            objects.append(
                {
                    "name": "get_subsidy_detail の戻り値",
                    "description": "補助金 1 件の詳細。files は MCP サーバーが添付を保存した結果で、公式 API には無い項目。",
                    "fields": _as_fields(collected, descriptions),
                }
            )

    # 公式仕様のオブジェクトは、MCP を経由せず API を直接叩く場合の参照にもなる。
    objects.extend(spec_objects)

    return {
        "origin": "spec+observed",
        "origin_detail": (
            f"入力項目は MCP のツール定義。戻り値の項目は実レスポンスから列挙し、説明は"
            f"公式 OpenAPI（{spec.get('info', {}).get('title')} {spec.get('info', {}).get('version')}）の"
            "同名項目から引いた。仕様側のオブジェクト定義も併記している"
        ),
        "source_url": JGRANTS_SPEC_URL,
        "objects": objects,
        "enums": [],
    }


async def _jgrants_spec() -> tuple[dict, list[dict], dict[str, str]]:
    """公式 OpenAPI を取得し、オブジェクト定義と「項目名 → 説明」の対応を返す。

    MCP のレスポンスは公式 API の項目をそのまま通すため、名前で突き合わせれば
    実データ由来の項目に仕様の説明を付けられる。同名で説明が食い違う項目は、
    どちらが正しいか決められないので対応から外す。
    """
    async with httpx.AsyncClient(timeout=90.0, trust_env=True) as client:
        response = await client.get(JGRANTS_SPEC_URL)
        response.raise_for_status()
    spec = yaml.safe_load(response.text)

    objects, seen = [], {}
    for name, schema in (spec.get("components", {}).get("schemas") or {}).items():
        properties = schema.get("properties") or {}
        if not properties:
            continue
        objects.append(
            {
                "name": f"{name}（公式 OpenAPI 由来）",
                "description": _clean(schema.get("description")),
                "fields": [
                    {
                        "name": field,
                        "type": _schema_type(definition),
                        "description": _clean(definition.get("description")),
                        "example": _clean(str(definition.get("example", ""))),
                    }
                    for field, definition in properties.items()
                ],
            }
        )
        for field, definition in properties.items():
            description = _clean(definition.get("description"))
            if not description:
                continue
            seen.setdefault(field, set()).add(description)

    descriptions = {k: next(iter(v)) for k, v in seen.items() if len(v) == 1}
    return spec, objects, descriptions


# --------------------------------------------------------------------------

async def extract_all(jgrants_url: str | None) -> dict:
    sources: dict[str, Any] = {}
    async with httpx.AsyncClient(timeout=120.0, trust_env=True) as client:
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

    result = asyncio.run(extract_all(args.jgrants_url))
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)

    failed = 0
    for source_id, data in result["sources"].items():
        if "error" in data:
            print(f"  [FAIL ] {source_id} - {data['error']}")
            failed += 1
            continue
        fields = [f for o in data["objects"] for f in o["fields"]]
        described = sum(1 for f in fields if f["description"])
        enum_values = sum(len(e["values"]) for e in data["enums"])
        print(
            f"  [OK   ] {source_id} - {len(data['objects'])} オブジェクト / {len(fields)} 項目"
            f"（説明あり {described}）/ 取りうる値 {enum_values} ({data['origin']})"
        )
    print(f"-> {args.out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
