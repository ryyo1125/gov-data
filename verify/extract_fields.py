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
import math
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
NDL_API_BASE = "https://ndlsearch.ndl.go.jp/api"
# NDL は同時リクエスト数の制限と大量アクセスの遮断を一次資料に明記している。
NDL_REQUEST_INTERVAL = 5
NDL_RETRY_AFTER_429 = 30
ESTAT_LOD_ENDPOINT = "https://data.e-stat.go.jp/lod/sparql/alldata/query"
GSI_TILE_BASE = "https://cyberjapandata.gsi.go.jp/xyz"
GSI_DOC_BASE = "https://maps.gsi.go.jp/development"
# タイル座標の基準にする地点（東京駅）。座標を直接書くと、どこを見ているのかが読めない。
GSI_SAMPLE_LAT, GSI_SAMPLE_LON = 35.6812, 139.7671
JGRANTS_SPEC_URL = (
    "https://files.microcms-assets.io/assets/"
    "7c793323a46a46b7bb9a2ac7d0023301/2bad5ef79255448f8381d9cf2a14dbfc/jgrants-api.yaml"
)
ATOM = "{http://www.w3.org/2005/Atom}"
OAI = "{http://www.openarchives.org/OAI/2.0/}"
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

async def _ndl_get(client: httpx.AsyncClient, path: str, **kwargs) -> httpx.Response:
    """429 を 1 回だけ待って引き直す。制限は先方の仕様であって障害ではない。

    verify/verify_ndl_search.py と同じ扱いにしてある。再試行を 1 回に限るのは、
    塞がれている相手を叩き続けないため。
    """
    response = await client.get(f"{NDL_API_BASE}{path}", **kwargs)
    if response.status_code == 429:
        await asyncio.sleep(NDL_RETRY_AFTER_429)
        response = await client.get(f"{NDL_API_BASE}{path}", **kwargs)
    response.raise_for_status()
    return response


async def extract_ndl_fields(client: httpx.AsyncClient) -> dict:
    """NDLサーチ: 各経路が実際に返す要素を読んで列挙する。

    仕様書は PDF で配布されており機械可読ではないため、ここは実データ由来になる。
    レート制限があるので、間隔を空けて必要最小限だけ叩く。

    この抽出は同じ通しの中で検証スクリプトが NDL を叩いた直後に走るため、
    実際に 429 を返されて項目一覧から NDL が丸ごと落ちたことがある。
    先方が明記している制限に当たっただけなので、待って引き直す。
    """
    objects = []

    response = await _ndl_get(client, "/opensearch", params={"cnt": 1, "title": "桜"})
    root = ET.fromstring(response.text)
    channel = root.find("channel")
    item = channel.find("item") if channel is not None else None
    objects.append(
        {
            "name": "OpenSearch: channel（RSS）",
            "description": "検索結果全体。件数と取得位置がここに入る。",
            "fields": _element_fields(channel, skip={"item"}),
        }
    )
    objects.append(
        {
            "name": "OpenSearch: item（書誌 1 件）",
            "description": "検索にヒットした資料 1 件分。同名要素が繰り返し現れることがある。",
            "fields": _element_fields(item),
        }
    )

    await asyncio.sleep(NDL_REQUEST_INTERVAL)
    response = await _ndl_get(client, "/oaipmh", params={"verb": "Identify"})
    root = ET.fromstring(response.text)
    identify = root.find(f"{OAI}Identify")
    objects.append(
        {
            "name": "OAI-PMH: Identify（リポジトリ情報）",
            "description": "ハーベスト前に確認する、リポジトリの素性と差分取得の粒度。",
            "fields": _element_fields(identify),
        }
    )

    return {
        "origin": "observed",
        "origin_detail": (
            "各経路のレスポンスを実際に読んで列挙。API 仕様書は PDF で配布されており"
            "機械可読ではないため、仕様由来の項目定義は取り込めていない"
        ),
        "source_url": "https://ndlsearch.ndl.go.jp/help/api/specifications",
        "objects": objects,
        "enums": [],
    }


