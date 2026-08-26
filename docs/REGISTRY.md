# 情報源台帳

**このファイルは `registry/build.py` が生成する。直接編集しても次回のビルドで失われる。**
内容を変えるときは `registry/sources/*.yaml` を編集し、検証結果を更新するときは
各エントリの再現コマンドを実行して `results/` を更新する。

- 生成日時: 2026-08-26T01:10:32+00:00
- 再検証の目安: 最終検証から 90 日

## 一覧

| ID | 名称 | 提供元 | 権威性 | 方式 | 認証 | 出典表示 | 状態 | 最終検証 |
|---|---|---|---|---|---|---|---|---|
| `egov-data-catalog` | e-Gov データポータル（CKAN API） | デジタル庁（e-Gov） | primary_official | rest_api | not_required | yes | 検証済 (7/7) | 2026-08-26 |
| `egov-hourei-api` | e-Gov 法令 API Version 2 | デジタル庁（e-Gov） | primary_official | rest_api | not_required | yes | 検証済 (8/8) | 2026-08-26 |
| `estat-lod` | 統計 LOD（SPARQL エンドポイント） | 総務省統計局・独立行政法人統計センター（e-Stat） | primary_official | rest_api | not_required | yes | 検証済 (7/7) | 2026-08-26 |
| `gsi-tiles` | 地理院タイル（国土地理院 XYZ タイル配信） | 国土交通省国土地理院 | primary_official | rest_api | not_required | yes | 検証済 (14/15) | 2026-08-26 |
| `jgrants-mcp` | Jグランツ MCP Server | デジタル庁 | official_wrapper | mcp | not_required | yes | 検証済 (9/9) | 2026-08-26 |
| `jma-xml` | 気象庁防災情報XML（PULL型 Atom フィード） | 気象庁 | primary_official | rest_api | not_required | undocumented | 検証済 (9/9) | 2026-08-26 |
| `ndl-search` | 国立国会図書館サーチ 外部提供インタフェース | 国立国会図書館 | primary_official | rest_api | not_required | undocumented | 検証済 (7/7) | 2026-08-26 |

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
- 実測値: package_search の count は 18140 件
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
- 最終検証: 2026-08-26T01:03:24+00:00
- 再現コマンド: `.work/toolvenv/bin/python verify/verify_egov_data_catalog.py --out results/egov-data-catalog.json`
- 検証スクリプト: `verify/verify_egov_data_catalog.py` / 結果: `results/egov-data-catalog.json`
- 検証環境: Python 3.11.15 / Linux-6.18.44-fc-v21-x86_64-with-glibc2.39

| ステップ | 結果 | 所要 | 備考 |
|---|---|---|---|
| `site_read` | OK | 562 ms |  |
| `package_search` | OK | 751 ms |  |
| `package_list` | OK | 237 ms |  |
| `organization_list` | OK | 241 ms |  |
| `group_list` | OK | 223 ms |  |
| `tag_list` | OK | 1193 ms |  |
| `package_show` | OK | 586 ms |  |

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
  - 根拠: data.e-gov.go.jp の /info/ja/help と /info/ja/about-site を辿ってもメタデータ項目の仕様へのリンクが無く、API も項目説明を返さない。実測は results/fields.json を参照。
- **データセット画面のメタデータは「e-Govデータポータル標準」と「自治体標準ODS オープンデータ一覧」の 2 系統に分かれ、HTML 上も別クラスで区別されている。**
  - 根拠: データセット画面の tr が metadata_basic_field と metadata_detail_field に分かれており、画面上も「一部表示／全て表示」で切り替えられる。
- **値による突合で付けられる説明の数は実行ごとに変動する。package_search が返すデータセットが毎回同じとは限らず、値が空の項目は突合できないため。**
  - 根拠: 同じスクリプトの連続実行で、説明を付けられた項目数が 22 と 19 に変わった。抽出手法に由来する揺れであり、提供側の変更ではない。
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
- 実測値: /laws の total_count は 9550 件（全法令）

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
- 最終検証: 2026-08-26T01:03:20+00:00
- 再現コマンド: `.work/toolvenv/bin/python verify/verify_egov_hourei.py --out results/egov-hourei-api.json`
- 検証スクリプト: `verify/verify_egov_hourei.py` / 結果: `results/egov-hourei-api.json`
- 検証環境: Python 3.11.15 / Linux-6.18.44-fc-v21-x86_64-with-glibc2.39

| ステップ | 結果 | 所要 | 備考 |
|---|---|---|---|
| `fetch_openapi_spec` | OK | 1291 ms |  |
| `GET /laws（全件数）` | OK | 1395 ms |  |
| `GET /laws` | OK | 488 ms |  |
| `GET /law_revisions/{law_id}` | OK | 467 ms |  |
| `GET /law_data/{law_id}` | OK | 500 ms |  |
| `GET /keyword` | OK | 1813 ms |  |
| `GET /law_file/xml/{law_id}` | OK | 497 ms |  |
| `GET /attachment/{law_revision_id}` | OK | 649 ms |  |

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

## 統計 LOD（SPARQL エンドポイント） (`estat-lod`)

e-Stat の統計データを RDF として公開し、SPARQL 1.1 で照会できるようにしたもの。認証情報は不要で、appId が要る e-Stat API とは別系統。

### 提供と経路

- 提供元: 総務省統計局・独立行政法人統計センター（e-Stat）（権威性: `primary_official`）
- 一次情報: https://data.e-stat.go.jp/lodw/
- 方式: `rest_api` / エンドポイント: `https://data.e-stat.go.jp/lod/sparql/alldata/query`
- 仕様: https://data.e-stat.go.jp/lodw/sparqlendpoint/api

### 提供される情報

