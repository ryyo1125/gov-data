# 情報源台帳

**このファイルは `registry/build.py` が生成する。直接編集しても次回のビルドで失われる。**
内容を変えるときは `registry/sources/*.yaml` を編集し、検証結果を更新するときは
各エントリの再現コマンドを実行して `results/` を更新する。

- 生成日時: 2026-08-19T07:07:56+00:00
- 再検証の目安: 最終検証から 90 日

## 一覧

| ID | 名称 | 提供元 | 権威性 | 方式 | 認証 | 出典表示 | 状態 | 最終検証 |
|---|---|---|---|---|---|---|---|---|
| `egov-hourei-api` | e-Gov 法令 API Version 2 | デジタル庁（e-Gov） | primary_official | rest_api | not_required | undocumented | 検証済 (7/7) | 2026-08-19 |
| `jgrants-mcp` | Jグランツ MCP Server | デジタル庁 | official_wrapper | mcp | not_required | yes | 検証済 (9/9) | 2026-08-19 |

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
- 収録範囲: 検証時点で /laws の total_count が 9541 件。全文検索は法令本文（law_full_text）を対象とする。

### 接続要件

- 認証: `not_required` — OpenAPI 仕様に securitySchemes の定義が無く、認証情報なしで全 6 エンドポイントが 200 を返した。
- レート制限: undocumented
- 利用規約: 未確認
- 出典表示: `undocumented`

### 安定性（一次資料の記述）

- OpenAPI 仕様の「注意事項」に、以下は試行版であり仕様変更が発生する場合があると明記されている。
- 試行版の対象は、法令本文取得 API が返す JSON 形式データ、法令本文ファイル取得 API の JSON 形式データ、キーワード検索 API で名称に law_num を含むパラメータ指定時のレスポンス。
- Version 1（https://laws.e-gov.go.jp/apitop/）を改良開発した後継 API であると仕様に記載。

### 到達性

| ホスト | 役割 | 備考 |
|---|---|---|
| `laws.e-gov.go.jp` | api | API・OpenAPI 仕様・XML 一括ダウンロードのすべてがこのホスト。 |
| `www.e-gov.go.jp` | portal | 検証環境の egress ポリシーで 403。利用規約ページがここにあるため規約を確認できていない。 |

### 検証

- 状態: **検証済**
- 最終検証: 2026-08-19T07:07:34+00:00
- 再現コマンド: `.work/toolvenv/bin/python verify/verify_egov_hourei.py --out results/egov-hourei-api.json`
- 検証スクリプト: `verify/verify_egov_hourei.py` / 結果: `results/egov-hourei-api.json`
- 検証環境: Python 3.11.15 / Linux-6.18.5-fc-v20-x86_64-with-glibc2.39

| ステップ | 結果 | 所要 | 備考 |
|---|---|---|---|
| `fetch_openapi_spec` | OK | 1349 ms |  |
| `GET /laws` | OK | 449 ms |  |
| `GET /law_revisions/{law_id}` | OK | 413 ms |  |
| `GET /law_data/{law_id}` | OK | 450 ms |  |
| `GET /keyword` | OK | 1942 ms |  |
| `GET /law_file/xml/{law_id}` | OK | 485 ms |  |
| `GET /attachment/{law_revision_id}` | OK | 677 ms |  |

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
- **利用規約・出典表示義務・レート制限は未確認。**
  - 根拠: 規約ページのある www.e-gov.go.jp が検証環境の egress ポリシーで 403。OpenAPI 仕様にも該当記述が無い。到達できないだけであり、規約が存在しないという意味ではない。
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
- 収録範囲: 検証時点で get_subsidy_overview が全 189 件を集計。募集中・募集予定の補助金が対象。

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
| `www.digital.go.jp` | portal | 検証環境の egress ポリシーで 403。API 側には影響しない。 |

### 検証

- 状態: **検証済**
- 最終検証: 2026-08-19T07:07:55+00:00
- 再現コマンド: `./verify/run_jgrants_verification.sh`
- 検証スクリプト: `verify/verify_jgrants_mcp.py` / 結果: `results/jgrants-mcp.json`
- 検証環境: Python 3.11.15 / Linux-6.18.5-fc-v20-x86_64-with-glibc2.39