def _element_fields(parent, skip: set[str] | None = None) -> list[dict]:
    """XML の子要素を、出現順・重複なしで項目として並べる。"""
    if parent is None:
        return []
    skip = skip or set()
    seen: dict[str, str] = {}
    for child in parent:
        name = _local(child.tag)
        if name in skip:
            continue
        seen.setdefault(name, (child.text or "").strip()[:60])
    return [
        {"name": name, "type": "要素", "description": "", "example": example}
        for name, example in seen.items()
    ]


# --------------------------------------------------------------------------
# 地理院タイル: 一覧ページのデータ ID と、仕様ページの項目定義を突き合わせる
# --------------------------------------------------------------------------

async def extract_gsi_tiles_fields(client: httpx.AsyncClient) -> dict:
    """地理院タイル: URL のパラメータ・標高タイルのセル・GeoJSON の属性を集める。

    この情報源で「項目」にあたるものは 3 層に分かれている。

    1. URL テンプレートのパラメータ（何を指定して取るか）— 仕様ページに定義がある
    2. 標高タイルのセル／画素（取れた中身の読み方）— 詳細仕様に定義がある
    3. GeoJSON タイルのプロパティ（点データの属性）— 仕様書が無いので実データから

    データ ID は一覧ページにしか列挙されていないので、そこから拾う。
    """
    index = await client.get(f"{GSI_DOC_BASE}/ichiran.html")
    index.raise_for_status()
    catalog = _gsi_catalog(index.text)

    spec = await client.get(f"{GSI_DOC_BASE}/siyou.html")
    spec.raise_for_status()
    dem_spec = await client.get(f"{GSI_DOC_BASE}/demtile.html")
    dem_spec.raise_for_status()

    objects = [
        {
            "name": "URL テンプレートのパラメータ",
            "description": (
                "タイル 1 枚の URL は "
                "https://cyberjapandata.gsi.go.jp/xyz/{t}/{z}/{x}/{y}.{ext} で、"
                "この 5 つを埋めて GET する。説明は仕様ページの記述をそのまま引いた。"
            ),
            "fields": _gsi_url_parameters(spec.text),
        },
        {
            "name": "標高タイル（テキスト形式・.txt）のセル",
            "description": (
                "1 行に 256 個の標高値がカンマ区切りで並び、それが 256 行。"
                "地図タイルのピクセル座標に対応する。"
            ),
            "fields": _gsi_dem_text_fields(dem_spec.text),
        },
        {
            "name": "標高タイル（PNG 形式・.png）の画素",
            "description": (
                "24 ビットカラー PNG の画素値から標高値を計算する。"
                "x = 2^16 R + 2^8 G + B とし、x < 2^23 なら h = xu、x = 2^23 なら NA、"
                "x > 2^23 なら h = (x - 2^24)u（u は標高分解能 0.01m）。"
            ),
            "fields": _gsi_dem_png_fields(dem_spec.text),
        },
    ]

    # GeoJSON タイルの属性は仕様書が無い。実データを読んで列挙する。
    for data_id, zoom, label in (("skhb01", 10, "指定緊急避難場所（洪水）"),
                                 ("disaster_lore_all", 7, "自然災害伝承碑（すべて）")):
        objects.append(await _gsi_geojson_object(client, data_id, zoom, label))

    # 一覧ページの備考が、自然災害伝承碑について公開している情報を列挙している。
    # ただし GeoJSON のキーとの対応は書かれていないので、別の表として並べる。
    objects.append(_gsi_lore_documented(index.text))

    return {
        "origin": "spec+observed",
        "origin_detail": (
            "URL パラメータと標高タイルの読み方は仕様ページ・標高タイルの詳細仕様から、"
            "データ ID の一覧と提供条件は一覧ページから引いた。GeoJSON タイルの属性だけは"
            "定義書が無いため実データから列挙しており、そのタイルに現れなかった属性は落ちる"
        ),
        "source_url": "https://maps.gsi.go.jp/development/ichiran.html",
        "objects": objects,
        "enums": [
            {
                "name": "{t}（データ ID）",
                "description": (
                    "一覧ページに載っている配信中のタイル。"
                    "意味の欄は「名称（URL に添えられた注記）｜利用条件の分類｜"
                    "ズームレベル｜提供範囲」の順に、一覧ページの記載を並べたもの"
                ),
                "values": catalog,
            },
            {
                "name": "自然災害伝承碑の災害種別",
                "description": "一覧ページの備考が列挙している値",
                "values": [
                    {"value": kind, "meaning": ""}
                    for kind in _gsi_lore_disaster_kinds(index.text)
                ],
            },
        ],
    }