- 種類: 政府統計 / 地域コード
- 形式: json / xml / csv / tsv / n-triples
- 更新頻度: undocumented
- 収録範囲: 統計データと地域に関するデータを RDF で提供する。データセット・属性・測度・次元・ カタログ・地域コード・調査項目といった語彙が定義されている。 どの統計が収録されているかは「統計LODで利用可能な統計データ」に一覧がある。

### 接続要件

- 認証: `not_required` — 認証情報なしで SELECT / ASK / CONSTRUCT / DESCRIBE がいずれも応答した。一次資料にも API キーの記述は無い。
- レート制限: undocumented
- 利用規約: https://creativecommons.org/licenses/by/4.0/
- 出典表示: `yes` — 注があるものを除き、サイトの内容物はクリエイティブ・コモンズ 表示 4.0 ライセンスの下に提供される。表示（出典の明示）が条件。

### 安定性（一次資料の記述）

- SPARQL 1.1 に準拠すると一次資料に明記。
- 一次資料が示すエンドポイント URL は http:// だが、https:// でも応答する。

### 到達性

| ホスト | 役割 | 備考 |
|---|---|---|
| `data.e-stat.go.jp` | api | SPARQL エンドポイントと仕様・語彙定義がすべてこのホスト。 |
| `www.e-stat.go.jp` | portal | e-Stat 本体。統計 LOD とは別系統で、API 利用には appId が要る。 |

### 検証

- 状態: **検証済**
- 最終検証: 2026-08-26T01:05:53+00:00
- 再現コマンド: `.work/toolvenv/bin/python verify/verify_estat_lod.py --out results/estat-lod.json`
- 検証スクリプト: `verify/verify_estat_lod.py` / 結果: `results/estat-lod.json`
- 検証環境: Python 3.11.15 / Linux-6.18.44-fc-v21-x86_64-with-glibc2.39

| ステップ | 結果 | 所要 | 備考 |
|---|---|---|---|
| `SELECT (JSON)` | OK | 25031 ms |  |
| `SELECT (CSV)` | OK | 24109 ms |  |
| `SELECT (XML)` | OK | 733 ms |  |
| `ASK` | OK | 9374 ms |  |
| `CONSTRUCT: 出力形式のネゴシエーション` | OK | 25386 ms |  |
| `DESCRIBE: 出力形式のネゴシエーション` | OK | 63125 ms |  |
| `POST での照会` | OK | 842 ms |  |

### 実行して分かったこと

- **CONSTRUCT と DESCRIBE で、一次資料が既定と記す application/rdf+xml と text/turtle はいずれも HTTP 406 で拒否される。仕様の記述と実装が食い違っている。**
  - 根拠: 同一クエリで Accept を変えて実測。application/rdf+xml と text/turtle が 406（text/html の本文 457 バイト）、application/n-triples と text/plain が 200 を返した。
- **CONSTRUCT / DESCRIBE で Accept を付けないと、RDF ではなく application/sparql-results+json が返る。グラフを期待していると型が合わない。**
  - 根拠: Accept ヘッダ無しの CONSTRUCT と DESCRIBE がいずれも Content-Type application/sparql-results+json を返した。
- **DESCRIBE に application/n-triples を指定すると 60 秒でも応答が返らない。形式によって処理の重さが大きく違う。**
  - 根拠: 同じ DESCRIBE クエリで text/plain は 200 を 284 バイトで返すのに対し、application/n-triples は 60 秒タイムアウトした。
- **SELECT は Accept ヘッダで JSON / XML / CSV を切り替えられ、要求した形式がそのまま Content-Type で返る。**
  - 根拠: 同一クエリで application/sparql-results+json、application/sparql-results+xml、text/csv を指定し、いずれも要求どおりの Content-Type で応答した（CSV は "CPI\n100.2\n99.8\n99.8"）。
- **GET と POST の双方で同じ結果を得られる。長いクエリは POST に逃がせる。**
  - 根拠: 同一 SELECT を GET と POST で投げ、いずれも 3 行・変数 CPI の同じ結果が返った。
- **応答に返る変数名は大文字化される。?p を指定しても JSON の binding のキーは "P" になる。小文字で引くと空振りする。**
  - 根拠: select ?p where {{ ?s ?p ?o }} limit 5 の応答が head.vars=["P"]、binding のキーも "P" だった。?s ?p ?o では ["S","P","O"] が返る。
- **グラフ全体に distinct を掛けると返らず、無作為な limit では同じ述語ばかり返る。語彙を調べるには主語を 1 件に絞る必要がある。**
  - 根拠: select distinct ?p where {{ ?s ?p ?o }} は 60 秒でタイムアウト。limit 400 では 400 行すべてが rdf:type だった。統計値 1 件に絞ると 10 種の述語が得られた。
- **利用条件は SPARQL の仕様ページではなくサイト全体のフッターに書かれており、CC BY 4.0 が適用される。**
  - 根拠: https://data.e-stat.go.jp/lodw/ の各ページ末尾に「注があるものを除いて, このサイトの内容物はクリエイティブ・コモンズ 表示 4.0 ライセンスの下に提供されています。」と記載。

## 地理院タイル（国土地理院 XYZ タイル配信） (`gsi-tiles`)

国土地理院が配信するタイル状の地図データ。認証情報は不要で、 URL にズームレベルとタイル座標を埋めて GET するだけで取得できる。 拡張子によって中身の性質が違い、画像（png / jpg）のほかに、 標高値（txt）と点データ（geojson）が同じ規則で配信されている。

### 提供と経路

- 提供元: 国土交通省国土地理院（権威性: `primary_official`）
- 一次情報: https://maps.gsi.go.jp/development/ichiran.html
- 方式: `rest_api` / エンドポイント: `https://cyberjapandata.gsi.go.jp/xyz/{t}/{z}/{x}/{y}.{ext}`
- 仕様: https://maps.gsi.go.jp/development/siyou.html

### 提供される情報