| ステップ | 結果 | 所要 | 備考 |
|---|---|---|---|
| `initialize` | OK | 0 ms |  |
| `list_tools` | OK | 19 ms |  |
| `list_resources` | OK | 9 ms |  |
| `list_prompts` | OK | 7 ms |  |
| `call:ping` | OK | 14 ms |  |
| `call:search_subsidies` | OK | 1109 ms |  |
| `call:get_subsidy_detail` | OK | 238 ms |  |
| `call:get_subsidy_overview` | OK | 1823 ms |  |
| `call:get_file_content` | OK | 2861 ms |  |

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
- **出典表示義務はドキュメントではなくツールの docstring にのみ書かれている。**
  - 根拠: jgrants_mcp_server/core.py の各ツール docstring に「出典表示」の記載。

## 保留中の候補（到達不能で未登録）

検証環境の egress ポリシーで到達できず、事実を書く根拠が得られなかったもの。
台帳に載せていないのは提供が終わっているからではない。
実体は `registry/blocked.yaml`。

### 気象庁防災情報XML（PULL型 Atom フィード） (`jma-xml`)

- 状態: 到達不可のまま
- 調べた理由: 防災気象情報を台帳に登録するために調査した。
- 対象ホスト: `xml.kishou.go.jp`, `www.jma.go.jp`, `www.data.jma.go.jp`
- 到達できない理由: 3 ホストすべてが検証環境の egress ポリシーで 403（httpx.ProxyError: 403 Forbidden）。 実データはもちろん、仕様書 https://xml.kishou.go.jp/xmlpull.html にも到達できないため、 エンドポイント・更新頻度・利用規約のいずれも一次資料で確認できない。 Web 検索で得られる二次情報だけを根拠にエントリを書くことは台帳の規律に反するので登録しない。
- 次の一手: xml.kishou.go.jp / www.jma.go.jp / www.data.jma.go.jp を egress 許可リストに追加してから、 xmlpull.html でフィード URL を確認し、verify/verify_jma_xml.py を書いて検証する。

### e-Gov データポータル（CKAN API） (`egov-data-catalog`)

- 状態: 到達不可のまま
- 調べた理由: 台帳に載せる候補を機械的に洗い出せるカタログとして調査した。
- 対象ホスト: `data.e-gov.go.jp`, `www.data.go.jp`
- 到達できない理由: www.data.go.jp/api/3/action/* は data.e-gov.go.jp へ 301 リダイレクトされ、 そのホストが検証環境の egress ポリシーで 403。カタログ API を実行できない。
- 次の一手: data.e-gov.go.jp を egress 許可リストに追加してから CKAN API を検証する。


## 到達性の実測

`verify/verify_reachability.py` の実測結果（2026-08-19T07:07:28+00:00）。
到達できないことは、そのサービスが存在しないことを意味しない。

| ホスト | 結果 | 詳細 |
|---|---|---|
| `api.jgrants-portal.go.jp` | 到達可 | HTTP 404 |
| `data.e-gov.go.jp` | egress で拒否 | プロキシが拒否: 403 Forbidden |
| `developers.digital.go.jp` | 到達可 | HTTP 200 |
| `laws.e-gov.go.jp` | 到達可 | HTTP 200 |
| `www.data.go.jp` | 到達可 | HTTP 301 |
| `www.data.jma.go.jp` | egress で拒否 | プロキシが拒否: 403 Forbidden |
| `www.digital.go.jp` | egress で拒否 | プロキシが拒否: 403 Forbidden |
| `www.e-gov.go.jp` | egress で拒否 | プロキシが拒否: 403 Forbidden |
| `www.jgrants-portal.go.jp` | 到達可 | HTTP 200 |
| `www.jma.go.jp` | egress で拒否 | プロキシが拒否: 403 Forbidden |
| `xml.kishou.go.jp` | egress で拒否 | プロキシが拒否: 403 Forbidden |