def _gsi_catalog(html_text: str) -> list[dict]:
    """一覧ページから、データ ID と提供条件の対応を組み立てる。

    ページは <h4 class="title"> の見出しの下に URL が並び、その後ろに
    ズームレベル・提供範囲の表が続く構造になっている。利用条件は
    「■ 1. 基本測量成果」などの区切りで変わるので、直前の区切りも持たせる。
    """
    text = unescape(html_text)
    sections = [
        (m.start(), _clean(m.group(1)))
        for m in re.finditer(r'<h4 class="h4_normal">(.*?)</h4>', text, re.S)
    ]
    titles = [
        (m.start(), _clean(m.group(1)))
        for m in re.finditer(r'<h4 class="title"[^>]*>(.*?)</h4>', text, re.S)
    ]

    # 同じデータ ID が複数の節に現れることがある。標準地図はズームレベルによって
    # 利用条件の分類が変わり、そのぶん別々の見出しの下に同じ URL が載っている。
    # 最初の 1 件で決めてしまうと、条件の一部しか台帳に残らない。
    occurrences: dict[str, dict] = {}
    pattern = re.compile(
        r'<div class="source">URL：https://cyberjapandata\.gsi\.go\.jp/xyz/'
        r'([A-Za-z0-9_\-]+)/\{z\}/\{x\}/\{y\}\.(\w+)\s*(（[^）]*）)?'
    )
    for match in pattern.finditer(text):
        data_id, extension, note = match.group(1), match.group(2), match.group(3) or ""
        title = _latest_before(titles, match.start())
        section = _latest_before(sections, match.start()).lstrip("■ ").strip()
        table = _gsi_table_after(text, match.end())
        entry = occurrences.setdefault(
            data_id,
            {"title": f"{title}{note}", "ext": extension, "sections": [], "zooms": [], "areas": []},
        )
        found = [("sections", [section])] + [
            ("zooms", table.get("ズームレベル", [])),
            ("areas", table.get("提供範囲", [])),
        ]
        for key, items in found:
            for value in items:
                if value and value not in entry[key]:
                    entry[key].append(value)

    values: list[dict] = []
    for data_id, entry in occurrences.items():
        parts = [entry["title"], f".{entry['ext']}", "／".join(entry["sections"])]
        if entry["zooms"]:
            parts.append("ZL " + "／".join(entry["zooms"]))
        if entry["areas"]:
            parts.append("／".join(entry["areas"]))
        values.append({"value": data_id, "meaning": "｜".join(p for p in parts if p)})
    return values


def _latest_before(items: list[tuple[int, str]], position: int) -> str:
    """位置より前にある最後の見出しを返す。ページ上の所属を決めるのに使う。"""
    found = ""
    for start, label in items:
        if start > position:
            break
        found = label
    return found