- 種類: 地図 / 空中写真 / 標高 / 防災 / 地理空間情報
- 形式: png / jpg / txt / geojson
- 更新頻度: undocumented。タイル種別ごとの更新頻度は一覧ページに記載が無く、載っているのは 「提供開始」の日付だけ。個々のタイルの更新時期は応答の Last-Modified で判断できる。
- 収録範囲: 配信されているタイルの種類は一覧ページにしか列挙されていない。内訳は画像が大半で、 ベースマップ（標準地図・淡色地図・白地図）、空中写真、標高・土地の凹凸、 土地の成り立ち・土地利用、基準点・地磁気、災害ごとの正射画像などがある。 画像以外では、標高タイル（カンマ区切りの標高値）と、指定緊急避難場所・ 自然災害伝承碑などの点データ（GeoJSON）が同じ URL 規則で取れる。 タイル種別ごとに提供ズームレベルと提供範囲が異なり、範囲外は 404 になる。
- 実測値: 一覧ページに載っている GeoJSON タイルの URL テンプレート 23 件 （画像タイルは災害ごとの正射画像が随時追加されるため件数を追わない）

### 接続要件

- 認証: `not_required` — 認証情報なしで画像・標高・GeoJSON のいずれも 200 で応答した。 一覧ページ・仕様ページのどちらにも API キーにあたる記述は無い。
- レート制限: undocumented
- 利用規約: https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html
- 出典表示: `yes` — 出典は「国土地理院」または「地理院タイル」等と記載し、地理院タイル一覧ページ （https://maps.gsi.go.jp/development/ichiran.html）へのリンクを付ける。

### 安定性（一次資料の記述）

- タイルの URL は「原則として」https://cyberjapandata.gsi.go.jp/xyz/{t}/{z}/{x}/{y}.{ext} と命名されると仕様ページに明記。
- タイル 1 枚の大きさは 256 ピクセル × 256 ピクセルで統一されていると仕様ページに明記。
- 測地系は日本国内の地図については世界測地系（JGD2011）で、北緯・南緯約 85.0511 度以上を除外したメルカトル投影と仕様ページに明記。
- 提供しているズームレベルや範囲は種類により異なるため一覧ページを参照するよう、仕様ページが指示している。
- テキスト形式の標高タイルは令和 6 年 10 月より更新を停止していると一覧ページに明記。
- 標高タイルの PNG 形式は 24 ビットカラー、標高分解能 0.01m、無効値は (R, G, B) = (128, 0, 0) と詳細仕様に明記。

### 到達性

| ホスト | 役割 | 備考 |
|---|---|---|
| `cyberjapandata.gsi.go.jp` | api | タイル本体の配信。画像・標高・GeoJSON がすべてこのホスト。 |
| `maps.gsi.go.jp` | documentation | 一覧ページ・仕様ページ・標高タイルの詳細仕様。何が配信されているかはここにしか無い。 |
| `www.gsi.go.jp` | terms | 国土地理院コンテンツ利用規約の本文。この環境ではプロキシが 403 を返し到達できない。 |

### 検証

- 状態: **検証済**
- 最終検証: 2026-08-26T01:07:47+00:00
- 再現コマンド: `.work/toolvenv/bin/python verify/verify_gsi_tiles.py --out results/gsi-tiles.json`
- 検証スクリプト: `verify/verify_gsi_tiles.py` / 結果: `results/gsi-tiles.json`
- 検証環境: Python 3.11.15 / Linux-6.18.44-fc-v21-x86_64-with-glibc2.39

| ステップ | 結果 | 所要 | 備考 |
|---|---|---|---|
| `一次資料: 地理院タイル一覧` | OK | 865 ms |  |
| `一次資料: 地理院タイルの仕様` | OK | 42 ms |  |
| `一次資料: 標高タイルの詳細仕様` | OK | 43 ms |  |
| `地図タイル: 標準地図 std（ZL14 PNG）` | OK | 335 ms |  |
| `地図タイル: 淡色地図 pale（ZL14 PNG）` | OK | 67 ms |  |
| `地図タイル: 全国最新写真 seamlessphoto（ZL14 JPEG）` | OK | 66 ms |  |
| `標高タイル: DEM5A テキスト形式（ZL14）` | OK | 87 ms |  |
| `標高タイル: DEM5A PNG 形式とテキスト形式の突合（ZL14）` | OK | 257 ms |  |
| `GeoJSON タイル: 指定緊急避難場所 skhb01（ZL10）` | OK | 109 ms |  |
| `GeoJSON タイル: 自然災害伝承碑 disaster_lore_all（ZL7）` | OK | 317 ms |  |
| `提供範囲外・存在しないデータ ID の返り方` | OK | 4530 ms |  |
| `文書化されたズームレベルの外側の返り方` | OK | 3649 ms |  |
| `CORS: Origin 付きリクエスト` | OK | 1157 ms |  |
| `条件付きリクエスト（ETag / Last-Modified）` | OK | 2162 ms |  |
| `利用規約: 国土地理院コンテンツ利用規約` | FAIL | - | 自環境の egress でプロキシが拒否した: 403 Forbidden |

### 実行して分かったこと

- **PNG 形式の標高タイルとテキスト形式の標高タイルの値は一致しない。一次資料は「画素値（RGB値）から算出される標高値は、テキスト形式の標高タイルの標高値と同じになります」と書いているが、実測では大半の画素が食い違う。**
  - 根拠: 同一タイル（dem5a / dem5a_png の 14/14552/6451）の 65,536 画素を突合し、一致 20,045、不一致 45,491、最大差 7.74m。無効値は PNG 側に 7,126 画素あるがテキスト側は 0。なお同じ一覧ページに「テキスト形式の標高タイルは令和6年10月より更新を停止しております」とあるが、それがこの差の原因だとは一次資料に書かれていない。
