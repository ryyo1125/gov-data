# 情報源台帳

**このファイルは `registry/build.py` が生成する。直接編集しても次回のビルドで失われる。**
内容を変えるときは `registry/sources/*.yaml` を編集し、検証結果を更新するときは
各エントリの再現コマンドを実行して `results/` を更新する。

- 生成日時: 2026-08-19T09:17:14+00:00
- 再検証の目安: 最終検証から 90 日

## 一覧

| ID | 名称 | 提供元 | 権威性 | 方式 | 認証 | 出典表示 | 状態 | 最終検証 |
|---|---|---|---|---|---|---|---|---|
| `egov-data-catalog` | e-Gov データポータル（CKAN API） | デジタル庁（e-Gov） | primary_official | rest_api | not_required | yes | 検証済 (7/7) | 2026-08-19 |
| `egov-hourei-api` | e-Gov 法令 API Version 2 | デジタル庁（e-Gov） | primary_official | rest_api | not_required | yes | 検証済 (8/8) | 2026-08-19 |
| `jgrants-mcp` | Jグランツ MCP Server | デジタル庁 | official_wrapper | mcp | not_required | yes | 検証済 (9/9) | 2026-08-19 |
| `jma-xml` | 気象庁防災情報XML（PULL型 Atom フィード） | 気象庁 | primary_official | rest_api | not_required | undocumented | 検証済 (9/9) | 2026-08-19 |

## e-Gov データポータル（CKAN API） (`egov-data-catalog`)

日本政府のオープンデータカタログ。府省庁が公開するデータセットのメタデータを CKAN の標準 API で検索・取得できる。台帳に載せる候補を機械的に洗い出す用途に使える。

### 提供と経路

- 提供元: デジタル庁（e-Gov）（権威性: `primary_official`）
- 一次情報: https://data.e-gov.go.jp/
- 方式: `rest_api` / エンドポイント: `https://data.e-gov.go.jp/data/api/3/action`
- 仕様: https://docs.ckan.org/en/latest/api/

### 提供される情報

- 種類: オープンデータのメタデータ
- 形式: json
- 更新頻度: undocumented
- 収録範囲: 府省庁が公開するデータセットのメタデータを収録する。実データそのものは各データセットの resource が指す先にある。
- 実測値: package_search の count は 18141 件
- 実測値: tag_list は 5745 件

### 接続要件

- 認証: `not_required` — 認証情報なしで 7 アクションすべてが success=true を返した。
- レート制限: undocumented
- 利用規約: https://www.e-gov.go.jp/terms
- 出典表示: `yes` — 出典：e-Govポータル（https://www.e-gov.go.jp）の形式で出典を記載する。

### 安定性（一次資料の記述）

- CKAN の標準 API を採用しているが、e-Gov 側でのバージョン管理方針やサポート終了予定に関する記述は見つかっていない。

### 到達性

