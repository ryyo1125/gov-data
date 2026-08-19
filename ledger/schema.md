# データ台帳スキーマ（医療系補助金ウォッチ MVP）

台帳は2層。**取得記録**（いつ・どの条件で叩いたか）と**公募レコード**（何が返ってきたか）を分離する。
これを分けないと「取れなかったのか、存在しなかったのか」が後から区別できない。

## 1. `runs.csv` — 取得記録（1リクエスト＝1行）

| 列 | 内容 |
|---|---|
| `run_id` | 実行ID（`YYYYMMDD-HHMM-連番`） |
| `fetched_at` | 取得日時（UTC, ISO8601） |
| `server` | `digital-go-jp/jgrants-mcp-server` |
| `server_version` | `ping` が返す version（例 `2.0.0`） |
| `tool` | `search_subsidies` 等 |
| `params_json` | 渡した引数一式（再取得できる完全な形で） |
| `http_status` | 成否。エラー時はメッセージ全文 |
| `returned_count` | 返ってきた件数（`total_count` は総件数ではない点に注意） |
| `truncated_suspected` | 件数が上限値ちょうど等、打ち切りが疑われる場合 `1` |

## 2. `subsidies.csv` — 公募レコード（1補助金＝1行、`subsidy_id` で一意）

| 列 | 出所 | 備考 |
|---|---|---|
| `subsidy_id` | API `id` | 主キー |
| `title` | API `title` | |
| `institution_name` | API **[要確認]** | 実測後に確定 |
| `subsidy_max_limit` | API | 数値化前の原文も残す |
| `acceptance_start` / `acceptance_end` | API | ISO8601 |
| `target_area` / `target_industry` / `target_employees` / `use_purpose` | API | |
| `application_url` | API `inquiry_url` | |
| `portal_url` | 生成 | `https://www.jgrants-portal.go.jp/grants/view/{subsidy_id}` |
| `last_updated` | API `update_datetime` | **差分検知の主キー** |
| `matched_keywords` | 生成 | どのキーワードで引っかかったか（カバレッジ検証用・複数可） |
| `first_seen_run_id` / `last_seen_run_id` | 生成 | 消えた公募の検知に使う |
| `detail_fetched` | 生成 | 詳細APIを叩いたか |
| `attachments_count` | API | 添付ファイル数 |
| `pdf_only_fields` | 生成 | 補助率・対象経費など、PDFからしか取れなかった項目名 |

## 記録規約

- **欠損は空欄にしない。** `NOT_RETURNED`（APIが返さなかった）と `NOT_FETCHED`（こちらが取りに行っていない）を区別する。
- 加工値（金額の数値化、業種の再分類など）は必ず**原文列を隣に残す**。
- 公募は取り下げ・修正されうる。`last_updated` の変化と、前回 run に居たのに今回消えた `subsidy_id` の両方を差分レポートに出す。

## カバレッジ検証の記録

`keyword` が必須で業種は「医療、福祉」しか無いため、カバレッジはキーワード選定に完全依存する。
キーワード候補（初期案）: 医療 / 診療所 / クリニック / 歯科 / 医科 / 電子カルテ / オンライン診療 /
医療DX / 病院 / 介護 / IT導入。

`keyword_coverage.csv` に、キーワードごとの `hit_count`・`unique_contribution`（そのキーワードでしか
取れなかった件数）を記録する。**寄与ゼロのキーワードは落とし、寄与の高いものだけで定期実行の型を作る。**