- **存在しないタイルは 404 で Amazon S3 の NoSuchKey XML が返る。提供範囲外の座標・存在しないデータ ID・提供していない拡張子は、どれも同じ応答なので区別できない。**
  - 根拠: std/14/0/0.png（提供範囲外）、no_such_tileset/14/14552/6451.png（存在しない ID）、std/14/14552/6451.geojson（提供していない拡張子）がいずれも 404・application/xml・<Code>NoSuchKey</Code> を返した。
- **標準地図は一覧ページが ZL2〜18 しか記載していないが、ZL0 と ZL1 も 200 で画像を返す。記載が無いことは提供していないことを意味しない。**
  - 根拠: std/0/0/0.png が 200・image/png・77,992 バイト、std/1/1/0.png が 200・76,255 バイト。ZL19（std/19/465694/206453.png）は 404 NoSuchKey。
- **CORS 応答ヘッダは Origin ヘッダを付けたときだけ返る。付けずに叩いて Access-Control-Allow-Origin が無いことを、ブラウザから使えない根拠にしてはいけない。**
  - 根拠: 同じ URL に対し、Origin 無しでは Access-Control-Allow-Origin が返らず、Origin ヘッダに https://example.com を与えると `*` が返った。
- **ETag と Last-Modified が付き、If-None-Match と If-Modified-Since のどちらでも 304 が返る。タイルは枚数が多いので、再取得を条件付きリクエストで避けられる。**
  - 根拠: std/14/14552/6451.png の ETag と Last-Modified をそのまま送り返し、いずれも 304・本文 0 バイト。Server ヘッダは AmazonS3。
- **.geojson の Content-Type は application/json ではなく application/octet-stream。形式は Content-Type ではなく拡張子でしか判別できない。**
  - 根拠: skhb01 と disaster_lore_all のどちらも application/octet-stream で返った。テキスト形式の標高タイル（.txt）は text/plain。
- **GeoJSON タイルは提供ズームレベルが 1 つに固定されており、そこから外れると 404 になる。地図タイルと同じ感覚でズームレベルを選ぶと空振りする。**
  - 根拠: skhb01 は ZL10、disaster_lore_all は ZL7 が一覧ページの記載で、その ZL では 200（それぞれ 1,195 件・536 件のフィーチャ）。同じ地点の ZL14 ではどちらも 404 NoSuchKey だった。
- **GeoJSON のプロパティのキーはフィーチャごとに異なる。先頭の 1 件だけを見て項目を決めると取りこぼす。**
  - 根拠: skhb01（ZL10）の先頭フィーチャは name / address / remarks / disaster1 / disaster7 の 5 キーだが、1,195 件を通すと disaster1〜disaster8 が出そろい 11 キーになった。該当する災害種別のキーだけが入る作りになっている。
- **利用規約の本文があるホスト www.gsi.go.jp には、この環境からは到達できない。プロキシが 403 を返しており、先方の障害ではない。**
  - 根拠: https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html への GET が httpx.ProxyError（403 Forbidden）。同じ検証の中で maps.gsi.go.jp と cyberjapandata.gsi.go.jp には到達できている。

## Jグランツ MCP Server (`jgrants-mcp`)

デジタル庁が運用する補助金電子申請システム「Jグランツ」の公開 API を、デジタル庁自身が MCP サーバーとして実装したもの。

### 提供と経路

- 提供元: デジタル庁（権威性: `official_wrapper`）
- 一次情報: https://www.jgrants-portal.go.jp/
- 方式: `mcp` / エンドポイント: `http://127.0.0.1:8000/mcp`
- 仕様: https://files.microcms-assets.io/assets/7c793323a46a46b7bb9a2ac7d0023301/2bad5ef79255448f8381d9cf2a14dbfc/jgrants-api.yaml
- 実装: digital-go-jp/jgrants-mcp-server（保守: デジタル庁 / MIT / 検証時 2.0.0）

### 提供される情報

- 種類: 補助金・助成金
- 形式: json / markdown / pdf / docx / csv
- 更新頻度: undocumented
- 収録範囲: 募集中・募集予定の補助金が対象。過去の募集は含まれない。件数は募集の開始と締切で 日々変わるため台帳に書かない（実測は results/jgrants-mcp.json の call:get_subsidy_overview を参照）。

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
| `files.microcms-assets.io` | spec | 公式 OpenAPI 仕様 jgrants-api.yaml の実体。政府ドメインではない CDN のため許可リストから漏れやすい。到達できないと項目の説明が埋まらない。 |

### 検証

- 状態: **検証済**
- 最終検証: 2026-08-26T01:08:15+00:00
- 再現コマンド: `./verify/run_jgrants_verification.sh`
- 検証スクリプト: `verify/verify_jgrants_mcp.py` / 結果: `results/jgrants-mcp.json`
- 検証環境: Python 3.11.15 / Linux-6.18.44-fc-v21-x86_64-with-glibc2.39

| ステップ | 結果 | 所要 | 備考 |
|---|---|---|---|
| `initialize` | OK | 0 ms |  |
| `list_tools` | OK | 20 ms |  |
| `list_resources` | OK | 8 ms |  |
| `list_prompts` | OK | 7 ms |  |
| `call:ping` | OK | 11 ms |  |
| `call:search_subsidies` | OK | 995 ms |  |
| `call:get_subsidy_detail` | OK | 210 ms |  |
| `call:get_subsidy_overview` | OK | 1702 ms |  |
| `call:get_file_content` | OK | 2401 ms |  |

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
- **公式 OpenAPI 仕様 jgrants-api.yaml は developers.digital.go.jp ではなく microCMS のアセット CDN（files.microcms-assets.io）にホストされている。政府ドメインだけを許可しても到達できない。**
  - 根拠: 仕様ページの HTML 内リンクが https://files.microcms-assets.io/assets/.../jgrants-api.yaml を指しており、当該ホストは当初プロキシに 403 で拒否されていた。許可追加後に HTTP 200 で 39,919 バイトを取得できた。