| ホスト | 役割 | 備考 |
|---|---|---|
| `data.e-gov.go.jp` | api | CKAN API の実体。 |
| `www.data.go.jp` | portal | /api/3/action/* は data.e-gov.go.jp へ 301 リダイレクトされる。 |
| `www.e-gov.go.jp` | terms |  |

### 検証

- 状態: **検証済**
- 最終検証: 2026-08-19T09:08:47+00:00
- 再現コマンド: `.work/toolvenv/bin/python verify/verify_egov_data_catalog.py --out results/egov-data-catalog.json`
- 検証スクリプト: `verify/verify_egov_data_catalog.py` / 結果: `results/egov-data-catalog.json`
- 検証環境: Python 3.11.15 / Linux-6.18.5-fc-v20-x86_64-with-glibc2.39

| ステップ | 結果 | 所要 | 備考 |
|---|---|---|---|
| `site_read` | OK | 838 ms |  |
| `package_search` | OK | 571 ms |  |
| `package_list` | OK | 241 ms |  |
| `organization_list` | OK | 263 ms |  |
| `group_list` | OK | 256 ms |  |
| `tag_list` | OK | 683 ms |  |
| `package_show` | OK | 587 ms |  |

### 実行して分かったこと

- **API のパスは CKAN 標準の /api/3/action/* ではなく /data/api/3/action/* である。標準のパスは 404 を返す。**
  - 根拠: https://data.e-gov.go.jp/api/3/action/package_search が 404、/data/api/3/action/package_search が 200 を返すことを確認。
- **旧窓口 www.data.go.jp/api/3/action/* は data.e-gov.go.jp へ 301 リダイレクトされるが、リダイレクト先も 404 になる。移行先を知らないと辿り着けない。**
  - 根拠: curl -L で 301 -> https://data.e-gov.go.jp/api/3/action/package_search -> 404 を確認。
- **データセットのライセンス情報は事実上入っていない。license_id と license_title は取得した 100 件すべてで null だった。**
  - 根拠: package_search?rows=100 の結果を集計し、license_title が「なし」100 件であることを確認。カタログだけでは再配布可否を判断できない。
- **frequency_of_update は日本語の自由記述で、表記が揺れる。機械処理には正規化が要る。**
  - 根拠: 100 件サンプルで「少なくとも年1回」「更新しない」「年２回」「四半期」「1年」など全角半角混在の値が並んだ。
- **tag_list に先頭が半角スペースのタグが含まれる。**
  - 根拠: tag_list の先頭 3 件が " ガス", " スポーツ", " エネルギー" と、いずれも空白始まりだった。
- **package_list が返すのは CKAN 標準のデータセット名ではなく日付らしき文字列である。**
  - 根拠: package_list?limit=5 の戻り値が ["20160621", "20170627", "20180710"] だった。
- **メタデータ項目の定義書が公開されていない。項目の意味は、データセット画面に出る日本語ラベルを同じ値の API 項目と突き合わせて推定するしかない。**
  - 根拠: data.e-gov.go.jp の /info/ja/help と /info/ja/about-site を辿ってもメタデータ項目の仕様へのリンクが無く、API も項目説明を返さない。値による突合で説明を付けられたのは 87 項目中 22 項目にとどまった。
- **データセット画面のメタデータは「e-Govデータポータル標準」と「自治体標準ODS オープンデータ一覧」の 2 系統に分かれ、HTML 上も別クラスで区別されている。**
  - 根拠: データセット画面の tr が metadata_basic_field と metadata_detail_field に分かれており、画面上も「一部表示／全て表示」で切り替えられる。
- **package_show は id を渡さないと HTTP 409 を返す。404 ではない。**
  - 根拠: /package_show?limit=1 で 409 と success=false を確認。

## e-Gov 法令 API Version 2 (`egov-hourei-api`)

デジタル庁が運用する e-Gov 法令検索の法令データを提供する HTTP API。法令一覧・改正履歴・本文・全文検索・添付ファイルを取得できる。

### 提供と経路

- 提供元: デジタル庁（e-Gov）（権威性: `primary_official`）
- 一次情報: https://laws.e-gov.go.jp/
- 方式: `rest_api` / エンドポイント: `https://laws.e-gov.go.jp/api/2`
- 仕様: https://laws.e-gov.go.jp/api/2/swagger-ui/lawapi-v2.yaml（2.1.139）

### 提供される情報

- 種類: 法令
- 形式: json / xml / pdf
- 更新頻度: undocumented
- 収録範囲: 法令一覧・改正履歴・本文・添付ファイルを提供。全文検索は法令本文（law_full_text）を対象とする。
- 実測値: /laws の total_count は 9541 件（全法令）

### 接続要件

- 認証: `not_required` — OpenAPI 仕様に securitySchemes の定義が無く、認証情報なしで全 6 エンドポイントが 200 を返した。
- レート制限: undocumented
- 利用規約: https://www.e-gov.go.jp/terms
- 出典表示: `yes` — 出典：e-Govポータル（https://www.e-gov.go.jp）の形式で出典を記載する。実際の提供元や当該ページの URL に置き換えてよい。

### 安定性（一次資料の記述）

- OpenAPI 仕様の「注意事項」に、以下は試行版であり仕様変更が発生する場合があると明記されている。
- 試行版の対象は、法令本文取得 API が返す JSON 形式データ、法令本文ファイル取得 API の JSON 形式データ、キーワード検索 API で名称に law_num を含むパラメータ指定時のレスポンス。
- Version 1（https://laws.e-gov.go.jp/apitop/）を改良開発した後継 API であると仕様に記載。

### 到達性

| ホスト | 役割 | 備考 |
|---|---|---|
| `laws.e-gov.go.jp` | api | API・OpenAPI 仕様・XML 一括ダウンロードのすべてがこのホスト。 |
| `www.e-gov.go.jp` | terms | 利用規約（PDL1.0 の適用と出典記載例）はこのホスト。API 本体とはホストが異なる。 |

### 検証

- 状態: **検証済**
- 最終検証: 2026-08-19T09:08:43+00:00
- 再現コマンド: `.work/toolvenv/bin/python verify/verify_egov_hourei.py --out results/egov-hourei-api.json`
- 検証スクリプト: `verify/verify_egov_hourei.py` / 結果: `results/egov-hourei-api.json`
- 検証環境: Python 3.11.15 / Linux-6.18.5-fc-v20-x86_64-with-glibc2.39

| ステップ | 結果 | 所要 | 備考 |
|---|---|---|---|
| `fetch_openapi_spec` | OK | 989 ms |  |
| `GET /laws（全件数）` | OK | 1098 ms |  |
| `GET /laws` | OK | 337 ms |  |
| `GET /law_revisions/{law_id}` | OK | 279 ms |  |
| `GET /law_data/{law_id}` | OK | 311 ms |  |
| `GET /keyword` | OK | 1406 ms |  |
| `GET /law_file/xml/{law_id}` | OK | 324 ms |  |
| `GET /attachment/{law_revision_id}` | OK | 502 ms |  |

### 実行して分かったこと

- **認証は不要。API キーの登録手続きも存在しない。**
  - 根拠: 仕様に securitySchemes が無いことを検証スクリプトが declares_security_scheme=false として記録。加えて認証情報なしで 6 エンドポイントすべてが 200 を返した。
- **添付ファイルが存在しない law_revision_id を /attachment に渡すと、HTTP 200 でも 404 でもなく HTTP 400 で code 404003 が返る。**
  - 根拠: 321CONSTITUTION_19470503_000000000000000 を指定して {"code":"404003","message":"指定のパラメータで取得できる添付ファイルは存在しません。"} を確認。
- **law_revision_id は law_info ではなく revision_info 配下にある。**
  - 根拠: /law_data のレスポンスで law_info に revision id が無く、revision_info.law_revision_id に存在することを確認。
- **law_revision_id は改正のたびに変わるため、検証スクリプトにハードコードできない。**
  - 根拠: law_revision_id の書式が {law_id}_{施行日}_{改正法令 ID} であり、民法は 129AC0000000089_20260624_508AC0000000045 だった。
- **添付ファイルを持つ法令は少数。省令 40 件を走査して 3 件のみ該当した。**
  - 根拠: /laws?law_type=MinisterialOrdinance の先頭 40 件について law_data の attached_files_info を確認。
- **利用規約は API のドキュメントではなく e-Gov ポータル側にあり、PDL1.0 の適用対象は「e-gov.go.jp 及びそのサブドメイン」と書かれているため laws.e-gov.go.jp も含まれる。**
  - 根拠: https://www.e-gov.go.jp/terms の本文で「e-gov.go.jp及びそのサブドメインのWebサイト（中略）で公開している情報（中略）の著作権は、特記されていない限りデジタル庁に帰属し、権利表記の記載がない限り『公共データ利用規約（第1.0版）』（PDL1.0）が適用されます」と確認。
- **規約ページは既定の User-Agent では先方の WAF に拒否される。egress の問題ではない。**
  - 根拠: 既定 UA では HTTP 403 で「アクセスがブロックされています｜e-Gov」の HTML が返り、ブラウザ相当の UA では 200 が返った。
- **レート制限は依然として一次資料に記述が無い。**
  - 根拠: OpenAPI 仕様および https://www.e-gov.go.jp/terms のいずれにもレート制限の記載が無いことを確認。
- **API とは別に XML 一括ダウンロードが提供されている。**
  - 根拠: OpenAPI 仕様の description に https://laws.e-gov.go.jp/bulkdownload?file_section=1&only_xml_flag=true が記載。

## Jグランツ MCP Server (`jgrants-mcp`)

デジタル庁が運用する補助金電子申請システム「Jグランツ」の公開 API を、デジタル庁自身が MCP サーバーとして実装したもの。

### 提供と経路

- 提供元: デジタル庁（権威性: `official_wrapper`）
- 一次情報: https://www.jgrants-portal.go.jp/
- 方式: `mcp` / エンドポイント: `http://127.0.0.1:8000/mcp`
- 仕様: https://developers.digital.go.jp/documents/jgrants/api/
- 実装: digital-go-jp/jgrants-mcp-server（保守: デジタル庁 / MIT / 検証時 2.0.0）

### 提供される情報

- 種類: 補助金・助成金
- 形式: json / markdown / pdf / docx / csv
- 更新頻度: undocumented
- 収録範囲: 募集中・募集予定の補助金が対象。過去の募集は含まれない。
- 実測値: get_subsidy_overview が集計した総数は 189 件

### 接続要件

- 認証: `not_required` — 検証時、API キー等を一切設定せずに全ツールが応答した。ただし公式ドキュメントに認証要否の記述は無い。
- レート制限: undocumented
- 利用規約: 未確認
- 出典表示: `yes` — 本ツールで取得した情報を利用・公開する際は「Jグランツ（jGrants）からの出典」である旨を明記すること。

### 安定性（一次資料の記述）

- 公式ドキュメントに API のバージョン管理方針・サポート終了予定の記述は無い。
- ベース URL は https://api.jgrants-portal.go.jp/exp/v1/public であり、パスに exp を含む。

### 到達性

| ホスト | 役割 | 備考 |
|---|---|---|
| `api.jgrants-portal.go.jp` | api | MCP サーバーが実際に叩く先。 |
| `www.jgrants-portal.go.jp` | portal |  |
| `developers.digital.go.jp` | docs |  |
| `www.digital.go.jp` | portal |  |
| `files.microcms-assets.io` | spec | 公式 OpenAPI 仕様 jgrants-api.yaml の実体。政府ドメインではない CDN のため許可リストから漏れやすい。 |

### 検証

- 状態: **検証済**
- 最終検証: 2026-08-19T09:09:15+00:00
- 再現コマンド: `./verify/run_jgrants_verification.sh`
- 検証スクリプト: `verify/verify_jgrants_mcp.py` / 結果: `results/jgrants-mcp.json`
- 検証環境: Python 3.11.15 / Linux-6.18.5-fc-v20-x86_64-with-glibc2.39

| ステップ | 結果 | 所要 | 備考 |
|---|---|---|---|
| `initialize` | OK | 0 ms |  |
| `list_tools` | OK | 24 ms |  |
| `list_resources` | OK | 12 ms |  |
| `list_prompts` | OK | 9 ms |  |
| `call:ping` | OK | 12 ms |  |
| `call:search_subsidies` | OK | 1430 ms |  |
| `call:get_subsidy_detail` | OK | 288 ms |  |
| `call:get_subsidy_overview` | OK | 1818 ms |  |
| `call:get_file_content` | OK | 2318 ms |  |

### 実行して分かったこと

- **get_subsidy_overview は keyword を受け取らない。引数は output_format のみ。**
  - 根拠: keyword を渡して pydantic の unexpected_keyword_argument で失敗。jgrants_mcp_server/core.py:233 のシグネチャで確認。
- **initialize が返す serverInfo.version は FastMCP 自体の版数で、アプリの版数は ping でしか取れない。**
  - 根拠: results/jgrants-mcp.json の initialize が 3.4.7、call:ping が 2.0.0 を返した。
- **get_file_content は事前に同じ subsidy_id で get_subsidy_detail を呼ぶ必要がある。**
  - 根拠: get_subsidy_detail が JGRANTS_FILES_DIR 配下へ保存したファイルのみ読める（core.py:630 以降）。
- **添付ファイルを持たない補助金が多く、検索結果の先頭だけでは get_file_content を検証できない。**
  - 根拠: 検証スクリプトで先頭 5 件まで詳細を引き直す実装が必要だった（verify_jgrants_mcp.py の FILE_PROBE_LIMIT）。
- **公式ドキュメントには認証要否・レート制限・利用規約・API 安定性の記述が無い。**
  - 根拠: https://developers.digital.go.jp/documents/jgrants/api/ を参照して該当記述が無いことを確認。
- **公式 OpenAPI 仕様 jgrants-api.yaml は developers.digital.go.jp ではなく microCMS のアセット CDN（files.microcms-assets.io）にホストされており、当環境の egress ポリシーで取得できない。戻り値の項目説明が埋められないのはこのため。**
  - 根拠: 仕様ページの HTML 内リンクが https://files.microcms-assets.io/assets/.../jgrants-api.yaml を指しており、当該ホストへの CONNECT がプロキシに 403 で拒否されることを確認。
- **出典表示義務はドキュメントではなくツールの docstring にのみ書かれている。**
  - 根拠: jgrants_mcp_server/core.py の各ツール docstring に「出典表示」の記載。

## 気象庁防災情報XML（PULL型 Atom フィード） (`jma-xml`)

気象庁が発表する警報・注意報、天気概況、地震・火山情報などの電文を、Atom フィード経由で取得できる公開サービス。認証不要の HTTPS GET のみで構成される。

### 提供と経路

- 提供元: 気象庁（権威性: `primary_official`）
- 一次情報: https://xml.kishou.go.jp/xmlpull.html
- 方式: `rest_api` / エンドポイント: `https://www.data.jma.go.jp/developer/xml/feed`
- 仕様: https://xml.kishou.go.jp/xmlpull.html

### 提供される情報

- 種類: 気象警報・注意報 / 天気概況 / 地震・火山情報 / 海上警報
- 形式: atom / xml
- 更新頻度: 高頻度フィード（regular / extra / eqvol / other）は毎分更新で直近少なくとも 10 分の入電を掲載。長期フィード（同名 + _l）は毎時更新で数日間の全入電を掲載。
- 収録範囲: 定時・随時・地震火山・その他の 4 系統について、高頻度と長期の 2 種類のフィードを提供。 entry 数は入電のたびに変わるため件数は台帳に書かない（実測は results/jma-xml.json を参照）。

### 接続要件

- 認証: `not_required` — 認証情報なしで 8 フィードと電文本体のすべてが 200 を返した。仕様ページにも認証に関する記述は無い。
- レート制限: 1 日 10GB 以上のダウンロードを伴うアクセスが確認された場合、アクセス元 IP アドレスを遮断すると xmlpull.html に明記。
- 利用規約: https://xml.kishou.go.jp/considerationforxml.pdf
- 出典表示: `undocumented`

### 安定性（一次資料の記述）

- サーバーメンテナンス等により配信が停止・遅延する場合があると xmlpull.html に明記。
- 電文のフォーマットやコード表は業務の変更等により随時更新・変更される場合があると留意事項 PDF に明記。
- 利用者が電文を用いて行う一切の行為について気象庁は責任を負わないと明記。

### 到達性

| ホスト | 役割 | 備考 |
|---|---|---|
| `xml.kishou.go.jp` | docs | 仕様ページと留意事項 PDF。フィード本体とはホストが異なる。 |
| `www.data.jma.go.jp` | api | Atom フィードと電文本体の実体はすべてこのホスト。 |
| `www.jma.go.jp` | portal |  |

### 検証

- 状態: **検証済**
- 最終検証: 2026-08-19T09:09:02+00:00
- 再現コマンド: `.work/toolvenv/bin/python verify/verify_jma_xml.py --out results/jma-xml.json`
- 検証スクリプト: `verify/verify_jma_xml.py` / 結果: `results/jma-xml.json`
- 検証環境: Python 3.11.15 / Linux-6.18.5-fc-v20-x86_64-with-glibc2.39

| ステップ | 結果 | 所要 | 備考 |
|---|---|---|---|
| `GET /regular.xml (定時・高頻度)` | OK | 2354 ms |  |
| `GET /extra.xml (随時・高頻度)` | OK | 1437 ms |  |
| `GET /eqvol.xml (地震火山・高頻度)` | OK | 806 ms |  |
| `GET /other.xml (その他・高頻度)` | OK | 794 ms |  |
| `GET /regular_l.xml (定時・長期)` | OK | 2950 ms |  |
| `GET /extra_l.xml (随時・長期)` | OK | 2447 ms |  |
| `GET /eqvol_l.xml (地震火山・長期)` | OK | 832 ms |  |
| `GET /other_l.xml (その他・長期)` | OK | 819 ms |  |
| `GET 電文本体` | OK | 1986 ms |  |

### 実行して分かったこと

- **仕様ページのホスト（xml.kishou.go.jp）とフィード本体のホスト（www.data.jma.go.jp）が異なる。片方だけを許可リストに入れても使えない。**
  - 根拠: xmlpull.html 内のフィードリンクがすべて https://www.data.jma.go.jp/developer/xml/feed/ を指していることを確認。
- **長期フィードを高頻度フィードと同じ毎分間隔で取得すると、明記された 1 日 10GB の遮断閾値を超える。**
  - 根拠: 検証時の長期 4 本の合計が約 8.9MB。毎分取得すると 8.9MB×1440≒12.8GB/日となり閾値を超える。仕様どおり毎時取得なら約 213MB/日に収まる。
- **フィード自体の updated は JST（+09:00）、entry の updated は UTC（Z）で表記され、同一フィード内でタイムゾーン表記が混在する。**
  - 根拠: regular.xml の feed_updated が 2026-08-19T16:34:45+09:00、先頭 entry の updated が 2026-08-19T07:34:33Z。
- **電文本体のルート要素は名前空間 http://xml.kishou.go.jp/jmaxml1/ の Report で、Control と Head を子に持つ。**
  - 根拠: 取得した VPFG50（府県天気概況）電文の root_tag と child_tags を results/jma-xml.json に記録。
- **公式の XML Schema が配布されており、全電文共通の Report / Control / Head の構造はそこから確定できる。一方 Body は電文種別ごとに異なり、共通スキーマからは決まらない。**
  - 根拠: https://xml.kishou.go.jp/jmaxml_20241031_Schema(xsd).zip に jmx.xsd ほか 8 ファイルが含まれ、jmx.xsd の type.report が Control と Head の後に任意の名前空間の要素 1 つを取る定義になっている。
- **出典表示の義務は一次資料に明記されていない。ただし編集して流通させる場合は編集責任者の明示義務がある。**
  - 根拠: 留意事項 PDF「３．（３）編集責任者等の明示について」に編集時の明示義務の記載があり、出典表示に関する記載は無い。

## 到達性の実測

`verify/verify_reachability.py` の実測結果（2026-08-19T09:08:37+00:00）。
到達できないことは、そのサービスが存在しないことを意味しない。

| ホスト | 結果 | 詳細 |
|---|---|---|
| `api.jgrants-portal.go.jp` | 到達可 | HTTP 404 |
| `data.e-gov.go.jp` | 到達可 | HTTP 301 |
| `developers.digital.go.jp` | 到達可 | HTTP 200 |
| `files.microcms-assets.io` | egress で拒否 | プロキシが拒否: 403 Forbidden |
| `laws.e-gov.go.jp` | 到達可 | HTTP 200 |
| `www.data.go.jp` | 到達可 | HTTP 301 |
| `www.data.jma.go.jp` | 到達可 | HTTP 200 |
| `www.digital.go.jp` | 到達可 | HTTP 200 |
| `www.e-gov.go.jp` | 到達可 | HTTP 403 |
| `www.jgrants-portal.go.jp` | 到達可 | HTTP 200 |
| `www.jma.go.jp` | 到達可 | HTTP 302 |
| `xml.kishou.go.jp` | 到達可 | HTTP 200 |
