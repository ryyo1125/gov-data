# 検証ログ: Jグランツ公式MCPサーバー（医療系）

- 検証日: 2026-08-19
- 対象: [digital-go-jp/jgrants-mcp-server](https://github.com/digital-go-jp/jgrants-mcp-server)（デジタル庁公式 / MIT）
- 実行環境: Claude Code リモートコンテナ（Python 3.11.15 / fastmcp 3.4.7）

## 結論（先に）

**MCP接続層は成功、データ取得は失敗。** 原因は Jグランツ側でもサーバー実装でもなく、
本実行環境の egress ポリシーが `api.jgrants-portal.go.jp` を遮断しているため。

## 実施手順（再現可能）

```
git clone --depth 1 https://github.com/digital-go-jp/jgrants-mcp-server.git
cd jgrants-mcp-server && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
JGRANTS_FILES_DIR=./tmp ./venv/bin/python -m jgrants_mcp_server.core --host 127.0.0.1 --port 8000
./venv/bin/python ../scripts/probe_jgrants_mcp.py   # 本リポジトリの scripts/ に配置
```

## 結果

### 成功したもの

`tools/list` — 公開ツール5件と引数スキーマを実測で確認:

| ツール | 引数 | 必須 |
|---|---|---|
| `search_subsidies` | keyword, use_purpose, industry, target_number_of_employees, target_area_search, sort, order, acceptance | keyword |
| `get_subsidy_detail` | subsidy_id | subsidy_id |
| `get_subsidy_overview` | output_format | — |
| `get_file_content` | subsidy_id, filename, return_format | subsidy_id, filename |
| `ping` | — | — |

`resources/list` — `jgrants://guidelines`（usage_guidelines）1件。

`ping` — 正常応答:
```json
{"status": "ok", "server": "jGrants MCP Server", "version": "2.0.0", "timestamp": "2026-08-19T03:04:22.010068+00:00"}
```

### 失敗したもの

`search_subsidies(keyword="医療", industry="医療、福祉", sort="created_date", order="DESC", acceptance=1)`:
```json
{"error": "エラーが発生しました: 403 Forbidden"}
```

この 403 は Jグランツ API からではなく **egress プロキシの CONNECT 拒否**。プロキシ側ログで確認済み:

```
{"kind": "connect_rejected",
 "detail": "gateway answered 403 to CONNECT (policy denial or upstream failure)",
 "host": "api.jgrants-portal.go.jp:443"}
```

同様にブロックされたホスト: `www.jgrants-portal.go.jp`、`developers.digital.go.jp`。

### 解除に必要なこと

このセッションの環境（Claude Code on the web の environment 設定）のネットワークポリシーで、
以下を許可リストに追加する。参照: https://code.claude.com/docs/en/claude-code-on-the-web

- `api.jgrants-portal.go.jp` — API本体（必須）
- `www.jgrants-portal.go.jp` — 公募ページの人間向けURL確認（任意）
- `developers.digital.go.jp` — API公式ドキュメント（任意）

## 副次的に判明した運用上の注意

依存パッケージ `markitdown` が `mobile.events.data.microsoft.com` へテレメトリ送信を試行していた
（プロキシログで CONNECT 拒否として観測）。添付ファイルのMarkdown変換を使う場合、
Microsoft へのテレメトリ経路が発生する点は、行政データを扱う運用として把握しておく。