def _gsi_table_after(text: str, position: int) -> dict[str, list[str]]:
    """URL の直後に続く表を、次の見出し・次の URL の手前まで全部読む。

    1 つの URL に表が 1 つとは限らない。標準地図はズームレベルの帯ごとに
    データソースも提供範囲も違い、表がその数だけ並ぶ。最初の 1 つで打ち切ると
    「標準地図は ZL18 だけ」という嘘になる。
    """
    # 区切りは次の URL ではなく次の見出しにする。指定緊急避難場所のように URL が
    # 8 本並んでその後ろに表が 1 つ、という書き方があり、URL で切ると表を落とす。
    next_heading = text.find("<h4", position)
    limit = next_heading if next_heading != -1 else len(text)

    rows: dict[str, list[str]] = {}
    cursor = position
    while True:
        start = text.find("<table", cursor)
        if start == -1 or start >= limit:
            break
        end = text.find("</table>", start)
        if end == -1:
            break
        for row in re.findall(r"<tr>(.*?)</tr>", text[start:end], re.S):
            cells = [_clean(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
            if len(cells) >= 2 and cells[0] in ("ズームレベル", "提供範囲", "提供開始"):
                value = cells[1][:80]
                if value and value not in rows.setdefault(cells[0], []):
                    rows[cells[0]].append(value)
        cursor = end + 1

    if rows:
        return rows
    # 見出しの下に表が無いことがある。指定緊急避難場所（skhb01〜08）がそれで、
    # 次の見出し「指定避難所」の後ろにある表がデータソース欄に
    # 「指定緊急避難場所・指定避難所」と書いており、両方を指している。
    # 何も返さないと提供ズームレベルが落ちるので、直後の表まで見にいく。
    # skhb01 は実際に ZL10 で 200 を返すことを検証で確かめている。
    start = text.find("<table", position)
    end = text.find("</table>", start) if start != -1 else -1
    if start == -1 or end == -1:
        return rows
    for row in re.findall(r"<tr>(.*?)</tr>", text[start:end], re.S):
        cells = [_clean(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(cells) >= 2 and cells[0] in ("ズームレベル", "提供範囲", "提供開始"):
            value = cells[1][:80]
            if value:
                rows.setdefault(cells[0], []).append(value)
    return rows


def _gsi_url_parameters(html_text: str) -> list[dict]:
    """仕様ページの「{t}：データID」の並びを、そのまま項目にする。"""
    text = _clean(html_text)
    fields = []
    for name, meaning in re.findall(r"\{(\w+)\}：([^{]+?)(?=\s*\{|\s*例えば|$)", text):
        fields.append(
            {
                "name": "{" + name + "}",
                "type": "パス要素",
                "description": meaning.strip(),
                "example": "",
            }
        )
    return fields


def _gsi_dem_text_fields(html_text: str) -> list[dict]:
    """標高タイル（テキスト形式）の仕様を、セル単位の項目として並べる。"""
    text = _clean(html_text)
    return [
        {
            "name": "標高値",
            "type": "数値（m）",
            "description": _gsi_sentence(text, "標高データは小数点第二位まで"),
            "example": "20.71",
        },
        {
            "name": "e",
            "type": "文字",
            "description": _gsi_sentence(text, "標高値が存在しない画素"),
            "example": "e",
        },
        {
            "name": "行・列",
            "type": "構造",
            "description": _gsi_sentence(text, "数値データは対応する地図タイル"),
            "example": "256 行 × 256 列",
        },
    ]


def _gsi_dem_png_fields(html_text: str) -> list[dict]:
    """標高タイル（PNG 形式）の仕様を、画素単位の項目として並べる。"""
    text = _clean(html_text)
    return [
        {
            "name": "R, G, B",
            "type": "画素値（0〜255）",
            "description": _gsi_sentence(text, "ピクセルの画素値（RGB値）から"),
            "example": "",
        },
        {
            "name": "(R, G, B) = (128, 0, 0)",
            "type": "画素値",
            "description": _gsi_sentence(text, "無効値"),
            "example": "",
        },
    ]


def _gsi_sentence(text: str, needle: str) -> str:
    """1 行に均した本文から、目印を含む一文だけを取り出す。"""
    position = text.find(needle)
    if position == -1:
        return ""
    start = max(text.rfind("。", 0, position) + 1, 0)
    end = text.find("。", position)
    return text[start : end + 1 if end != -1 else None].strip()


async def _gsi_geojson_object(
    client: httpx.AsyncClient, data_id: str, zoom: int, label: str
) -> dict:
    """GeoJSON タイルを 1 枚読み、現れた属性をすべて列挙する。

    属性はフィーチャによって異なるため、先頭 1 件ではなく全件を通す。
    """
    x, y = _gsi_tile_xy(GSI_SAMPLE_LAT, GSI_SAMPLE_LON, zoom)
    response = await client.get(f"{GSI_TILE_BASE}/{data_id}/{zoom}/{x}/{y}.geojson")
    response.raise_for_status()
    features = json.loads(response.text).get("features", [])
    collected: dict[str, set[str]] = {}
    for feature in features:
        _collect(feature.get("properties", {}), collected)
    examples: dict[str, str] = {}
    for feature in features:
        for key, value in feature.get("properties", {}).items():
            if key not in examples and value not in ("", " ", None):
                examples[key] = _clean(str(value))[:60]
    return {
        "name": f"GeoJSON タイル: {label}（`{data_id}` ZL{zoom}）",
        "description": (
            f"タイル {zoom}/{x}/{y} の {len(features)} 件を通して現れた属性。"
            "定義書は公開されておらず、説明は空欄になる。"
        ),
        "fields": [
            {
                "name": key,
                "type": "/".join(sorted(types)),
                "description": "",
                "example": examples.get(key, ""),
            }
            for key, types in collected.items()
        ],
    }


def _gsi_lore_documented(html_text: str) -> dict:
    """一覧ページの備考が列挙している「公開している情報」を項目として拾う。

    GeoJSON のキーとの対応はページに書かれていないため、突き合わせはしない。
    """
    text = unescape(html_text)
    # ページ全体を対象にすると「・一等三角点：8〜11」のような別の表まで拾ってしまう。
    # 自然災害伝承碑の備考の中だけを見る。
    start = text.find("【公開している情報】")
    end = text.find("【ご利用上の注意】", start) if start != -1 else -1
    if start == -1 or end == -1:
        return {
            "name": "自然災害伝承碑として公開している情報（一覧ページの記載）",
            "description": "一覧ページに該当する記載が見つからなかった。",
            "fields": [],
        }
    text = text[start:end]
    fields = []
    for name, meaning in re.findall(r"・([^\s：]+)\s*：([^<・]+)", text):
        description = _clean(meaning)
        if description and not any(f["name"] == name for f in fields):
            fields.append(
                {"name": name, "type": "記載", "description": description, "example": ""}
            )
    return {
        "name": "自然災害伝承碑として公開している情報（一覧ページの記載）",
        "description": (
            "一覧ページの備考が日本語の名前で列挙しているもの。"
            "上の GeoJSON の属性名との対応は一次資料に書かれていないので、突き合わせていない。"
        ),
        "fields": fields,
    }


def _gsi_lore_disaster_kinds(html_text: str) -> list[str]:
    """備考が括弧で列挙している災害種別を取り出す。"""
    text = _clean(html_text)
    match = re.search(r"災害種別\s*：[^（]*（([^）]+)）", text)
    if not match:
        return []
    return [kind.strip() for kind in match.group(1).split("、") if kind.strip()]


def _gsi_tile_xy(lat: float, lon: float, zoom: int) -> tuple[int, int]:
    """緯度経度からタイル座標を求める（仕様ページのメルカトル投影の定義に従う）。"""
    n = 2**zoom
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n)
    return x, y


async def extract_estat_lod_fields(client: httpx.AsyncClient) -> dict:
    """統計 LOD: SPARQL の応答構造と、語彙として定義されている述語を列挙する。

    RDF は固定のスキーマを持たないため「項目」は述語のこと。どんな述語が
    使われているかが分からないとクエリが書けないので、実データから拾う。
    """
    objects = []

    # 応答そのものの構造（SPARQL Results JSON）。
    response = await client.get(
        ESTAT_LOD_ENDPOINT,
        params={"query": "select ?s ?p ?o where { ?s ?p ?o } limit 1"},
        headers={"Accept": "application/sparql-results+json"},
    )
    response.raise_for_status()
    payload = response.json()
    binding = ((payload.get("results") or {}).get("bindings") or [{}])[0]
    objects.append(
        {
            "name": "SPARQL Results JSON（応答の器）",
            "description": "SELECT / ASK の応答形式。head.vars に変数名、results.bindings に行が入る。",
            "fields": [
                {"name": "head.vars", "type": "string[]", "description": "クエリで指定した変数名の一覧", "example": ""},
                {"name": "results.bindings[]", "type": "object[]", "description": "1 行分。変数名をキーに値が入る", "example": ""},
                *[
                    {
                        "name": f"results.bindings[].<変数>.{k}",
                        "type": "string",
                        "description": {"type": "リテラルか URI かの別", "value": "値そのもの", "datatype": "リテラルの型 URI"}.get(k, ""),
                        "example": str(v)[:60],
                    }
                    for k, v in (next(iter(binding.values()), {}) or {}).items()
                ],
            ],
        }
    )

    # 実データに現れる述語。語彙が分からないとクエリが書けない。
    # グラフ全体に distinct を掛けると返らず、無作為に limit を掛けても同じ述語ばかり
    # 返る。統計値 1 件を選び、その主語が持つ述語を引くのが最も実用に近い。
    subject = await _estat_lod_observation(client)
    predicates: list[str] = []
    if subject:
        response = await client.get(
            ESTAT_LOD_ENDPOINT,
            params={"query": f"select ?p where {{ <{subject}> ?p ?o }} limit 100"},
            headers={"Accept": "application/sparql-results+json"},
            timeout=90.0,
        )
        response.raise_for_status()
        seen: dict[str, None] = {}
        for b in (response.json().get("results") or {}).get("bindings", []):
            value = _binding(b, "p")
            if value:
                seen.setdefault(value, None)
        predicates = list(seen)
    objects.append(
        {
            "name": "統計値 1 件が持つ述語",
            "description": "RDF に固定スキーマは無いため、項目にあたるのは述語。観測値 1 件を例に、実際に使われている述語を並べる。",
            "fields": [
                {"name": p.rsplit("/", 1)[-1] or p, "type": "述語", "description": p, "example": ""}
                for p in predicates
            ],
        }
    )

    return {
        "origin": "observed",
        "origin_detail": (
            "SPARQL の応答構造と、実データに現れる述語を実測で列挙。RDF は固定スキーマを"
            "持たないため、ここに出るのは観測できた述語であって語彙の全量ではない"
        ),
        "source_url": "https://data.e-stat.go.jp/lodw/sparqlendpoint/api",
        "objects": objects,
        "enums": [],
    }


def _binding(row: dict, name: str) -> str | None:
    """SPARQL の応答は変数名を大文字化して返す（?p のキーは "P"）。大小を問わず引く。"""
    value = next((v for k, v in row.items() if k.lower() == name.lower()), None)
    return value["value"] if value else None


async def _estat_lod_observation(client: httpx.AsyncClient) -> str | None:
    """述語を調べる足場として、統計値を 1 件選ぶ。"""
    measure = "<http://data.e-stat.go.jp/lod/ontology/measure/index>"
    response = await client.get(
        ESTAT_LOD_ENDPOINT,
        params={"query": f"select ?s where {{ ?s {measure} ?v }} limit 1"},
        headers={"Accept": "application/sparql-results+json"},
        timeout=90.0,
    )
    response.raise_for_status()
    rows = (response.json().get("results") or {}).get("bindings") or []
    return _binding(rows[0], "s") if rows else None


async def extract_all(jgrants_url: str | None) -> dict:
    sources: dict[str, Any] = {}
    async with httpx.AsyncClient(timeout=120.0, trust_env=True) as client:
        for source_id, extractor in [
            ("egov-hourei-api", extract_law_fields),
            ("egov-data-catalog", extract_ckan_fields),
            ("jma-xml", extract_jma_fields),
            ("ndl-search", extract_ndl_fields),
            ("estat-lod", extract_estat_lod_fields),
            ("gsi-tiles", extract_gsi_tiles_fields),
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