- **ベース URL の /exp/ は公式仕様に含まれる。MCP サーバーが叩く https://api.jgrants-portal.go.jp/exp/v1/public は仕様どおりであって、実験版を独自に叩いているわけではない。**
  - 根拠: 公式仕様の servers[0].url が https://api.jgrants-portal.go.jp/exp で、paths が /v1/public/subsidies などの相対パスになっている。
- **公式仕様にも securitySchemes とレート制限の定義が無い。認証要否とレート制限が未記載なのは、ドキュメントページだけの問題ではない。**
  - 根拠: jgrants-api.yaml 全文に securitySchemes / security の記述が無く、「制限」「回数」「レート」「利用規約」「出典」のいずれの語も出現しないことを確認。
- **補助金詳細の API には v1 と v2 があり、返す項目数が違う（v1 は 22 項目、v2 は 19 項目）。MCP サーバーが使うのは v1。**
  - 根拠: 公式仕様の paths に /v1/public/subsidies/id/{id} と /v2/public/subsidies/id/{id} があり、schemas の type_1（22 プロパティ）と type_1_v2（19 プロパティ）に対応している。
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
- 最終検証: 2026-08-26T01:08:04+00:00
- 再現コマンド: `.work/toolvenv/bin/python verify/verify_jma_xml.py --out results/jma-xml.json`
- 検証スクリプト: `verify/verify_jma_xml.py` / 結果: `results/jma-xml.json`
- 検証環境: Python 3.11.15 / Linux-6.18.44-fc-v21-x86_64-with-glibc2.39

| ステップ | 結果 | 所要 | 備考 |
|---|---|---|---|
| `GET /regular.xml (定時・高頻度)` | OK | 1937 ms |  |
| `GET /extra.xml (随時・高頻度)` | OK | 1480 ms |  |
| `GET /eqvol.xml (地震火山・高頻度)` | OK | 820 ms |  |
| `GET /other.xml (その他・高頻度)` | OK | 813 ms |  |
| `GET /regular_l.xml (定時・長期)` | OK | 2817 ms |  |
| `GET /extra_l.xml (随時・長期)` | OK | 2714 ms |  |
| `GET /eqvol_l.xml (地震火山・長期)` | OK | 1701 ms |  |
| `GET /other_l.xml (その他・長期)` | OK | 1459 ms |  |
| `GET 電文本体` | OK | 2168 ms |  |

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

## 国立国会図書館サーチ 外部提供インタフェース (`ndl-search`)

国立国会図書館サーチが収録する書誌メタデータを、検索用 3 経路（SRU / OpenSearch / OpenURL）とハーベスト用 1 経路（OAI-PMH）で提供する。認証情報は不要。

### 提供と経路

- 提供元: 国立国会図書館（権威性: `primary_official`）
- 一次情報: https://ndlsearch.ndl.go.jp/help/api
- 方式: `rest_api` / エンドポイント: `https://ndlsearch.ndl.go.jp/api`
- 仕様: https://ndlsearch.ndl.go.jp/help/api/specifications

### 提供される情報

- 種類: 書誌メタデータ / 図書館蔵書
- 形式: xml / rss / html
- 更新頻度: undocumented
- 収録範囲: NDLサーチが収録し、かつ提供機関から許諾が得られたメタデータ。データ提供機関ごとに 利用条件が異なる。OAI-PMH のセット単位で提供元を絞り込める。
- 実測値: OAI-PMH の ListSets が返すセット数は 474
- 実測値: OAI-PMH の earliestDatestamp は 2022-10-01T00:00:00Z

### 接続要件

- 認証: `not_required` — 認証情報なしで 4 経路すべてが応答した。一次資料にも API キーの記述は無い。利用申請は営利目的かどうかで要否が決まる手続きであって、技術的な資格情報ではない。
- レート制限: 同時リクエスト数に制限があり、特定のサーバから継続して大量のアクセスがある場合はアクセスを遮断する等の措置を行うと一次資料に明記。具体的な上限値は非公開。
- 利用規約: https://ndlsearch.ndl.go.jp/help/api
- 出典表示: `undocumented`

### 安定性（一次資料の記述）

- SRW と Z39.50 は 2020 年 3 月 2 日をもってサービス終了と一次資料に明記。
- 機能の一部でキャッシュを用いているため、リクエスト条件やタイミングによって応答性能が大きく変わる場合があると明記。
- メタデータは「国立国会図書館ダブリンコアメタデータ記述（DC-NDL）」に従うと明記。

### 到達性

| ホスト | 役割 | 備考 |
|---|---|---|
| `ndlsearch.ndl.go.jp` | api | API・仕様書・利用条件のすべてがこのホスト。 |

### 検証

- 状態: **検証済**
- 最終検証: 2026-08-26T01:07:20+00:00
- 再現コマンド: `.work/toolvenv/bin/python verify/verify_ndl_search.py --out results/ndl-search.json`
- 検証スクリプト: `verify/verify_ndl_search.py` / 結果: `results/ndl-search.json`
- 検証環境: Python 3.11.15 / Linux-6.18.44-fc-v21-x86_64-with-glibc2.39

| ステップ | 結果 | 所要 | 備考 |
|---|---|---|---|
| `SRU: explain` | OK | 1489 ms |  |
| `SRU: searchRetrieve` | OK | 16506 ms |  |
| `OpenSearch: 検索` | OK | 27025 ms |  |
| `OpenURL: 検索` | OK | 1075 ms |  |
| `OAI-PMH: Identify` | OK | 813 ms |  |
| `OAI-PMH: ListMetadataFormats` | OK | 799 ms |  |
| `OAI-PMH: ListSets` | OK | 9086 ms |  |

### 実行して分かったこと

