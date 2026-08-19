# Jグランツで「何が取れるか」— 項目リファレンス

出典区分を明示する。**[実測]** = 公式MCPサーバーへ接続して確認、**[ソース]** = 公式サーバー
[core.py](https://github.com/digital-go-jp/jgrants-mcp-server/blob/main/jgrants_mcp_server/core.py) の実装から確認、
**[要確認]** = 第三者記事由来で未検証（実データ取得後に検証すること）。

## 検索の絞り込み軸 [ソース]

| パラメータ | 取りうる値 |
|---|---|
| `keyword` | **必須**・2〜255文字。全角半角・大小文字の表記ゆれは吸収される |
| `industry` | 日本標準産業分類の大分類20種。複数指定は ` / ` 区切り |
| `use_purpose` | 15種（「設備整備・IT導入をしたい」「人材育成を行いたい」等）。複数指定は ` / ` 区切り |
| `target_number_of_employees` | 「従業員数の制約なし」「5名以下」「20名以下」「50名以下」「100名以下」「300名以下」「900名以下」「901名以上」 |
| `target_area_search` | 「全国」＋地方ブロック9種＋47都道府県 |
| `sort` | `created_date` / `acceptance_start_datetime` / `acceptance_end_datetime` |
| `order` | `ASC` / `DESC` |
| `acceptance` | `1`=受付中のみ / `0`=フィルタなし（＝過去公募も含む） |

## 医療系に絞る場合の制約（重要）

1. **業種の粒度は「医療、福祉」の1カテゴリのみ** [ソース]
   産業分類の大分類しか無いため、クリニック・歯科・介護・保育がすべて同一カテゴリに混在する。
   **歯科だけ／無床診療所だけ、といった絞り込みは業種パラメータでは不可能。**
   → `keyword` との併用が必須（例: "歯科" "診療所" "医科" "電子カルテ" "オンライン診療"）。

2. **`keyword` が必須なので「業種で全件」が取れない** [ソース]
   カバレッジはキーワード選定に完全に依存する。
   → 検証の最重要項目は「どのキーワード集合なら該当公募を取りこぼさないか」。
   複数キーワードで引いて `id` で和集合を取り、キーワードごとの寄与率を台帳に記録する運用が要る。

3. **`total_count` はAPIの総件数ではない** [ソース]
   実装は `total_count = len(data["result"])`、つまり**返ってきた配列の長さ**。
   `limit`/`offset` は渡していないため、API側に上限があれば黙って切れる。
   → 上限の有無は実データで要確認。切れているのに「全件」と誤読するリスクがある。

4. **`acceptance=1` が既定** [ソース]
   既定では受付中のみ。**過年度の傾向分析には `acceptance=0` が必要。**

## 取得できる項目

### 検索結果（`search_subsidies`）
APIの `result` 配列をそのまま返す [ソース]。含まれる項目は
`id` / `name` / `title` / `subsidy_max_limit` / `acceptance_start_datetime` /
`acceptance_end_datetime` / `target_area_search` / `target_number_of_employees` 等 **[要確認]**。

### 詳細（`get_subsidy_detail`）[ソース]

| 返却キー | 元APIフィールド | 内容 |
|---|---|---|
| `id` | `id` | 補助金ID（例 `a0WJ200000CDR9HMAX`） |
| `title` | `title` | 補助金名称 |
| `description` | `detail` | 詳細説明（**HTML形式**。台帳投入時は要パース） |
| `subsidy_max_limit` | `subsidy_max_limit` | 最大補助額 |
| `acceptance_start` / `acceptance_end` | `acceptance_*_datetime` | 募集開始／終了（ISO8601） |
| `status` | （クライアント側算出） | 締切が未来なら「受付中」。**API由来ではない** |
| `target.area` | `target_area_search` | 補助対象地域 |
| `target.industry` | `target_industry` | 対象業種 |
| `target.employees` | `target_number_of_employees` | 対象従業員数 |
| `target.purpose` | `use_purpose` | 利用目的 |
| `application_url` | `inquiry_url` | 申請・問合せページURL |
| `last_updated` | `update_datetime` | 最終更新日時（**差分検知の鍵**） |
| `files.application_guidelines` | `application_guidelines` | 公募要領（BASE64→ローカル保存） |
| `files.outline_of_grant` | `outline_of_grant` | 補助金概要（同上） |
| `files.application_form` | `application_form` | 申請様式（同上） |

補助率・対象経費・申請要件といった**実務上いちばん効く条件は構造化されておらず、
添付PDF本文にしか無い**可能性が高い。`get_file_content` でMarkdown化して読む必要がある。
「構造化項目で分かること／PDFを開かないと分からないこと」の比率測定を検証項目に入れる。

### 集計（`get_subsidy_overview`）[ソース]
`search_subsidies` の結果に対するクライアント側集計。締切時期別（今月／来月／それ以降）、
補助額レンジ別（〜100万／〜1000万／〜1億／1億超／未指定）、締切間近リスト、高額補助金リスト。
**元の検索結果に依存するため、キーワードのカバレッジがそのまま集計の偏りになる。**

## 利用条件

公式サーバーのdocstringに明記: 取得情報を利用・公開する際は
**「Jグランツ（jGrants）からの出典」である旨を明記**すること。
人間向けページURLは `https://www.jgrants-portal.go.jp/grants/view/{subsidy_id}`。
