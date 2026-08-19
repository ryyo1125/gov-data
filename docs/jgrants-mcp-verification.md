# デジタル庁 Jグランツ MCP Server 接続・利用検証レポート

- **検証日**: 2026-08-19（UTC）
- **対象**: [digital-go-jp/jgrants-mcp-server](https://github.com/digital-go-jp/jgrants-mcp-server)
  — デジタル庁が公開する、補助金電子申請システム「Jグランツ」公開 API の MCP ラッパー
- **バックエンド API**: `https://api.jgrants-portal.go.jp/exp/v1/public`
  （[公式ドキュメント](https://developers.digital.go.jp/documents/jgrants/api/)）
- **結果**: 接続・ツール実行ともに成功（9 ステップ中 9 成功、失敗 0）

## 検証環境

| 項目 | 値 |
|---|---|
| Python | 3.11.15 |
| パッケージ管理 | uv |
| MCP フレームワーク | FastMCP 3.4.7（`requirements.txt` は `fastmcp>=2.12.4`） |
| トランスポート | Streamable-HTTP（`http://127.0.0.1:8000/mcp`） |
| MCP プロトコル | `2025-11-25` |
| ネットワーク | 送信 HTTPS はエージェントプロキシ経由 |

## 実施手順

```bash
./verify/run_jgrants_verification.sh
```

このスクリプトが、リポジトリの clone → `uv venv` + 依存インストール → サーバー起動 →
`verify/verify_jgrants_mcp.py` による検証 → `results/jgrants-verification.json` への
結果書き出しまでを一括で行う。

## 検証結果

| # | ステップ | 結果 | 所要 | 備考 |
|---|---|---|---|---|
| 1 | `initialize` | OK | — | `serverInfo` = `jgrants-mcp-server` / protocol `2025-11-25` |
| 2 | `tools/list` | OK | 15 ms | 5 ツール |
| 3 | `resources/list` | OK | 9 ms | `jgrants://guidelines` |
| 4 | `prompts/list` | OK | 5 ms | `subsidy_search_guide`, `api_usage_agreement` |
| 5 | `ping` | OK | 10 ms | `{"status":"ok","version":"2.0.0"}` |
| 6 | `search_subsidies` | OK | 1.5 s | キーワード「IT導入」で 4 件 |
| 7 | `get_subsidy_detail` | OK | 231 ms | 実データ（都道府県事業の詳細 HTML）を取得 |
| 8 | `get_subsidy_overview` | OK | 1.8 s | 全 189 件を締切期間別・金額規模別に集計 |
| 9 | `get_file_content` | OK | 1.7 s | 添付 PDF を Markdown 変換して取得（27,560 文字） |

### 公開ツール

| ツール | 引数 | 用途 |
|---|---|---|
| `search_subsidies` | `keyword`（必須）ほか業種・地域・従業員数などの絞り込み | 補助金検索（`GET /subsidies`） |
| `get_subsidy_detail` | `subsidy_id` | 詳細取得＋添付ファイルの自動ダウンロード |
| `get_subsidy_overview` | `output_format`（`json` / `csv`） | 締切期間別・金額規模別の統計（サーバー側で集計） |
| `get_file_content` | `subsidy_id`, `filename`, `return_format` | 保存済み添付を Markdown / BASE64 で取得 |
| `ping` | なし | 疎通確認 |

### 取得できた実データの例

- `search_subsidies(keyword="IT導入")` → 4 件（例: 「令和８年度東京都医療ＤＸ人材育成支援事業」
  `a0WJ200000CDXvUMAX`、上限 50 万円、受付 2026-04-14〜2026-11-30）
- `get_subsidy_overview()` → 全 189 件。締切別 `this_month: 51 / next_month: 22 /
  after_next_month: 116`、金額別 `under_1m: 27 / under_10m: 49 / under_100m: 24 /
  over_100m: 26 / unspecified: 63`、締切間近の案件リスト付き
- `get_file_content()` → 「令和８年度蓄電池_公募要領.pdf」を Markdown 化。表組みも
  パイプ表として抽出され、そのまま LLM に渡せる品質

## 気づいた点

1. **`initialize` のバージョンと `ping` のバージョンが一致しない。**
   `serverInfo.version` は FastMCP 自体のバージョン（3.4.7）が入り、`ping` が返す
   アプリのバージョンは `2.0.0`。クライアント側でサーバー版数を判定する場合は
   `ping` を使う必要がある。
2. **`get_subsidy_overview` は `keyword` を受け取らない。**
   引数は `output_format` のみで、集計対象はサーバー内部の既定キーワード検索結果に固定。
   `keyword` を渡すと pydantic の `unexpected_keyword_argument` で失敗する。
3. **`get_file_content` は `get_subsidy_detail` に依存する。**
   詳細取得時にサーバーのローカルディスク（`JGRANTS_FILES_DIR`）へ保存されたファイルのみ
   読み出せる。事前に同じ `subsidy_id` で `get_subsidy_detail` を呼ぶ必要がある。
   保存先は既定で `./jgrants_files`、リモート運用時はディスク使用量に注意。
4. **添付ファイルを持たない補助金が多い。** 検索結果の先頭がそうだった場合に備えて、
   検証スクリプトは先頭 5 件まで詳細を引いて添付を持つ案件を探す実装にした。
5. **`FastMCP 3.4.7` で動作した。** `requirements.txt` の下限は 2.12.4 だが、
   README が想定する 2.12.x 系との差異による問題は今回の範囲では発生しなかった。
6. **出典表示の義務。** ツールの docstring に「Jグランツ（jGrants）からの出典である旨を
   明記すること」と書かれている。取得データを公開・再配布する場合は出典表記が必要。

## ネットワーク（egress）の状況

エージェントプロキシ経由での到達性を確認した結果:

| ホスト | 結果 |
|---|---|
| `api.jgrants-portal.go.jp` | 到達可（本検証で実利用） |
| `www.jgrants-portal.go.jp` | 到達可 |
| `developers.digital.go.jp` | 到達可（API 公式ドキュメント） |
| `laws.e-gov.go.jp` / `elaws.e-gov.go.jp` | 到達可 |
| `www.e-stat.go.jp` / `api.e-stat.go.jp` | 到達可（API 利用には appId が必要） |
| `www.data.go.jp` | 到達可 |
| `registry.modelcontextprotocol.io` | 到達可 |
| `www.digital.go.jp` | **プロキシで 403（ポリシー拒否）** |

`www.digital.go.jp` のみ egress ポリシーで拒否される。API とドキュメントの
ホストは通るため本検証には影響しないが、デジタル庁の Tech ブログ等を
参照する必要が出た場合は許可リストへの追加が必要。

## 次に検証しうる対象

- e-Gov 法令 API（`laws.e-gov.go.jp`）— 公式 MCP は未提供。第三者実装か自作ラッパーの比較
- e-Stat API（`api.e-stat.go.jp`）— appId 取得が前提
- リモート（`--host 0.0.0.0`）配置時の認証・アクセス制御の要否