- **SRU は operation=explain に対応していない。explain を指定すると HTTP 200 だが searchRetrieveResponse に診断が入って返る。**
  - 根拠: /api/sru?operation=explain の応答が root=searchRetrieveResponse、diagnostics に uri=info:srw/diagnostic/1/1、message="operation is not searchRetrieve" を含んでいた。
- **仕様に載る /api/openurl は画面側の /openurl へ 301 リダイレクトされ、クエリ名も au から q-au に書き換わる。リダイレクトを追わないと 301 で止まる。**
  - 根拠: /api/openurl?au=夏目漱石 が https://ndlsearch.ndl.go.jp/openurl?cs=api_openurl&q-au=夏目漱石 へ 301 した。追従すると HTTP 200・text/html を返す。
- **OpenURL が返すのは HTML であり、機械可読な経路ではない。機械処理には SRU か OpenSearch を使う。**
  - 根拠: 追従後の Content-Type が text/html;charset=utf-8 で 379,286 バイトの画面が返った。
- **レート制限は実在し、連続実行すると 429 Too Many Requests が返る。一次資料が上限値を公開していないため、実測でしか分からない。**
  - 根拠: 間隔を空けずに検証を 2 回続けたところ、SRU・OpenSearch・OAI-PMH が 429 を返した。5 秒間隔と 429 時 30 秒待機の再試行を入れて解消した。
- **OAI-PMH の deletedRecord は persistent で、削除されたレコードの情報が保持される。差分ハーベストで削除を追える。**
  - 根拠: Identify の応答に deletedRecord=persistent、granularity=YYYY-MM-DDThh:mm:ssZ、protocolVersion=Version 2.0 が含まれていた。
- **OpenSearch は RSS で返り、item に title / link / author / category / pubDate に加えて titleTranscription（読み）が入る。**
  - 根拠: /api/opensearch の応答が rss ルートで、channel に totalResults / startIndex / itemsPerPage、item に titleTranscription を含んでいた。

## 候補（未登録）

調べたが、まだ検証していない情報源。**何を提供するかは書かない** —
一次資料に当たる前に書けるのは名前とホストと調べた理由だけで、それ以外は推測になる。
実体は `registry/candidates.yaml`。

- 候補 9 件
- **いま着手できるもの: 3 件**（到達でき、認証待ちでもない）

| 候補 | 保留の理由 | ホストへの到達 |
|---|---|---|
| **e-Stat API（政府統計の総合窓口）** (`estat-api`) | 認証情報が無い | 可 |
| **J-STAGE** (`jstage`) | 到達できない（自環境の egress） | **不可** |
| **法人番号システム Web-API（国税庁）** (`houjin-bangou`) | 到達できない（自環境の egress） | **不可** |
| **不動産情報ライブラリ（国土交通省）** (`reinfolib`) | 認証情報が無い | 可 |
| **国土数値情報（国土交通省）** (`nlftp-mlit`) | 未着手 | 可 |
| **官報** (`kanpo`) | 未着手 | 可 |
| **特許庁 IP Data** (`jpo-ip-data`) | 認証情報が無い | 可 |
| **医療機関等情報提供制度（厚生労働省）** (`iryou-teikyou`) | 未着手 | 可 |
| **国土交通データプラットフォーム（国土交通 DPF 利用者 API）** (`mlit-data`) | 到達できない（自環境の egress） | **不可** |

### e-Stat API（政府統計の総合窓口） (`estat-api`)

- 保留の理由: 認証情報が無い
- 調べた理由: 政府統計を扱うなら最初に当たる情報源のため。
- 対象ホスト: `api.e-stat.go.jp`, `www.e-stat.go.jp`（到達可）
- 詳細: 利用には appId が必要で、まだ取得していない。ホストには到達できるので 一次資料（API 仕様）は読めるが、実際に叩いて確かめることができない。 検証できないものは台帳に載せないという原則により、ここで保留する。 なお統計 LOD（estat-lod）は同じ e-Stat でも appId を要求しない別経路で、 そちらは認証情報を待たずに検証できる。
- 次の一手: appId を取得したうえで、公開されている各エンドポイントを検証する。

### J-STAGE (`jstage`)

- 保留の理由: 到達できない（自環境の egress）
- 調べた理由: 学術論文の書誌・全文を扱う公的な情報源として。
- 対象ホスト: `www.jstage.jst.go.jp`, `api.jstage.jst.go.jp`（到達不可）
- 詳細: 一次資料は読めたが、API ホストに到達できない。公式マニュアル https://www.jstage.jst.go.jp/static/files/ja/manual_api.pdf （Ver.2.0、 2026-03-26）がリクエスト先を https://api.jstage.jst.go.jp/searchapi/do と明示しており、そのホストへの GET はプロキシが 403（httpx の ProxyError） を返す。閲覧側の www.jstage.jst.go.jp には到達できるため、 これは先方の障害ではなく自環境の egress。 認証情報は不要と一次資料で確認した。利用規約第 2 条は 「非営利目的で利用するときは、JST への利用申請は不要」とし、 営利目的のときだけ申請書の提出を求めている。マニュアルにも API キーに あたるパラメータは無い。
- 次の一手: api.jstage.jst.go.jp を egress の許可リストに追加してもらう。通ったら 巻号一覧・記事検索・資料検索の 3 機能を検証する。

### 法人番号システム Web-API（国税庁） (`houjin-bangou`)

- 保留の理由: 到達できない（自環境の egress）
- 調べた理由: 法人の名寄せに使える公的な識別子として。
- 対象ホスト: `api.houjin-bangou.nta.go.jp`, `www.houjin-bangou.nta.go.jp`（到達不可）
- 詳細: 認証要否を確定できなかった。仕様が置かれている www.houjin-bangou.nta.go.jp への GET はプロキシが 403（ProxyError）を 返し、一次資料に到達できない。API ホスト api.houjin-bangou.nta.go.jp 自体には到達できるが、パスの当てずっぽう（/4/num、/4/name、/4/diff を id 有り・無しで）はすべて Apache の 404 Not Found を返しただけで、 これは「認証が要る」根拠にも「エンドポイントが無い」根拠にもならない。 一次資料を読まずに認証要否を書くことはしない。
- 次の一手: www.houjin-bangou.nta.go.jp を egress の許可リストに追加してもらい、 仕様書を読んでからエンドポイントと認証要否を確定する。

