#!/usr/bin/env python3
"""地理院タイル（国土地理院 XYZ タイル配信）の接続・利用検証。

配信は 1 種類のパス規則 https://cyberjapandata.gsi.go.jp/xyz/{t}/{z}/{x}/{y}.{ext}
に統一されているが、{ext} によって中身の性質がまったく違う。ここでは 4 系統を
すべて叩く。

    png / jpg  地図タイル（画像）
    txt        標高タイル（カンマ区切りの標高値）
    geojson    点データのタイル（避難場所、自然災害伝承碑など）

認証情報は不要。一次資料にレート制限の記述は無いが、それは「制限が無い」ことの
根拠にならないので、この検証は逐次・少数のリクエストに留める。

    python verify/verify_gsi_tiles.py --out results/gsi-tiles.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import re
import struct
import sys
import zlib
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _report import Reporter  # noqa: E402

SOURCE_ID = "gsi-tiles"
TILE_BASE = "https://cyberjapandata.gsi.go.jp/xyz"
DOC_BASE = "https://maps.gsi.go.jp/development"
# 国土地理院コンテンツ利用規約。一覧ページが利用条件の根拠として指している。
TERMS_URL = "https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html"

# 一次資料が「原則として」と書いている URL 命名規則。この文字列が仕様ページから
# 消えたら、規則そのものが変わったということ。
URL_TEMPLATE = "https://cyberjapandata.gsi.go.jp/xyz/{t}/{z}/{x}/{y}.{ext}"
# タイル座標の基準にする地点。タイル座標を直接ハードコードすると、どの場所を
# 見ているのかが読めなくなるので、緯度経度から毎回計算する。
SAMPLE_LAT, SAMPLE_LON = 35.6812, 139.7671  # 東京駅

REQUEST_INTERVAL = 1.0
# PNG 標高タイルの無効値。一次資料が (R, G, B) = (128, 0, 0) と明記している。
DEM_PNG_NODATA = (128, 0, 0)
DEM_RESOLUTION = 0.01  # 一次資料が標高分解能 u = 0.01m と明記している
TILE_PIXELS = 256


def tile_xy(lat: float, lon: float, zoom: int) -> tuple[int, int]:
    """緯度経度からタイル座標を求める（仕様ページのメルカトル投影の定義に従う）。"""
    n = 2**zoom
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n)
    return x, y


async def verify(tile_base: str) -> Reporter:
    reporter = Reporter(SOURCE_ID, tile_base)

    async with httpx.AsyncClient(timeout=90.0, trust_env=True, follow_redirects=True) as client:
        steps = [
            ("一次資料: 地理院タイル一覧", _tile_index(client)),
            ("一次資料: 地理院タイルの仕様", _tile_spec(client)),
            ("一次資料: 標高タイルの詳細仕様", _dem_spec(client)),
            ("地図タイル: 標準地図 std（ZL14 PNG）", _map_tile(client, tile_base, "std", 14, "png")),
            ("地図タイル: 淡色地図 pale（ZL14 PNG）", _map_tile(client, tile_base, "pale", 14, "png")),
            (
                "地図タイル: 全国最新写真 seamlessphoto（ZL14 JPEG）",
                _map_tile(client, tile_base, "seamlessphoto", 14, "jpg"),
            ),
            ("標高タイル: DEM5A テキスト形式（ZL14）", _dem_text(client, tile_base)),
            ("標高タイル: DEM5A PNG 形式とテキスト形式の突合（ZL14）", _dem_png(client, tile_base)),
            (
                "GeoJSON タイル: 指定緊急避難場所 skhb01（ZL10）",
                _geojson_tile(client, tile_base, "skhb01", 10),
            ),
            (
                "GeoJSON タイル: 自然災害伝承碑 disaster_lore_all（ZL7）",
                _geojson_tile(client, tile_base, "disaster_lore_all", 7),
            ),
            ("提供範囲外・存在しないデータ ID の返り方", _absent(client, tile_base)),
            ("文書化されたズームレベルの外側の返り方", _zoom_edges(client, tile_base)),
            ("CORS: Origin 付きリクエスト", _cors(client, tile_base)),
            ("条件付きリクエスト（ETag / Last-Modified）", _conditional(client, tile_base)),
        ]
        for index, (name, coro) in enumerate(steps):
            if index:
                await asyncio.sleep(REQUEST_INTERVAL)
            await reporter.step(name, coro)

        # 利用規約の本文があるホストは、この環境の egress で塞がれている。
        # 先方の障害ではないので failed とは分けて記録する。
        await _terms(client, reporter)

    return reporter


async def _terms(client: httpx.AsyncClient, reporter: Reporter) -> None:
    name = "利用規約: 国土地理院コンテンツ利用規約"
    try:
        response = await client.get(TERMS_URL)
    except httpx.ProxyError as exc:
        reporter.blocked(name, f"自環境の egress でプロキシが拒否した: {exc}")
        return
    await reporter.step(name, _terms_digest(response))


async def _terms_digest(response: httpx.Response) -> dict:
    response.raise_for_status()
    return {"status": response.status_code, "url": str(response.url), "bytes": len(response.content)}


async def _tile_index(client: httpx.AsyncClient) -> dict:
    """一覧ページ。配信されているタイルの種類はここにしか列挙されていない。"""
    response = await client.get(f"{DOC_BASE}/ichiran.html")
    response.raise_for_status()
    text = response.text
    # 一覧に載っている URL テンプレートを数える。ここが唯一の「何が配信されているか」。
    pairs = set(
        re.findall(
            r"cyberjapandata\.gsi\.go\.jp/xyz/([A-Za-z0-9_\-]+)/\{z\}/\{x\}/\{y\}\.(\w+)", text
        )
    )
    extensions: dict[str, int] = {}
    for _, ext in pairs:
        extensions[ext] = extensions.get(ext, 0) + 1
    # 利用条件は 3 分類ごとに違う。見出しが消えたら分類が変わったということ。
    categories = [
        c
        for c in ("基本測量成果", "基本測量成果以外で出典の記載のみで利用可能なもの", "上記以外のもの")
        if c in text
    ]
    return {
        "status": response.status_code,
        "url_templates": len(pairs),
        "extensions": dict(sorted(extensions.items())),
        "categories_found": categories,
        # 出典表示の条件。台帳の usage_restrictions の根拠になる一文。
        "attribution_documented": "出典の明示のみで申請不要" in text,
        "text_dem_frozen_documented": "テキスト形式の標高タイルは令和6年10月より更新を停止" in text,
    }


async def _tile_spec(client: httpx.AsyncClient) -> dict:
    """仕様ページ。URL 命名規則と投影法・タイル座標の定義がある。"""
    response = await client.get(f"{DOC_BASE}/siyou.html")
    response.raise_for_status()
    text = response.text
    return {
        "status": response.status_code,
        "url_template_documented": URL_TEMPLATE in text,
        "tile_pixels_documented": "256ピクセル×256ピクセル" in text,
        "datum_documented": "世界測地系（JGD2011）" in text,
        "mercator_cutoff_documented": "85.0511" in text,
    }


async def _dem_spec(client: httpx.AsyncClient) -> dict:
    """標高タイルの詳細仕様。テキスト形式と PNG 形式の対応関係が書かれている。"""
    response = await client.get(f"{DOC_BASE}/demtile.html")
    response.raise_for_status()
    text = response.text
    return {
        "status": response.status_code,
        "nodata_text_documented": "標高値が存在しない画素には「e」の文字が格納されている" in text,
        "nodata_png_documented": "(R, G, B)=(128, 0, 0)" in text,
        "resolution_documented": "0.01m" in text,
        # この主張が実測と食い違う。突合ステップの評価基準になる。
        "png_equals_text_documented": "テキスト形式の標高タイルの標高値と同じになります" in text,
    }


async def _map_tile(
    client: httpx.AsyncClient, base: str, data_id: str, zoom: int, ext: str
) -> dict:
    """画像タイル 1 枚。中身の画素までは見ず、形式と大きさが仕様どおりかを見る。"""
    x, y = tile_xy(SAMPLE_LAT, SAMPLE_LON, zoom)
    response = await client.get(f"{base}/{data_id}/{zoom}/{x}/{y}.{ext}")
    response.raise_for_status()
    body = response.content
    digest = {
        "tile": f"{zoom}/{x}/{y}",
        "status": response.status_code,
        "content_type": response.headers.get("content-type"),
        "bytes": len(body),
        "last_modified": response.headers.get("last-modified"),
    }
    if body[:8] == b"\x89PNG\r\n\x1a\n":
        width, height, depth, color_type = struct.unpack(">IIBB", body[16:26])
        digest["png"] = {
            "width": width,
            "height": height,
            "bit_depth": depth,
            "color_type": color_type,
        }
    elif body[:2] == b"\xff\xd8":
        digest["jpeg"] = {"soi": True, "size": _jpeg_size(body)}
    return digest


def _jpeg_size(body: bytes) -> list[int] | None:
    """JPEG の SOF マーカーから縦横を読む。仕様どおり 256x256 かを見るため。"""
    pos = 2
    while pos + 9 < len(body):
        if body[pos] != 0xFF:
            pos += 1
            continue
        marker = body[pos + 1]
        length = struct.unpack(">H", body[pos + 2 : pos + 4])[0]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height, width = struct.unpack(">HH", body[pos + 5 : pos + 9])
            return [width, height]
        pos += 2 + length
    return None


async def _dem_text(client: httpx.AsyncClient, base: str) -> dict:
    """テキスト形式の標高タイル。256 行 × 256 列であることと無効値の出方を見る。"""
    x, y = tile_xy(SAMPLE_LAT, SAMPLE_LON, 14)
    response = await client.get(f"{base}/dem5a/14/{x}/{y}.txt")
    response.raise_for_status()
    rows = response.text.strip().split("\n")
    widths = {len(row.split(",")) for row in rows}
    nodata = sum(row.split(",").count("e") for row in rows)
    return {
        "tile": f"14/{x}/{y}",
        "status": response.status_code,
        # .txt なのに content-type は text/plain。geojson との違いを残しておく。
        "content_type": response.headers.get("content-type"),
        "rows": len(rows),
        "columns": sorted(widths),
        "nodata_cells": nodata,
        "corner_values": {
            "top_left": rows[0].split(",")[0],
            "top_right": rows[0].split(",")[-1],
            "bottom_left": rows[-1].split(",")[0],
            "bottom_right": rows[-1].split(",")[-1],
        },
    }


async def _dem_png(client: httpx.AsyncClient, base: str) -> dict:
    """PNG 形式の標高タイルを復号し、同じタイルのテキスト形式と 1 画素ずつ突き合わせる。

    一次資料は「画素値から算出される標高値は、テキスト形式の標高値と同じになる」と
    書いている。同じかどうかは実際に比べないと分からないので、比べる。
    """
    x, y = tile_xy(SAMPLE_LAT, SAMPLE_LON, 14)
    png = await client.get(f"{base}/dem5a_png/14/{x}/{y}.png")
    png.raise_for_status()
    header, pixels = _decode_rgb_png(png.content)

    text = await client.get(f"{base}/dem5a/14/{x}/{y}.txt")
    text.raise_for_status()
    rows = text.text.strip().split("\n")

    width = header["width"]
    same = differ = 0
    max_gap = 0.0
    nodata_png = nodata_text = 0
    for row_index in range(min(header["height"], len(rows))):
        cells = rows[row_index].split(",")
        for col_index in range(min(width, len(cells))):
            offset = (row_index * width + col_index) * 3
            rgb = (pixels[offset], pixels[offset + 1], pixels[offset + 2])
            if rgb == DEM_PNG_NODATA:
                from_png = None
                nodata_png += 1
            else:
                value = (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]
                if value >= 2**23:
                    value -= 2**24
                from_png = round(value * DEM_RESOLUTION, 2)
            cell = cells[col_index]
            from_text = None if cell == "e" else float(cell)
            if from_text is None:
                nodata_text += 1
            if from_png == from_text:
                same += 1
            else:
                differ += 1
                if from_png is not None and from_text is not None:
                    max_gap = max(max_gap, abs(from_png - from_text))
    return {
        "tile": f"14/{x}/{y}",
        "png_header": header,
        "pixels_compared": same + differ,
        "pixels_identical": same,
        "pixels_differing": differ,
        "max_difference_m": round(max_gap, 2),
        "nodata_pixels_png": nodata_png,
        "nodata_cells_text": nodata_text,
    }


def _decode_rgb_png(body: bytes) -> tuple[dict, bytearray]:
    """24 ビットカラー PNG を復号する。標高値を取り出すため画素まで必要になる。

    標高タイルは色ではなく数値なので、画像ライブラリ抜きでも読める形にしてある。
    色種別が 2（トゥルーカラー）でないものは、標高タイルではないので受け付けない。
    """
    if body[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("PNG シグネチャが一致しない")
    position = 8
    idat = b""
    header: dict = {}
    while position < len(body):
        length, kind = struct.unpack(">I4s", body[position : position + 8])
        chunk = body[position + 8 : position + 8 + length]
        position += 12 + length
        if kind == b"IHDR":
            width, height, depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", chunk)
            header = {
                "width": width,
                "height": height,
                "bit_depth": depth,
                "color_type": color_type,
                "interlace": interlace,
            }
        elif kind == b"IDAT":
            idat += chunk
        elif kind == b"IEND":
            break
    if header.get("color_type") != 2 or header.get("bit_depth") != 8 or header.get("interlace"):
        raise ValueError(f"想定外の PNG 形式: {header}")

    raw = zlib.decompress(idat)
    stride = header["width"] * 3
    out = bytearray()
    previous = bytearray(stride)
    cursor = 0
    for _ in range(header["height"]):
        filter_type = raw[cursor]
        cursor += 1
        line = bytearray(raw[cursor : cursor + stride])
        cursor += stride
        _unfilter(filter_type, line, previous, stride)
        out += line
        previous = line
    return header, out


def _unfilter(filter_type: int, line: bytearray, previous: bytearray, stride: int) -> None:
    """PNG のフィルタを解除する（RFC 2083 の Sub / Up / Average / Paeth）。"""
    bpp = 3
    if filter_type == 0:
        return
    if filter_type == 1:
        for i in range(bpp, stride):
            line[i] = (line[i] + line[i - bpp]) & 0xFF
    elif filter_type == 2:
        for i in range(stride):
            line[i] = (line[i] + previous[i]) & 0xFF
    elif filter_type == 3:
        for i in range(stride):
            left = line[i - bpp] if i >= bpp else 0
            line[i] = (line[i] + ((left + previous[i]) >> 1)) & 0xFF
    elif filter_type == 4:
        for i in range(stride):
            left = line[i - bpp] if i >= bpp else 0
            up = previous[i]
            upper_left = previous[i - bpp] if i >= bpp else 0
            pa = abs(up - upper_left)
            pb = abs(left - upper_left)
            pc = abs(left + up - 2 * upper_left)
            if pa <= pb and pa <= pc:
                predictor = left
            elif pb <= pc:
                predictor = up
            else:
                predictor = upper_left
            line[i] = (line[i] + predictor) & 0xFF
    else:
        raise ValueError(f"未知のフィルタ種別: {filter_type}")


async def _geojson_tile(client: httpx.AsyncClient, base: str, data_id: str, zoom: int) -> dict:
    """点データのタイル。項目名は仕様書ではなく、返ってきた実データにしかない。"""
    x, y = tile_xy(SAMPLE_LAT, SAMPLE_LON, zoom)
    response = await client.get(f"{base}/{data_id}/{zoom}/{x}/{y}.geojson")
    response.raise_for_status()
    document = json.loads(response.text)
    features = document.get("features", [])
    keys: list[str] = []
    for feature in features:
        for key in feature.get("properties", {}):
            if key not in keys:
                keys.append(key)
    geometry_types = sorted({f.get("geometry", {}).get("type") for f in features if f.get("geometry")})
    return {
        "tile": f"{zoom}/{x}/{y}",
        "status": response.status_code,
        # .geojson でも application/json ではない。判定に使えないので記録する。
        "content_type": response.headers.get("content-type"),
        "type": document.get("type"),
        "features": len(features),
        "geometry_types": geometry_types,
        "property_keys": keys,
        "sample_properties": features[0].get("properties") if features else None,
    }


async def _absent(client: httpx.AsyncClient, base: str) -> dict:
    """無いものを要求したときの返り方。配信の実体が何かもここに出る。"""
    x, y = tile_xy(SAMPLE_LAT, SAMPLE_LON, 14)
    cases = {
        # 提供範囲（日本とその周辺）の外にあるタイル座標
        "提供範囲外の座標 std/14/0/0": f"{base}/std/14/0/0.png",
        # 存在しないデータ ID
        "存在しないデータ ID": f"{base}/no_such_tileset/14/{x}/{y}.png",
        # 存在するデータ ID だが、提供していない拡張子
        "提供していない拡張子 std .geojson": f"{base}/std/14/{x}/{y}.geojson",
    }
    observed = {}
    for label, url in cases.items():
        response = await client.get(url)
        body = response.text[:400]
        code = re.search(r"<Code>([^<]+)</Code>", body)
        observed[label] = {
            "status": response.status_code,
            "content_type": response.headers.get("content-type"),
            "error_code": code.group(1) if code else None,
        }
        await asyncio.sleep(REQUEST_INTERVAL)
    return observed


async def _zoom_edges(client: httpx.AsyncClient, base: str) -> dict:
    """一覧ページが書いているズームレベル範囲の外側を叩く。

    std は「ZL2〜8」と「ZL5〜18」の 2 区分でしか書かれていない。その外側が
    どうなるかは書かれていないので、書かれていないことを実測で埋める。
    """
    observed = {}
    for zoom in (0, 1, 19):
        x, y = tile_xy(SAMPLE_LAT, SAMPLE_LON, zoom)
        response = await client.get(f"{base}/std/{zoom}/{x}/{y}.png")
        observed[f"std ZL{zoom}"] = {
            "tile": f"{zoom}/{x}/{y}",
            "status": response.status_code,
            "content_type": response.headers.get("content-type"),
            "bytes": len(response.content),
        }
        await asyncio.sleep(REQUEST_INTERVAL)
    return observed


async def _cors(client: httpx.AsyncClient, base: str) -> dict:
    """一次資料が想定する使い方はブラウザからの読み込み。CORS が要る。"""
    x, y = tile_xy(SAMPLE_LAT, SAMPLE_LON, 14)
    url = f"{base}/std/14/{x}/{y}.png"
    without = await client.get(url)
    await asyncio.sleep(REQUEST_INTERVAL)
    with_origin = await client.get(url, headers={"Origin": "https://example.com"})
    return {
        "without_origin_header": {
            "status": without.status_code,
            "access_control_allow_origin": without.headers.get("access-control-allow-origin"),
        },
        "with_origin_header": {
            "status": with_origin.status_code,
            "access_control_allow_origin": with_origin.headers.get("access-control-allow-origin"),
        },
    }


async def _conditional(client: httpx.AsyncClient, base: str) -> dict:
    """タイルは枚数が多い。再取得を避けられるかは実用上の分かれ目になる。"""
    x, y = tile_xy(SAMPLE_LAT, SAMPLE_LON, 14)
    url = f"{base}/std/14/{x}/{y}.png"
    first = await client.get(url)
    first.raise_for_status()
    etag = first.headers.get("etag")
    last_modified = first.headers.get("last-modified")

    await asyncio.sleep(REQUEST_INTERVAL)
    by_etag = await client.get(url, headers={"If-None-Match": etag}) if etag else None
    await asyncio.sleep(REQUEST_INTERVAL)
    by_date = (
        await client.get(url, headers={"If-Modified-Since": last_modified})
        if last_modified
        else None
    )
    return {
        "etag_present": bool(etag),
        "last_modified_present": bool(last_modified),
        "if_none_match_status": by_etag.status_code if by_etag else None,
        "if_modified_since_status": by_date.status_code if by_date else None,
        "server": first.headers.get("server"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=TILE_BASE)
    parser.add_argument("--out", default=f"results/{SOURCE_ID}.json")
    args = parser.parse_args()

    reporter = asyncio.run(verify(args.base_url))
    reporter.write(args.out)
    return reporter.print_console(args.out)


if __name__ == "__main__":
    raise SystemExit(main())