### 不動産情報ライブラリ（国土交通省） (`reinfolib`)

- 保留の理由: 認証情報が無い
- 調べた理由: 不動産取引価格などを扱う情報源として。
- 対象ホスト: `www.reinfolib.mlit.go.jp`（到達可）
- 詳細: API キーが必要と実測で確認した。キー無しで https://www.reinfolib.mlit.go.jp/ex-api/external/XIT001 を叩くと HTTP 401 と {"statusCode":401,"message":"Access denied due to missing subscription key. ..."} が返る。一次資料 https://www.reinfolib.mlit.go.jp/help/apiManual/ も、API 利用規約に 同意して利用申請したうえで、発行された API キーを Ocp-Apim-Subscription-Key リクエストヘッダーに設定するよう求めている。 申請はユーザー作業。
- 次の一手: API キーを取得する。取得できたら credential_env に環境変数名だけを書き、 各エンドポイントを検証する。

### 国土数値情報（国土交通省） (`nlftp-mlit`)

- 保留の理由: 未着手
- 調べた理由: 地理空間の統計データを扱う情報源として。
- 対象ホスト: `nlftp.mlit.go.jp`（到達可）
- 詳細: 認証は不要と実測で確認した。データセットページ https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html が 示す実ファイル https://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2026/N03-20260101_GML.zip に Range ヘッダ付きで GET したところ、認証情報なしで HTTP 206・ application/zip・Content-Range の総サイズ 803201348 が返った。 なお API については、トップ（/ksj/）と /ksj/first.html、データセット ページのいずれにも案内が見当たらず、ダウンロード導線はすべて zip への 直リンクだった。API があるともないとも一次資料が言っていないので undocumented 扱いとし、検証対象はファイル配布経路とする。
- 次の一手: 検証対象のデータセットを絞り（まず N03 行政区域）、ダウンロード URL の 規則性と利用約款を一次資料で確認してエントリを起こす。巨大な zip を 毎回落とさずに済むよう、検証は Range で先頭だけを取る。

### 官報 (`kanpo`)

- 保留の理由: 未着手
- 調べた理由: 法令の公布や公示を一次で追える情報源として。
- 対象ホスト: `www.kanpo.go.jp`（到達可）
- 詳細: 認証は不要と実測で確認した。日付別の全体目次 https://www.kanpo.go.jp/20260821/20260821.fullcontents.html が 認証情報なしで HTTP 200・HTML を返し、本文の目次が読めた。 機械可読な提供経路（API・XML・JSON）は、トップと目次ページのリンクを 見たかぎり見当たらず、日付とページで組み立てる HTML と PDF のみだった。 候補に挙げていた notice.go.jp は官報とは無関係のサイト（IoT 機器の セキュリティ啓発サイト NOTICE）だったので hosts から外した。
- 次の一手: /ご利用に当たって（guidance.html）で転載・再利用の条件を確認する。 機械可読な経路が本当に無いなら、HTML の目次構造をどこまで安定した インタフェースとみなせるかを判断してから、エントリにするか決める。

### 特許庁 IP Data (`jpo-ip-data`)

- 保留の理由: 認証情報が無い
- 調べた理由: 産業財産権の情報を扱う情報源として。
- 対象ホスト: `ip-data.jpo.go.jp`（到達可）
- 詳細: ID・パスワードが必要と実測で確認した。トークン無しで https://ip-data.jpo.go.jp/api/patent/v1/app_progress/2020000001 を叩くと HTTP 401 と {"result":{"statusCode":"210","errorMessage":"無効な トークンです。",...}} が返る。一次資料 https://ip-data.jpo.go.jp/files/アクセス方法.pdf は、利用登録時に通知 される URL へ grant_type=password と特許庁発行の ID・パスワードを POST してアクセストークン（有効期間 1 時間）を取得し、 Authorization: Bearer で各 API を呼ぶ手順を示している。 利用登録はユーザー作業。 なお OpenAPI 仕様 https://ip-data.jpo.go.jp/api_guide/api_reference.js （42 パス）には securitySchemes の記述が無く、認証の記述は仕様ではなく 別 PDF にある。仕様に securitySchemes が無いことは認証不要の根拠に ならない例。
- 次の一手: 利用登録して ID・パスワードを取得する。取得できたらトークン取得から 各 API までを検証する。アクセス数に日次上限がある点も記録する。

### 医療機関等情報提供制度（厚生労働省） (`iryou-teikyou`)

- 保留の理由: 未着手
- 調べた理由: 医療機関の所在や機能を扱う情報源として。
- 対象ホスト: `www.iryou.teikyouseido.mhlw.go.jp`（到達可）
- 詳細: 認証は不要と実測で確認した。トップ https://www.iryou.teikyouseido.mhlw.go.jp/znk-web/juminkanja/S2300/initialize が認証情報なしで HTTP 200・HTML を返した。 ただし機械可読な提供経路は見当たらない。トップのリンクはすべて画面遷移 （/znk-web/juminkanja/S____/initialize）で、CSV・オープンデータ・ 一括ダウンロードへの導線は無かった。
- 次の一手: 検索画面の遷移がクエリで表現できるか、あるいは都道府県ごとの オープンデータが別のホストで公開されていないかを一次資料で確認する。 機械可読な経路が無いなら候補から外す判断も含めて決める。

### 国土交通データプラットフォーム（国土交通 DPF 利用者 API） (`mlit-data`)

- 保留の理由: 到達できない（自環境の egress）
- 調べた理由: RESAS API の提供終了案内が、代替として利用できるサイトの筆頭に 挙げていたため。
- 対象ホスト: `www.mlit-data.jp`（到達不可）
- 詳細: https://www.mlit-data.jp/api_docs/ への GET はプロキシが 403 （ProxyError）を返し、一次資料に到達できない。先方の障害ではなく 自環境の egress。到達できない以上、何を提供するかも認証要否も書かない。
- 次の一手: www.mlit-data.jp を egress の許可リストに追加してもらい、 API 仕様を読んで認証要否を確定する。


## 調査済み・対象外

調べた結果、台帳の対象にならないと分かったもの。**候補には数えない**。
記録を消すと次に同じ調査が繰り返されるので、判断の根拠つきで残す。
実体は `registry/candidates.yaml` の `retired:`。

### RESAS API（地域経済分析システム） (`resas`)

- 調べた理由: 地域経済の統計を扱う情報源として調べた。
- 対象ホスト: `opendata.resas-portal.go.jp`
- 対象外とした理由: 提供が終了している。一次資料 https://opendata.resas-portal.go.jp/docs/api/v1/index.html が 「RESAS API は、2025年3月24日（月）をもって、提供を終了することと なりました」「2024年10月31日（木）をもちまして、RESAS API ページにて 新たにアカウントを作成する機能を終了いたします」「2025年3月24日以降は 自動的にアカウントが削除され、API 機能のご利用を停止いたします」と 明記している。実測でも https://opendata.resas-portal.go.jp/api/v1/prefectures が HTTP 404 と HTML を返し、API として応答しない。到達できないから終了と解釈したのでは なく、提供元が終了を明記している。
- 代替として案内されているもの: 同じ案内が代替として挙げているのは、国土交通データプラットフォーム 利用者 API（候補 mlit-data）、不動産情報ライブラリ（候補 reinfolib）、 e-Stat API（候補 estat-api）。


## 到達性の実測

`verify/verify_reachability.py` の実測結果（2026-08-26T01:03:12+00:00）。
到達できないことは、そのサービスが存在しないことを意味しない。

| ホスト | 結果 | 詳細 |
|---|---|---|
| `api.e-stat.go.jp` | 到達可 | HTTP 403 |
| `api.houjin-bangou.nta.go.jp` | 到達可 | HTTP 404 |
| `api.jgrants-portal.go.jp` | 到達可 | HTTP 404 |
| `api.jstage.jst.go.jp` | egress で拒否 | プロキシが拒否: 403 Forbidden |
| `cyberjapandata.gsi.go.jp` | 到達可 | HTTP 200 |
| `data.e-gov.go.jp` | 到達可 | HTTP 301 |
| `data.e-stat.go.jp` | 到達可 | HTTP 301 |
| `developers.digital.go.jp` | 到達可 | HTTP 200 |
| `files.microcms-assets.io` | 到達可 | HTTP 403 |
| `housyasen.env.go.jp` | 到達可 | HTTP 200 |
| `ikilog.biodic.go.jp` | 到達可 | HTTP 200 |
| `ip-data.jpo.go.jp` | 到達可 | HTTP 302 |
| `laws.e-gov.go.jp` | 到達可 | HTTP 200 |
| `maps.gsi.go.jp` | 到達可 | HTTP 200 |
| `ndlsearch.ndl.go.jp` | 到達可 | HTTP 200 |
| `nlftp.mlit.go.jp` | 到達可 | HTTP 200 |
| `notice.go.jp` | 到達可 | HTTP 200 |
| `saigai.gsi.go.jp` | 到達可 | HTTP 200 |
| `warp.ndl.go.jp` | 到達可 | HTTP 200 |
| `www.bb.mof.go.jp` | 到達可 | HTTP 301 |
| `www.data.go.jp` | 到達可 | HTTP 301 |
| `www.data.jma.go.jp` | 到達可 | HTTP 200 |
| `www.digital.go.jp` | 到達可 | HTTP 200 |
| `www.e-gov.go.jp` | 到達可 | HTTP 403 |
| `www.e-stat.go.jp` | 到達可 | HTTP 200 |
| `www.esri.cao.go.jp` | 到達可 | HTTP 200 |
| `www.gsi.go.jp` | egress で拒否 | プロキシが拒否: 403 Forbidden |
| `www.hokoukukan.go.jp` | 到達可 | HTTP 403 |
| `www.houjin-bangou.nta.go.jp` | egress で拒否 | プロキシが拒否: 403 Forbidden |
| `www.iryou.teikyouseido.mhlw.go.jp` | 到達可 | HTTP 301 |
| `www.jgrants-portal.go.jp` | 到達可 | HTTP 200 |
| `www.jinji.go.jp` | 到達可 | HTTP 200 |
| `www.jma.go.jp` | 到達可 | HTTP 302 |
| `www.jstage.jst.go.jp` | 到達可 | HTTP 200 |
| `www.kanpo.go.jp` | 到達可 | HTTP 200 |
| `www.kodokensaku.mlit.go.jp` | 到達可 | HTTP 200 |
| `www.maff.go.jp` | 到達可 | HTTP 200 |
| `www.mext.go.jp` | 到達可 | HTTP 200 |
| `www.mlit-data.jp` | egress で拒否 | プロキシが拒否: 403 Forbidden |
| `www.mofa.go.jp` | 到達可 | HTTP 403 |
| `www.npa.go.jp` | 到達可 | HTTP 200 |
| `www.reinfolib.mlit.go.jp` | 到達可 | HTTP 200 |
| `www.rinya.maff.go.jp` | 到達可 | HTTP 200 |
| `www.soumu.go.jp` | 到達可 | HTTP 200 |
| `www5.cao.go.jp` | 到達可 | HTTP 200 |
| `www8.cao.go.jp` | 到達可 | HTTP 200 |
| `xml.kishou.go.jp` | 到達可 | HTTP 200 |
