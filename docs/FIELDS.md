# 取得できる項目の一覧

**このファイルは `registry/build.py` が `results/fields.json` から生成する。**
更新するには `verify/extract_fields.py` を実行してからビルドし直す。

- 生成日時: 2026-08-26T01:09:29+00:00

項目の出所は情報源ごとに違う。**仕様由来**は提供側が定義した正式な項目、
**実データ由来**はレスポンスを実際に読んで列挙したもので、サンプルに現れなかった
項目は落ちている可能性がある。どちらなのかを各節の冒頭に示す。

説明と例はすべて提供側の資料から引いたもので、こちらで補ったものは無い。
説明が空欄の項目は、提供側が定義を公開していないか、まだ見つけられていないもの。


## e-Gov 法令 API Version 2 (`egov-hourei-api`)

- 出所: 仕様由来（提供側が定義した正式な項目）
- 抽出方法: OpenAPI 2.1.139 の components/schemas。説明・例・取りうる値はすべて仕様に書かれているもの
- 参照元: https://laws.e-gov.go.jp/api/2/swagger-ui/lawapi-v2.yaml

### attached_file

添付ファイル情報

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `law_revision_id` | string | 法令ID | `322CO0000000016_20230508_505CO0000000175` |
| `src` | string | 法令XML中のFig要素のsrc属性 | `./pict/M06SE065-001.jpg` |
| `updated` | string | 正誤等による更新日時 | `2023-07-01 14:30:15+09:00` |

### attached_files_info

添付ファイル情報

| 項目 | 型 | 説明 |
|---|---|---|
| `image_data` | string | 添付ファイルデータ（添付ファイルをフォルダ名pictに収集し、フォルダ全体をZip形式で圧縮したファイルをBase64でエンコードした文字列） |
| `attached_files` | attached_file[] | 添付ファイル一覧 |

### error_info

エラー情報

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `code` | string | エラーコード | `400001` |
| `message` | string | エラーメッセージ | `法令種別（law_type、law_num_type）が誤っています。` |

### keyword_response

キーワード検索APIレスポンス

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `total_count` | integer | 指定`keyword`でヒットした総件数 | `10000` |
| `sentence_count` | integer | レスポンス単位で表示した`sentences`数の総和 | `100` |
| `next_offset` | integer | 次指定する`offset`値。末尾まで取得が完了した場合はnull | `200` |
| `items` | object[] | 法令ID単位の情報リスト * `revision_info` - 指定時点において効力を持つ版のメタ情報 |  |

### law_data_response

法令本文取得APIレスポンス

| 項目 | 型 | 説明 |
|---|---|---|
| `attached_files_info` | attached_files_info |  |
| `law_info` | law_info |  |
| `revision_info` | revision_info |  |
| `law_full_text` | object | 法令本文 * `law_full_text_format`と`response_format`の指定方法によって、レスポンス形式が変化します。 * データ構造の詳細は法令データ ドキュメンテーションを参照してください。 * JSON（詳細版）形式、JSON（簡易版）形式とXML形式の各要素は、丸数字で対応関係を表現しています。 * JSON（詳細版）形式では、`children`オブジェクトでXML形式の階層構造を表現しています。 |

### law_info

履歴に依存しない法令（法令IDで特定される法令）のメタ情報

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `law_type` | law_type | 法令種別 |  |
| `law_id` | string | 法令ID | `322CO0000000016` |
| `law_num` | string | 法令番号 | `昭和二十二年政令第十六号` |
| `law_num_era` | law_num_era | 法令番号の元号 |  |
| `law_num_year` | integer | 法令番号の年 | `5` |
| `law_num_type` | law_num_type | 法令番号の法令種別 |  |
| `law_num_num` | string | 法令番号の号数 | `192` |
| `promulgation_date` | string | 公布日 | `2023-07-01` |

### law_revisions_response

法令履歴一覧取得APIレスポンス

| 項目 | 型 | 説明 |
|---|---|---|
| `law_info` | law_info |  |
| `revisions` | revision_info[] | 版一覧 |

### laws_response

法令一覧取得API レスポンス

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `total_count` | integer | 取得件数の上限（`limit`）、何件目から取得するか（`offset`）適用前のリストに含まれる項目数（検索条件にマッチした全件数） | `10000` |
| `count` | integer | 返却するリスト（取得件数の上限（`limit`）、何件目から取得するか（`offset`）適用後）に含まれる項目数 | `100` |
| `next_offset` | integer | 次の何件目から取得するか（`offset`）。末尾まで取得が完了した場合はnull | `200` |
| `laws` | object[] | 法令ID単位の法令情報 |  |

### revision_info

法令の履歴に関する情報

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `law_revision_id` | string | 法令履歴ID | `322CO0000000016_20230508_505CO0000000175` |
| `law_type` | law_type | 法令種別 |  |
| `law_title` | string | 法令名 | `地方自治法施行令` |
| `law_title_kana` | string | 法令名読み | `ちほうじちほうせこうれい` |
| `abbrev` | string | 法令略称 | `地方自治令` |
| `category` | string | 法令分野分類 | `行政組織` |
| `updated` | string | 正誤等による更新日時 | `2023-07-01 14:30:15+09:00` |
| `amendment_promulgate_date` | string | 改正法令公布日 | `2023-07-01` |
| `amendment_enforcement_date` | string | 改正法令施行期日（この履歴に対応する改正の施行期日） | `2023-07-01` |
| `amendment_enforcement_comment` | string | 施行期日規定等の参考情報（この履歴に対応する改正の施行期日） | `公布の日から起算して一年を超えない範囲内において政令で定める日` |
| `amendment_scheduled_enforcement_date` | string | 擬似的な施行期日（実際の施行期日とは限らない）（この履歴に対応する改正の施行期日） | `2023-07-01` |
| `amendment_law_id` | string | 改正法令の法令ID（この履歴に対応する改正法令） | `505CO0000000175` |
| `amendment_law_title` | string | 改正法令名 | `組織的な犯罪の処罰及び犯罪収益の規制等に関する法律等の一部を改正する法律` |
| `amendment_law_title_kana` | string | 改正法令名読み | `そしきてきなはんざいのしょばつおよび` |
| `amendment_law_num` | string | 改正法令番号 | `令和五年政令百九十二号` |
| `amendment_type` | amendment_type | 改正種別 |  |
| `repeal_status` | repeal_status | 廃止等の状態 |  |
| `repeal_date` | string | 廃止日 | `2023-07-01` |
| `remain_in_force` | boolean | 廃止後の効力（`true`:廃止後でも効力を有するもの / `false`:廃止後に効力を有しないもの） |  |
| `mission` | mission | 新規制定又は被改正法令（`New`）・一部改正法令（`Partial`） |  |
| `current_revision_status` | current_revision_status | 履歴の状態 |  |

### 取りうる値: `amendment_type — 改正種別`

| 値 | 意味 |
|---|---|
| `1` | 新規 |
| `3` | 被改正 |
| `8` | 廃止 |

### 取りうる値: `category_cd — 事項別分類コード`

| 値 | 意味 |
|---|---|
| `001` | 憲法 |
| `002` | 刑事 |
| `003` | 財務通則 |
| `004` | 水産業 |
| `005` | 観光 |
| `006` | 国会 |
| `007` | 警察 |
| `008` | 国有財産 |
| `009` | 鉱業 |
| `010` | 郵務 |
| `011` | 行政組織 |
| `012` | 消防 |
| `013` | 国税 |
| `014` | 工業 |
| `015` | 電気通信 |
| `016` | 国家公務員 |
| `017` | 国土開発 |
| `018` | 事業 |
| `019` | 商業 |
| `020` | 労働 |
| `021` | 行政手続 |
| `022` | 土地 |
| `023` | 国債 |
| `024` | 金融・保険 |
| `025` | 環境保全 |
| `026` | 統計 |
| `027` | 都市計画 |
| `028` | 教育 |
| `029` | 外国為替・貿易 |
| `030` | 厚生 |
| `031` | 地方自治 |
| `032` | 道路 |
| `033` | 文化 |
| `034` | 陸運 |
| `035` | 社会福祉 |
| `036` | 地方財政 |
| `037` | 河川 |
| `038` | 産業通則 |
| `039` | 海運 |
| `040` | 社会保険 |
| `041` | 司法 |
| `042` | 災害対策 |
| `043` | 農業 |
| `044` | 航空 |
| `045` | 防衛 |
| `046` | 民事 |
| `047` | 建築・住宅 |
| `048` | 林業 |
| `049` | 貨物運送 |
| `050` | 外事 |

### 取りうる値: `current_revision_status — 履歴の状態`

| 値 | 意味 |
|---|---|
| `CurrentEnforced` | 現施行法令 |
| `UnEnforced` | 未施行法令 |
| `PreviousEnforced` | 過去施行法令 |
| `Repeal` | 廃止法令（廃止・失効・実効性喪失） |

### 取りうる値: `file_type — ファイル種別`

| 値 | 意味 |
|---|---|
| `xml` | XML |
| `json` | JSON |
| `html` | HTML |
| `rtf` | RTF |
| `docx` | DOCX |

### 取りうる値: `law_num_era — 法令番号の元号`

| 値 | 意味 |
|---|---|
| `Meiji` |  |
| `Taisho` |  |
| `Showa` |  |
| `Heisei` |  |
| `Reiwa` |  |

### 取りうる値: `law_num_type — 法令番号の法令種別`

| 値 | 意味 |
|---|---|
| `Constitution` | 憲法 |
| `Act` | 法律 |
| `CabinetOrder` | 政令 |
| `ImperialOrder` | 勅令 |
| `MinisterialOrdinance` | 府省令 |
| `Rule` | 規則 |
| `Misc` | その他 |

### 取りうる値: `law_type — 法令種別`

| 値 | 意味 |
|---|---|
| `Constitution` | 憲法 |
| `Act` | 法律 |
| `CabinetOrder` | 政令 |
| `ImperialOrder` | 勅令 |
| `MinisterialOrdinance` | 府省令 |
| `Rule` | 規則 |
| `Misc` | その他 |

### 取りうる値: `mission — 新規制定又は被改正法令（`New`）・一部改正法令（`Partial`）`

| 値 | 意味 |
|---|---|
| `New` | 新規制定 |
| `Partial` | 一部改正 |

### 取りうる値: `repeal_status — 廃止等の状態`

| 値 | 意味 |
|---|---|
| `None` | 廃止・失効等の状態なし |
| `Repeal` | 廃止 |
| `Expire` | 失効 |
| `Suspend` | 停止 |
| `LossOfEffectiveness` | 実効性喪失 |

### 取りうる値: `response_format — レスポンス形式（`json` 又は `xml`）`

| 値 | 意味 |
|---|---|
| `json` |  |
| `xml` |  |

## e-Gov データポータル（CKAN API） (`egov-data-catalog`)

- 出所: 実データ由来（レスポンスを読んで列挙。網羅の保証は無い）
- 抽出方法: package_search で取得した 20 件に現れた項目の和。説明は先頭 15 件のデータセット画面に出る日本語ラベルを、同じ値を持つ API の項目と突き合わせて対応付けたもの（値が一意に一致したものだけ採用）
- 参照元: https://data.e-gov.go.jp/data/api/3/action/package_search

### package（データセット）

1 件のデータセットを表す。resources に実ファイルがぶら下がる。

| 項目 | 型 | 説明 |
|---|---|---|
| `author` | string |  |
| `author_email` | null | サンプル内では常に null |
| `compliant_standard` | string |  |
| `contactPoint` | string |  |
| `contactPoint_email` | string |  |
| `contactPoint_etc` | string |  |
| `contactPoint_ext` | string |  |
| `contactPoint_formUrl` | string |  |
| `contactPoint_tel` | string |  |
| `creator_user_id` | string |  |
| `distribution` | string |  |
| `etc` | string |  |
| `extras` | array |  |
| `frequency_of_update` | string | 作成頻度 |
| `groups` | array |  |
| `history_information` | string |  |
| `id` | string |  |
| `index_id` | string |  |
| `isopen` | boolean |  |
| `landingPage` | string | 公開ウェブページ |
| `language` | string | 言語 |
| `license_id` | null | サンプル内では常に null |
| `license_title` | null | サンプル内では常に null |
| `local_government` | string |  |
| `maintainer` | null | サンプル内では常に null |
| `maintainer_email` | null | サンプル内では常に null |
| `metadata_created` | string |  |
| `metadata_modified` | string |  |
| `name` | string | データセット管理名 |
| `notes` | string | 説明 |
| `num_resources` | number |  |
| `num_tags` | number |  |
| `opendata_id` | string |  |
| `organization` | object |  |
| `owner_org` | string |  |
| `private` | boolean |  |
| `provider_last_modified_date` | string |  |
| `provider_metadata_modified` | string |  |
| `publisher` | string | 公表組織名 |
| `related_documents` | string |  |
| `relationships_as_object` | array |  |
| `relationships_as_subject` | array |  |
| `resources` | array |  |
| `spatial` | string | 対象地域 |
| `state` | string |  |
| `subtitle` | string |  |
| `tags` | array |  |
| `temporal` | string |  |
| `title` | string | タイトル |
| `type` | string |  |
| `url` | null | サンプル内では常に null |
| `version` | string |  |

### resource（データセットに紐づくファイル）

データセットが提供する個々のファイルや API のエンドポイント。

| 項目 | 型 | 説明 |
|---|---|---|
| `access_url` | string |  |
| `cache_last_updated` | null | サンプル内では常に null |
| `cache_url` | null | サンプル内では常に null |
| `compliant_standard` | string |  |
| `copyright` | string |  |
| `created` | string |  |
| `datastore_active` | boolean |  |
| `datastore_contains_all_records_of_source_file` | boolean |  |
| `description` | string |  |
| `docanlys` | boolean |  |
| `download_url` | string |  |
| `format` | string |  |
| `hash` | string |  |
| `id` | string |  |
| `language` | string | 言語 |
| `last_modified` | null | サンプル内では常に null |
| `last_modified_date` | string |  |
| `license_id` | string |  |
| `metadata_modified` | string |  |
| `mimetype` | string |  |
| `mimetype_inner` | null | サンプル内では常に null |
| `name` | string | データセット管理名 |
| `package_id` | string |  |
| `position` | number |  |
| `private` | string |  |
| `provider_last_modified_date` | string |  |
| `provider_metadata_modified` | string |  |
| `related_documents` | string |  |
| `resource_type` | null | サンプル内では常に null |
| `size` | number |  |
| `state` | string |  |
| `terms_and_conditions` | string |  |
| `url` | string |  |
| `url_type` | string |  |

## 気象庁防災情報XML（PULL型 Atom フィード） (`jma-xml`)

- 出所: 入力は仕様由来、戻り値は実データ由来
- 抽出方法: 全電文共通の Report / Control / Head は公式の XML Schema（jmx.xsd, jmx_ib.xsd）から。Atom フィードと電文 4 通の構造は実データから列挙。電文種別は多数あり、ここに出るのはその一部
- 参照元: https://xml.kishou.go.jp/jmaxml_20241031_Schema%28xsd%29.zip

### type.report（XML Schema 由来 / jmx.xsd）

| 項目 | 型 | 説明 |
|---|---|---|
| `Control` | type.control | （必須） |
| `Head` | 要素 | （必須） |

### type.control（XML Schema 由来 / jmx.xsd）

| 項目 | 型 | 説明 |
|---|---|---|
| `Title` | string | （必須） |
| `DateTime` | dateTime | （必須） |
| `Status` | enum.UNION.type.control.Status | （必須） |
| `EditorialOffice` | string | （必須） |
| `PublishingOffice` | list.type.control.PublishingOffice | （必須） |

### type.head（XML Schema 由来 / jmx_ib.xsd）

| 項目 | 型 | 説明 |
|---|---|---|
| `Title` | string | （必須） |
| `ReportDateTime` | dateTime | （必須） |
| `TargetDateTime` | dateTime | （必須） |
| `TargetDTDubious` | string | （任意） |
| `TargetDuration` | duration | （任意） |
| `ValidDateTime` | dateTime | （任意） |
| `EventID` | string | （必須） |
| `InfoType` | string | （必須） |
| `Serial` | string | （必須） |
| `InfoKind` | string | （必須） |
| `InfoKindVersion` | string | （必須） |
| `Headline` | type.headline | （必須） |

### Atom フィード（実データ由来）

電文の入電を知らせるフィード。entry の link から電文本体を取得する。

| 項目 | 型 | 説明 |
|---|---|---|
| `entry` | string |  |
| `entry/author` | string |  |
| `entry/content` | string |  |
| `entry/id` | string |  |
| `entry/link` | string |  |
| `entry/title` | string |  |
| `entry/updated` | string |  |
| `id` | string |  |
| `link` | string |  |
| `rights` | string |  |
| `subtitle` | string |  |
| `title` | string |  |
| `updated` | string |  |

### 電文 Body: 気象警報・注意報（Ｒ０６）（集約通報）（実データ由来 / regular フィード）

この電文種別に固有の Body 構造。種別ごとに異なるため、他の電文には当てはまらない。

| 項目 | 型 | 説明 |
|---|---|---|
| `Report/Control` | 要素 |  |
| `Report/Control/Title` | 要素 |  |
| `Report/Control/DateTime` | 要素 |  |
| `Report/Control/Status` | 要素 |  |
| `Report/Control/EditorialOffice` | 要素 |  |
| `Report/Control/PublishingOffice` | 要素 |  |
| `Report/Head` | 要素 |  |
| `Report/Head/Title` | 要素 |  |
| `Report/Head/ReportDateTime` | 要素 |  |
| `Report/Head/TargetDateTime` | 要素 |  |
| `Report/Head/EventID` | 要素 |  |
| `Report/Head/InfoType` | 要素 |  |
| `Report/Head/Serial` | 要素 |  |
| `Report/Head/InfoKind` | 要素 |  |
| `Report/Head/InfoKindVersion` | 要素 |  |
| `Report/Head/Headline` | 要素 |  |
| `Report/Head/Headline/Text` | 要素 |  |
| `Report/Head/Headline/Information` | 要素 |  |
| `Report/Body` | 要素 |  |
| `Report/Body/Warning` | 要素 |  |
| `Report/Body/Warning/Item` | 要素 |  |

### 電文 Body: 台風解析・予報情報（５日予報）（Ｈ３０）（実データ由来 / extra フィード）

この電文種別に固有の Body 構造。種別ごとに異なるため、他の電文には当てはまらない。

| 項目 | 型 | 説明 |
|---|---|---|
| `Report/Control` | 要素 |  |
| `Report/Control/Title` | 要素 |  |
| `Report/Control/DateTime` | 要素 |  |
| `Report/Control/Status` | 要素 |  |
| `Report/Control/EditorialOffice` | 要素 |  |
| `Report/Control/PublishingOffice` | 要素 |  |
| `Report/Head` | 要素 |  |
| `Report/Head/Title` | 要素 |  |
| `Report/Head/ReportDateTime` | 要素 |  |
| `Report/Head/TargetDateTime` | 要素 |  |
| `Report/Head/TargetDuration` | 要素 |  |
| `Report/Head/EventID` | 要素 |  |
| `Report/Head/InfoType` | 要素 |  |
| `Report/Head/Serial` | 要素 |  |
| `Report/Head/InfoKind` | 要素 |  |
| `Report/Head/InfoKindVersion` | 要素 |  |
| `Report/Head/Headline` | 要素 |  |
| `Report/Head/Headline/Text` | 要素 |  |
| `Report/Body` | 要素 |  |
| `Report/Body/MeteorologicalInfos` | 要素 |  |
| `Report/Body/MeteorologicalInfos/MeteorologicalInfo` | 要素 |  |

### 電文 Body: 震源・震度に関する情報（実データ由来 / eqvol フィード）

この電文種別に固有の Body 構造。種別ごとに異なるため、他の電文には当てはまらない。

| 項目 | 型 | 説明 |
|---|---|---|
| `Report/Control` | 要素 |  |
| `Report/Control/Title` | 要素 |  |
| `Report/Control/DateTime` | 要素 |  |
| `Report/Control/Status` | 要素 |  |
| `Report/Control/EditorialOffice` | 要素 |  |
| `Report/Control/PublishingOffice` | 要素 |  |
| `Report/Head` | 要素 |  |
| `Report/Head/Title` | 要素 |  |
| `Report/Head/ReportDateTime` | 要素 |  |
| `Report/Head/TargetDateTime` | 要素 |  |
| `Report/Head/EventID` | 要素 |  |
| `Report/Head/InfoType` | 要素 |  |
| `Report/Head/Serial` | 要素 |  |
| `Report/Head/InfoKind` | 要素 |  |
| `Report/Head/InfoKindVersion` | 要素 |  |
| `Report/Head/Headline` | 要素 |  |
| `Report/Head/Headline/Text` | 要素 |  |
| `Report/Body` | 要素 |  |
| `Report/Body/Earthquake` | 要素 |  |
| `Report/Body/Earthquake/OriginTime` | 要素 |  |
| `Report/Body/Earthquake/ArrivalTime` | 要素 |  |
| `Report/Body/Earthquake/Hypocenter` | 要素 |  |
| `Report/Body/Earthquake/Magnitude` | 要素 |  |
| `Report/Body/Intensity` | 要素 |  |
| `Report/Body/Intensity/Observation` | 要素 |  |
| `Report/Body/Comments` | 要素 |  |
| `Report/Body/Comments/ForecastComment` | 要素 |  |
| `Report/Body/Comments/VarComment` | 要素 |  |

### 電文 Body: 生物季節観測（実データ由来 / other フィード）

この電文種別に固有の Body 構造。種別ごとに異なるため、他の電文には当てはまらない。

| 項目 | 型 | 説明 |
|---|---|---|
| `Report/Control` | 要素 |  |
| `Report/Control/Title` | 要素 |  |
| `Report/Control/DateTime` | 要素 |  |
| `Report/Control/Status` | 要素 |  |
| `Report/Control/EditorialOffice` | 要素 |  |
| `Report/Control/PublishingOffice` | 要素 |  |
| `Report/Head` | 要素 |  |
| `Report/Head/Title` | 要素 |  |
| `Report/Head/ReportDateTime` | 要素 |  |
| `Report/Head/TargetDateTime` | 要素 |  |
| `Report/Head/EventID` | 要素 |  |
| `Report/Head/InfoType` | 要素 |  |
| `Report/Head/Serial` | 要素 |  |
| `Report/Head/InfoKind` | 要素 |  |
| `Report/Head/InfoKindVersion` | 要素 |  |
| `Report/Head/Headline` | 要素 |  |
| `Report/Head/Headline/Text` | 要素 |  |
| `Report/Body` | 要素 |  |
| `Report/Body/MeteorologicalInfos` | 要素 |  |
| `Report/Body/MeteorologicalInfos/MeteorologicalInfo` | 要素 |  |
| `Report/Body/AdditionalInfo` | 要素 |  |
| `Report/Body/AdditionalInfo/ObservationAddition` | 要素 |  |

## 国立国会図書館サーチ 外部提供インタフェース (`ndl-search`)

- 出所: 実データ由来（レスポンスを読んで列挙。網羅の保証は無い）
- 抽出方法: 各経路のレスポンスを実際に読んで列挙。API 仕様書は PDF で配布されており機械可読ではないため、仕様由来の項目定義は取り込めていない
- 参照元: https://ndlsearch.ndl.go.jp/help/api/specifications

### OpenSearch: channel（RSS）

検索結果全体。件数と取得位置がここに入る。

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `title` | 要素 |  | `桜 - 国立国会図書館サーチ OpenSearch` |
| `link` | 要素 |  | `https://ios-v2-prod-eks-alb.ndlsearch.ndl.go.jp/api/opensear` |
| `description` | 要素 |  | `Search results for cnt=1 title=桜` |
| `language` | 要素 |  | `ja` |
| `totalResults` | 要素 |  | `77060` |
| `startIndex` | 要素 |  | `1` |
| `itemsPerPage` | 要素 |  | `1` |

### OpenSearch: item（書誌 1 件）

検索にヒットした資料 1 件分。同名要素が繰り返し現れることがある。

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `title` | 要素 |  | `あー、いいのいいの。わたし好きな人いるから` |
| `link` | 要素 |  | `https://ndlsearch.ndl.go.jp/books/R000000004-I028071794` |
| `description` | 要素 |  | `<p><p><ul><li>タイトル：あー、いいのいいの。わたし好きな人いるから</li><li>タイトル（読み）：アー` |
| `author` | 要素 |  | `早川 茉莉,早川 茉莉` |
| `category` | 要素 |  | `記事` |
| `guid` | 要素 |  | `https://ndlsearch.ndl.go.jp/books/R000000004-I028071794` |
| `pubDate` | 要素 |  | `Wed, 26 Jun 2024 20:37:41 +0900` |
| `titleTranscription` | 要素 |  | `アー 、 イイ ノ イイ ノ 。 ワタシ スキ ナ ヒト イル カラ` |
| `creator` | 要素 |  | `早川 茉莉` |
| `seriesTitle` | 要素 |  | `特集 こうの史代 : 『夕凪の街 桜の国』『この世界の片隅に』『ぼおるぺん古事記』から『日の鳥』へ` |
| `seriesTitleTranscription` | 要素 |  | `トクシュウ コウ ノ シダイ : 『 ユウナギ ノ マチ サクラ ノ クニ 』 『 コノ セカイ ノ カタスミ ニ 』 ` |
| `publicationPlace` | 要素 |  | `JP` |
| `identifier` | 要素 |  | `028071794` |
| `subject` | 要素 |  | `ZK24` |
| `seeAlso` | 要素 |  |  |

### OAI-PMH: Identify（リポジトリ情報）

ハーベスト前に確認する、リポジトリの素性と差分取得の粒度。

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `repositoryName` | 要素 |  | `国立国会図書館サーチ` |
| `baseURL` | 要素 |  | `https://ndlsearch.ndl.go.jp` |
| `protocolVersion` | 要素 |  | `Version 2.0` |
| `earliestDatestamp` | 要素 |  | `2022-10-01T00:00:00Z` |
| `deletedRecord` | 要素 |  | `persistent` |
| `granularity` | 要素 |  | `YYYY-MM-DDThh:mm:ssZ` |

## 統計 LOD（SPARQL エンドポイント） (`estat-lod`)

- 出所: 実データ由来（レスポンスを読んで列挙。網羅の保証は無い）
- 抽出方法: SPARQL の応答構造と、実データに現れる述語を実測で列挙。RDF は固定スキーマを持たないため、ここに出るのは観測できた述語であって語彙の全量ではない
- 参照元: https://data.e-stat.go.jp/lodw/sparqlendpoint/api

### SPARQL Results JSON（応答の器）

SELECT / ASK の応答形式。head.vars に変数名、results.bindings に行が入る。

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `head.vars` | string[] | クエリで指定した変数名の一覧 |  |
| `results.bindings[]` | object[] | 1 行分。変数名をキーに値が入る |  |
| `results.bindings[].<変数>.type` | string | リテラルか URI かの別 | `uri` |
| `results.bindings[].<変数>.value` | string | 値そのもの | `http://data.e-stat.go.jp/lod/dataset/gridCode/dm012015502/ob` |

### 統計値 1 件が持つ述語

RDF に固定スキーマは無いため、項目にあたるのは述語。観測値 1 件を例に、実際に使われている述語を並べる。

| 項目 | 型 | 説明 |
|---|---|---|
| `dimension#refArea` | 述語 | http://purl.org/linked-data/sdmx/2009/dimension#refArea |
| `indexItems` | 述語 | http://data.e-stat.go.jp/lod/ontology/g00200573/dimension/2015/indexItems |
| `22-rdf-syntax-ns#type` | 述語 | http://www.w3.org/1999/02/22-rdf-syntax-ns#type |
| `index` | 述語 | http://data.e-stat.go.jp/lod/ontology/measure/index |
| `unitMeasure` | 述語 | http://data.e-stat.go.jp/lod/ontology/attribute/unitMeasure |
| `cube#measureType` | 述語 | http://purl.org/linked-data/cube#measureType |
| `timePeriod` | 述語 | http://data.e-stat.go.jp/lod/ontology/crossDomain/dimension/timePeriod |
| `unitMult` | 述語 | http://data.e-stat.go.jp/lod/ontology/attribute/unitMult |
| `obsType` | 述語 | http://data.e-stat.go.jp/lod/ontology/attribute/obsType |
| `cube#dataSet` | 述語 | http://purl.org/linked-data/cube#dataSet |

## 地理院タイル（国土地理院 XYZ タイル配信） (`gsi-tiles`)

- 出所: 入力は仕様由来、戻り値は実データ由来
- 抽出方法: URL パラメータと標高タイルの読み方は仕様ページ・標高タイルの詳細仕様から、データ ID の一覧と提供条件は一覧ページから引いた。GeoJSON タイルの属性だけは定義書が無いため実データから列挙しており、そのタイルに現れなかった属性は落ちる
- 参照元: https://maps.gsi.go.jp/development/ichiran.html

### URL テンプレートのパラメータ

タイル 1 枚の URL は https://cyberjapandata.gsi.go.jp/xyz/{t}/{z}/{x}/{y}.{ext} で、この 5 つを埋めて GET する。説明は仕様ページの記述をそのまま引いた。

| 項目 | 型 | 説明 |
|---|---|---|
| `{t}` | パス要素 | データID |
| `{x}` | パス要素 | タイル座標のX値 |
| `{y}` | パス要素 | タイル座標のY値 |
| `{z}` | パス要素 | ズームレベル |
| `{ext}` | パス要素 | 拡張子 |

### 標高タイル（テキスト形式・.txt）のセル

1 行に 256 個の標高値がカンマ区切りで並び、それが 256 行。地図タイルのピクセル座標に対応する。

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `標高値` | 数値（m） | 標高データは小数点第二位までデータとして入っている（単位はm）。 | `20.71` |
| `e` | 文字 | 標高値が存在しない画素には「e」の文字が格納されている。 | `e` |
| `行・列` | 構造 | 数値データは対応する地図タイルのピクセル座標における標高値を表す。 | `256 行 × 256 列` |

### 標高タイル（PNG 形式・.png）の画素

24 ビットカラー PNG の画素値から標高値を計算する。x = 2^16 R + 2^8 G + B とし、x < 2^23 なら h = xu、x = 2^23 なら NA、x > 2^23 なら h = (x - 2^24)u（u は標高分解能 0.01m）。

| 項目 | 型 | 説明 |
|---|---|---|
| `R, G, B` | 画素値（0〜255） | ピクセルの画素値（RGB値）から、当該ピクセル座標の標高値が算出できます。 |
| `(R, G, B) = (128, 0, 0)` | 画素値 | また、無効値（標高タイル（テキスト形式）の「e」に該当する箇所）は(R, G, B)=(128, 0, 0)です。 |

### GeoJSON タイル: 指定緊急避難場所（洪水）（`skhb01` ZL10）

タイル 10/909/403 の 1195 件を通して現れた属性。定義書は公開されておらず、説明は空欄になる。

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `name` | string |  | `あすはステーション大泉` |
| `address` | string |  | `東京都練馬区東大泉7-20-1` |
| `remarks` | null/string |  | `洪水は２階以上、高潮、津波は３階以上が対象` |
| `disaster1` | number |  | `1` |
| `disaster7` | number |  | `1` |
| `disaster3` | number |  | `1` |
| `disaster2` | number |  | `1` |
| `disaster4` | number |  | `1` |
| `disaster5` | number |  | `1` |
| `disaster8` | number |  | `1` |
| `disaster6` | number |  | `1` |

### GeoJSON タイル: 自然災害伝承碑（すべて）（`disaster_lore_all` ZL7）

タイル 7/113/50 の 536 件を通して現れた属性。定義書は公開されておらず、説明は空欄になる。

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `ID` | string |  | `08201-001` |
| `LoreName` | string |  | `洪水記念` |
| `LoreYear` | string |  | `1939` |
| `Address` | string |  | `茨城県水戸市柳河町(柳河小学校)` |
| `DisasterName` | string |  | `昭和13年洪水 (1938年6月ほか)` |
| `DisasterKind` | string |  | `洪水` |
| `DisasterInfo` | string |  | `昭和13年(1938)6月の那珂川の氾濫により、柳河村では家屋の被害(半壊7軒、流出6軒、浸水が442軒)、千歳橋と万代` |
| `ReleaseDate` | string |  | `2019/7/31` |
| `ModifyReleaseDate` | string |  | `2019/10/16、2020/10/9` |
| `Limitations` | string |  | `写真の二次利用：常総市教育委員会への利用申請が必要` |
| `Image` | string |  | `https://maps.gsi.go.jp/legend/disaster_lore/08201/08201-001.` |
| `ImageWidth` | string |  | `1200` |
| `ImageHeight` | string |  | `1200` |

### 自然災害伝承碑として公開している情報（一覧ページの記載）

一覧ページの備考が日本語の名前で列挙しているもの。上の GeoJSON の属性名との対応は一次資料に書かれていないので、突き合わせていない。

| 項目 | 型 | 説明 |
|---|---|---|
| `碑名` | 記載 | 自然災害伝承碑の名称 |
| `災害名` | 記載 | 同碑の対象となっている災害名 |
| `災害種別` | 記載 | 同碑の対象となっている災害の種類 |
| `建立年` | 記載 | 同碑が建立された年 |
| `所在地` | 記載 | 同碑の所在地 |
| `伝承内容` | 記載 | 碑文に記載された内容に、死者数や建物被害など被害の規模を示す情報等を補足し、100字程度に要約した情報 |
| `写真` | 記載 | 同碑の写真 |

### 取りうる値: `{t}（データ ID） — 一覧ページに載っている配信中のタイル。意味の欄は「名称（URL に添えられた注記）｜利用条件の分類｜ズームレベル｜提供範囲」の順に、一覧ページの記載を並べたもの`

| 値 | 意味 |
|---|---|
| `std` | 標準地図｜.png｜1. 基本測量成果／2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 18／15～17／12～14／9～11／5～8／2～8｜日本全国／日本全国とその周辺地域／全球（ズームレベル5～8の日本全国とその周辺地域を除く） |
| `pale` | 淡色地図｜.png｜1. 基本測量成果／2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 18／15～17／12～14／9～11／5～8／2～8｜日本全国／日本全国とその周辺地域／全球（ズームレベル5～8の日本全国とその周辺地域を除く） |
| `english` | English｜.png｜1. 基本測量成果｜ZL 9～11／5～8｜日本全国／日本全国とその周辺地域 |
| `lcm25k_2012` | 数値地図25000（土地条件）｜.png｜1. 基本測量成果｜ZL 10～16 |
| `lcm25k` | 土地条件図（初期整備版）｜.png｜1. 基本測量成果｜ZL 14～16 |
| `ccm1` | 沿岸海域土地条件図（平成元年以降）｜.png｜1. 基本測量成果｜ZL 14～16 |
| `ccm2` | 沿岸海域土地条件図（昭和63年以前）｜.png｜1. 基本測量成果｜ZL 14～16 |
| `vbm` | 火山基本図｜.png｜1. 基本測量成果｜ZL 11～17｜整備状況一覧図をご覧ください。 |
| `vbmd_bm` | 火山基本図データ（基図）｜.png｜1. 基本測量成果｜ZL 11～18｜整備状況一覧図をご覧ください。 |
| `vbmd_colorrel` | 火山基本図データ（陰影段彩図）｜.png｜1. 基本測量成果｜ZL 11～18｜整備状況一覧図をご覧ください。 |
| `vbmd_pm` | 火山基本図データ（写真地図）｜.png｜1. 基本測量成果｜ZL 11～18｜整備状況一覧図をご覧ください。 |
| `vlcd` | 火山土地条件図｜.png｜1. 基本測量成果｜ZL 10～16 |
| `lum4bl_capital2005` | 宅地利用動向調査（首都圏 2005年）｜.png｜1. 基本測量成果｜ZL 13～16｜首都圏（2000年、2005年）、中部圏（2003年）、近畿圏（2001年、2008年） |
| `lum4bl_capital2000` | 宅地利用動向調査（首都圏 2000年）｜.png｜1. 基本測量成果｜ZL 13～16｜首都圏（2000年、2005年）、中部圏（2003年）、近畿圏（2001年、2008年） |
| `lum4bl_chubu2003` | 宅地利用動向調査（中部圏 2003年）｜.png｜1. 基本測量成果｜ZL 13～16｜首都圏（2000年、2005年）、中部圏（2003年）、近畿圏（2001年、2008年） |
| `lum4bl_kinki2008` | 宅地利用動向調査（近畿圏 2008年）｜.png｜1. 基本測量成果｜ZL 13～16｜首都圏（2000年、2005年）、中部圏（2003年）、近畿圏（2001年、2008年） |
| `lum4bl_kinki2001` | 宅地利用動向調査（近畿圏 2001年）｜.png｜1. 基本測量成果｜ZL 13～16｜首都圏（2000年、2005年）、中部圏（2003年）、近畿圏（2001年、2008年） |
| `lum200k` | 20万分1土地利用図（1982～1983年）｜.png｜1. 基本測量成果｜ZL 11～14｜日本全国(一部を除く) |
| `lake1` | 湖沼図｜.png｜1. 基本測量成果｜ZL 11～17｜調査実施湖沼一覧をご覧ください。 |
| `lakedata` | 湖沼データ｜.png｜1. 基本測量成果｜ZL 11～18｜調査実施湖沼一覧をご覧ください。 |
| `blank` | 白地図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 5～14｜日本全国 |
| `seamlessphoto` | 写真｜.jpg｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 14～18／9～13／2～8｜日本全国／全世界(一部を除く) |
| `gazo4` | 1987年～1990年｜.jpg｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～17 |
| `gazo3` | 1984年～1986年｜.jpg｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～17 |
| `gazo2` | 1979年～1983年｜.jpg｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～17 |
| `gazo1` | 1974年～1978年｜.jpg｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～17 |
| `ort_old10` | 1961年～1969年｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～17 |
| `ort_USA10` | 1945年～1950年｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～17 |
| `ort_riku10` | 1936年～1942年頃｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 13～18｜東京23区内（世田谷区の一部を除く） 大阪市とその周辺 |
| `ort_1928` | 1928年頃｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 13～18｜大阪市域 |
| `ort` | 電子国土基本図（オルソ画像）（2007年～）｜.jpg｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 14～18 |
| `airphoto` | 簡易空中写真（2004年～）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 14, 15, 16, 17, 18 |
| `pp` | 単写真｜.geojson｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 14｜日本全国 |
| `lndst` | 全国ランドサットモザイク画像｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～13｜日本全国 |
| `modis` | 世界衛星モザイク画像｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～8｜全世界(一部を除く) |
| `relief` | 色別標高図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 5～15｜日本全国 |
| `anaglyphmap_color` | アナグリフ（カラー）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～12（DEM10B） 13～16（DEM5A、DEM5B、DEM10B）｜日本全国 |
| `anaglyphmap_gray` | アナグリフ（グレー）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～12（DEM10B） 13～16（DEM5A、DEM5B、DEM10B）｜日本全国 |
| `hillshademap` | 陰影起伏図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～12（DEM10B） 13～16（DEM5A、DEM5B、DEM10B）｜日本全国 |
| `earthhillshade` | 陰影起伏図（全球版）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 0～8｜全球 |
| `slopemap` | 傾斜量図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 3～15（DEM5A、DEM5B、DEM10B）｜日本全国 |
| `slopezone1map` | 全国傾斜量区分図（雪崩関連）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 3～15（DEM5A、DEM5B、DEM10B）｜日本全国 |
| `sekishoku` | 赤色立体地図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～14｜日本全国 |
| `afm` | 活断層図（都市圏活断層図）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 11～16 |
| `lcmfc2` | 治水地形分類図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 11～16 |
| `swale` | 明治期の低湿地｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～16 |
| `cp` | 基準点｜.geojson｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 電子基準点：7 電子基準点・一等三角点：8～11 電子基準点・一等三角点・左記以外：12｜日本全国 |
| `jikizu2020_chijiki_d` | 磁気図2020.0年値（磁気図（偏角）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 「磁気図（偏角）／偏角一覧図」：磁気図…4～8、偏角一覧図…9～13 「磁気図（偏角以外）」：4～8｜日本全国 |
| `jikizu2020_chijiki_i` | 磁気図2020.0年値（磁気図（伏角）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 「磁気図（偏角）／偏角一覧図」：磁気図…4～8、偏角一覧図…9～13 「磁気図（偏角以外）」：4～8｜日本全国 |
| `jikizu2020_chijiki_f` | 磁気図2020.0年値（磁気図（全磁力）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 「磁気図（偏角）／偏角一覧図」：磁気図…4～8、偏角一覧図…9～13 「磁気図（偏角以外）」：4～8｜日本全国 |
| `jikizu2020_chijiki_h` | 磁気図2020.0年値（磁気図（水平分力）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 「磁気図（偏角）／偏角一覧図」：磁気図…4～8、偏角一覧図…9～13 「磁気図（偏角以外）」：4～8｜日本全国 |
| `jikizu2020_chijiki_z` | 磁気図2020.0年値（磁気図（鉛直分力）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 「磁気図（偏角）／偏角一覧図」：磁気図…4～8、偏角一覧図…9～13 「磁気図（偏角以外）」：4～8｜日本全国 |
| `jikizu2015_chijiki_d` | 磁気図2015.0年値（磁気図（偏角）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 「磁気図（偏角）／偏角一覧図」：磁気図…4～8、偏角一覧図…9～13 「磁気図（偏角以外）」：4～8｜日本全国 |
| `jikizu2015_chijiki_i` | 磁気図2015.0年値（磁気図（伏角）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 「磁気図（偏角）／偏角一覧図」：磁気図…4～8、偏角一覧図…9～13 「磁気図（偏角以外）」：4～8｜日本全国 |
| `jikizu2015_chijiki_f` | 磁気図2015.0年値（磁気図（全磁力）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 「磁気図（偏角）／偏角一覧図」：磁気図…4～8、偏角一覧図…9～13 「磁気図（偏角以外）」：4～8｜日本全国 |
| `jikizu2015_chijiki_h` | 磁気図2015.0年値（磁気図（水平分力）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 「磁気図（偏角）／偏角一覧図」：磁気図…4～8、偏角一覧図…9～13 「磁気図（偏角以外）」：4～8｜日本全国 |
| `jikizu2015_chijiki_z` | 磁気図2015.0年値（磁気図（鉛直分力）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 「磁気図（偏角）／偏角一覧図」：磁気図…4～8、偏角一覧図…9～13 「磁気図（偏角以外）」：4～8｜日本全国 |
| `jikizu_chijikid` | 磁気図2010.0年値（磁気図（偏角）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 「磁気図（偏角）／偏角一覧図」：磁気図…4～7、偏角一覧図…8～13 「磁気図（偏角以外）」：4～7｜日本全国 |
| `jikizu_chijikii` | 磁気図2010.0年値（磁気図（伏角）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 「磁気図（偏角）／偏角一覧図」：磁気図…4～7、偏角一覧図…8～13 「磁気図（偏角以外）」：4～7｜日本全国 |
| `jikizu_chijikif` | 磁気図2010.0年値（磁気図（全磁力）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 「磁気図（偏角）／偏角一覧図」：磁気図…4～7、偏角一覧図…8～13 「磁気図（偏角以外）」：4～7｜日本全国 |
| `jikizu_chijikih` | 磁気図2010.0年値（磁気図（水平分力）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 「磁気図（偏角）／偏角一覧図」：磁気図…4～7、偏角一覧図…8～13 「磁気図（偏角以外）」：4～7｜日本全国 |
| `jikizu_chijikiz` | 磁気図2010.0年値（磁気図（鉛直分力）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 「磁気図（偏角）／偏角一覧図」：磁気図…4～7、偏角一覧図…8～13 「磁気図（偏角以外）」：4～7｜日本全国 |
| `20240809hyuganada_nichinan_0809do_sokuho` | 令和6年宮崎県日向灘を震源とする地震 日南地区 正射画像（速報）（2024年8月9日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜宮崎県宮崎市、日南市 |
| `20240419bungosuido_sukumo_0418do` | 令和6年豊後水道の地震 宿毛地区 正射画像（2024年4月18日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜高知県宿毛市、四万十市、三原村、愛媛県南宇和郡愛南町 |
| `20240419bungosuido_ainan_0418do` | 令和6年豊後水道の地震 愛南地区 正射画像（2024年4月18日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜愛媛県南宇和郡愛南町、宇和島市 |
| `20240102noto_0405_0426do` | 令和6年能登半島地震 能登地区 正射画像（2024年4月5日～4月26日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県珠洲市、輪島市、能登町、穴水町、七尾市、志賀町、中能登町、羽咋市、宝達志水町、津幡町、かほく市、内灘町、金沢市 富山県氷見市、高岡市、射水市、小矢部市、富 |
| `20240102noto_wazimanishi_0117do` | 令和6年能登半島地震 輪島西地区 正射画像（2024年1月17日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県輪島市、穴水町、七尾市、志賀町 |
| `20240102noto_anamizu_0117do` | 令和6年能登半島地震 穴水地区 正射画像（2024年1月17日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県穴水町、珠洲市、輪島市、能登町、七尾市 |
| `20240102noto_nanao_0117do` | 令和6年能登半島地震 七尾地区 正射画像（2024年1月17日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県七尾市、志賀町、中能登町 |
| `20240102noto_suzu_0114do` | 令和6年能登半島地震 珠洲地区 正射画像（2024年1月14日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県珠洲市 |
| `20240102noto_wazimahigashi_0114do` | 令和6年能登半島地震 輪島東地区 正射画像（2024年1月14日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県輪島市、珠洲市、能登町 |
| `20240102noto_anamizu_0114do` | 令和6年能登半島地震 穴水地区 正射画像（2024年1月14日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県穴水町、輪島市、能登町、珠洲市 |
| `20240102noto_wazimanaka_0111do` | 令和6年能登半島地震 輪島中地区 正射画像（2024年1月11日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県石川県輪島市、能登町、穴水町 |
| `20240102noto_wazimanishi_0111do` | 令和6年能登半島地震 輪島西地区 正射画像（2024年1月11日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県輪島市、穴水町、志賀町、七尾市 |
| `20240102noto_anamizu_0111do` | 令和6年能登半島地震 穴水地区 正射画像（2024年1月11日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県穴水町、輪島市、能登町 |
| `20240102_noto_suzu_0105do` | 令和6年能登半島地震 珠洲地区 正射画像（2024年1月5日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県珠洲市 |
| `20240102_noto_wazimanaka_0105do` | 令和6年能登半島地震 輪島中地区 正射画像（2024年1月5日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県輪島市、能登町、穴水町 |
| `20240102_noto_anamizu_0105do` | 令和6年能登半島地震 穴水地区 正射画像（2024年1月5日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県穴水町、輪島市、能登町、珠洲市、七尾市 |
| `20240102_noto_nanao_0105do` | 令和6年能登半島地震 七尾地区 正射画像（2024年1月5日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県七尾市、志賀町、中能登町 |
| `20240102noto_suzu_0102do` | 令和6年能登半島地震 珠洲地区 正射画像（2024年1月2日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県珠洲市、輪島市 |
| `20240102noto_wazimanaka_0102do` | 令和6年能登半島地震 輪島中地区 正射画像（2024年1月2日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県輪島市、能登町 |
| `20240102noto_wazimahigashi_0102do` | 令和6年能登半島地震 輪島東地区 正射画像（2024年1月2日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県輪島市、珠洲市、能登町 |
| `20190618yamagata_tsuruokamurakami_0620do` | 令和元年山形県沖の地震 鶴岡村上地区 正射画像（2019年06月20日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜山形県鶴岡市、新潟県村上市 |
| `20190618yamagata_tsuruokamurakami_0626do1` | 令和元年山形県沖の地震 鶴岡村上地区 正射画像（2019年06月26日撮影①）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜山形県鶴岡市、新潟県村上市 |
| `20190618yamagata_tsuruokamurakami_0626do` | 令和元年山形県沖の地震 鶴岡村上地区 正射画像（2019年06月26日撮影②）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜山形県鶴岡市、新潟県村上市 |
| `20190618yamagata_tsuruoka_digital` | 令和元年山形県沖の地震 デジタル標高地形図 山形県鶴岡市周辺｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～16｜山形県鶴岡市周辺 |
| `20180906hokkaido_kiyota_0913do` | 平成30年北海道胆振東部地震 札幌市清田地区 正射画像（2018年9月13日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜北海道札幌市清田区・厚別区、北広島市 |
| `20180906hokkaido_abira_0911do` | 平成30年北海道胆振東部地震 安平地区 正射画像（2018年9月11日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜北海道勇払郡安平町・厚真町など |
| `20180906hokkaido_atsuma_0911do` | 平成30年北海道胆振東部地震 厚真川地区 正射画像（2018年9月11日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜北海道勇払郡厚真町・安平町・むかわ町 |
| `20180906hokkaido_kiyota_0912do` | 平成30年北海道胆振東部地震 札幌市清田地区 正射画像（2018年9月12日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜北海道札幌市清田区・厚別区、北広島市 |
| `20180906hokkaido_atsumatoubu_0911do` | 平成30年北海道胆振東部地震 厚真東部地区 正射画像（2018年9月11日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜北海道勇払郡厚真町・むかわ町、沙流郡平取町 |
| `20180906hokkaido_atsumaseibu_0911do` | 平成30年北海道胆振東部地震 安平・厚真西部地区 正射画像（2018年9月11日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜北海道千歳市・苫小牧市など |
| `20180906hokkaido_atsumachiku_0906do` | 平成30年北海道胆振東部地震 厚真地区 正射画像（2018年9月6,8日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜北海道勇払郡厚真町・安平町・むかわ町 |
| `20180906hokkaido_atsuma_0906do` | 平成30年北海道胆振東部地震 厚真川地区 正射画像（2018年9月6日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜北海道勇払郡厚真町・安平町・むかわ町 |
| `20180906hokkaido_atsuma_digital` | 平成30年北海道胆振東部地震 デジタル標高地形図 厚真町周辺｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 6～16｜北海道厚真町周辺 |
| `20180906hokkaido_iburi_hokaichi` | 平成30年北海道胆振東部地震 斜面崩壊・堆積分布図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 6～16 |
| `20180906hokkaido_atsuma_sekishoku` | 平成30年北海道胆振東部地震 赤色立体地図 厚真町周辺｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 6～16｜北海道厚真町周辺 |
| `20161228ibaraki_1229dol` | 平成28年茨城県北部の地震 正射画像（2016年12月29日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜茨城県北部 |
| `20161021tottori_1022dol` | 平成28年鳥取県中部の地震 正射画像（2016年10月22日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜鳥取県中部 |
| `fukkyukizu` | 平成28年熊本地震 応急復旧対策基図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 18 |
| `20160414kumamoto_0724dol` | 平成28年熊本地震 熊本2地区 正射画像（2016年7月5日～24日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜熊本地区付近 |
| `20160414kumamoto_0705dol` | 平成28年熊本地震 阿蘇3地区 正射画像（2016年7月5日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜阿蘇地区付近 |
| `20160414kumamoto_0531dol` | 平成28年熊本地震 南阿蘇河陽地区 正射画像（2016年5月31日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜南阿蘇河陽地区付近 |
| `20160414kumamoto_0530dol` | 平成28年熊本地震 益城・西原地区 正射画像（2016年5月30日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜益城・西原地区付近 |
| `20160414kumamoto_0429dol1` | 平成28年熊本地震 熊本断層地区A 正射画像（2016年4月29日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜熊本断層地区付近 |
| `20160414kumamoto_0429dol2` | 平成28年熊本地震 熊本断層地区B 正射画像（2016年4月29日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜熊本断層地区付近 |
| `20160414kumamoto_0420dol01` | 平成28年熊本地震 西原2地区 正射画像（2016年4月20日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西原地区付近 |
| `20160414kumamoto_0420dol02` | 平成28年熊本地震 阿蘇2地区 正射画像（2016年4月20日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜阿蘇地区付近 |
| `20160414kumamoto_0420dol03` | 平成28年熊本地震 南阿蘇2地区 正射画像（2016年4月20日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜南阿蘇地区付近 |
| `20160414kumamoto_0420dol04` | 平成28年熊本地震 御船地区 正射画像（2016年4月20日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜御船地区付近 |
| `20160414kumamoto_0420dol05` | 平成28年熊本地震 八代地区 正射画像（2016年4月20日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜八代地区付近 |
| `20160414kumamoto_0420dol06` | 平成28年熊本地震 天草地区 正射画像（2016年4月19日,20日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜天草地区付近 |
| `20160414kumamoto_0420dol07` | 平成28年熊本地震 玉名地区 正射画像（2016年4月20日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜玉名地区付近 |
| `20160414kumamoto_0420dol08` | 平成28年熊本地震 山鹿地区 正射画像（2016年4月20日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜山鹿地区付近 |
| `20160414kumamoto_0420dol09` | 平成28年熊本地震 菊池地区 正射画像（2016年4月20日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜菊池地区付近 |
| `20160414kumamoto_0420dol10` | 平成28年熊本地震 竹田地区 正射画像（2016年4月20日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜竹田地区付近 |
| `20160414kumamoto_0420dol11` | 平成28年熊本地震 湯布院地区 正射画像（2016年4月20日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜湯布院地区付近 |
| `20160414kumamoto_0419dol2` | 平成28年熊本地震 南阿蘇2地区 正射画像（2016年4月19日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜南阿蘇地区付近 |
| `20160414kumamoto_0419dol6` | 平成28年熊本地震 小国地区 正射画像（2016年4月19日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜小国地区付近 |
| `20160414kumamoto_0416dol1` | 平成28年熊本地震 熊本地区 正射画像（2016年4月16日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜熊本地区付近 |
| `20160414kumamoto_0416dol2` | 平成28年熊本地震 宇土地区 正射画像（2016年4月16日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜宇土地区付近 |
| `20160414kumamoto_0416dol3` | 平成28年熊本地震 合志地区 正射画像（2016年4月16日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜合志地区付近 |
| `20160414kumamoto_0416dol4` | 平成28年熊本地震 西原地区 正射画像（2016年4月16日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西原地区付近 |
| `20160414kumamoto_0416dol5` | 平成28年熊本地震 阿蘇地区 正射画像（2016年4月16日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜阿蘇地区付近 |
| `20160414kumamoto_0416dol6` | 平成28年熊本地震 南阿蘇地区 正射画像（2016年4月16日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜南阿蘇地区付近 |
| `20160414kumamoto_0416dol7` | 平成28年熊本地震 別府地区 正射画像（2016年4月16日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜別府地区付近 |
| `20160414kumamoto_0415dol1` | 平成28年熊本地震 益城地区 正射画像（2016年4月15日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 14～18｜益城地区付近 |
| `20160414kumamoto_0415dol2` | 平成28年熊本地震 熊本南地区 正射画像（2016年4月15日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜熊本南地区付近 |
| `20160414kumamoto_0415dol3` | 平成28年熊本地震 宇城地区 正射画像（2016年4月15日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜宇城地区付近 |
| `20110311_tohoku_shinsui` | 平成23年東北地方太平洋沖地震 津波浸水範囲｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 7～16 |
| `fukkokizu` | 平成23年東北地方太平洋沖地震 災害復興計画基図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 18 |
| `toho4` | 平成23年東北地方太平洋沖地震後正射画像（2013年9月～2013年12月撮影）｜.jpg｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 15, 16, 17, 18 |
| `toho3` | 平成23年東北地方太平洋沖地震後正射画像（2012年10月～2013年5月撮影）｜.jpg｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 15, 16, 17, 18 |
| `toho2` | 平成23年東北地方太平洋沖地震後正射画像（2011年5月～2012年4月撮影）｜.jpg｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 15, 16, 17, 18 |
| `toho1` | 平成23年東北地方太平洋沖地震後正射画像（2011年3月～2011年4月撮影）｜.jpg｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 15, 16, 17 |
| `20250815rain_amakusa_0815do_sokuho` | 令和7年8月6日からの大雨 天草上島地区 正射画像（速報）（2025年8月15日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜熊本県天草市、上天草市 |
| `20250815rain_yatsushironishi_0816do_sokuho` | 令和7年8月6日からの大雨 八代西地区 正射画像（速報）（2025年8月16日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜熊本県八代市、氷川町、宇城市、甲佐町、美里町、山都町、御船町 |
| `20250815rain_yatsushirohigashi_0816do_sokuho` | 令和7年8月6日からの大雨 八代東地区 正射画像（速報）（2025年8月16日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜熊本県山都町、宮崎県五ヶ瀬町 |
| `20240923rain_wajimatobu_0924do_sokuho` | 令和6年9月20日からの大雨 輪島東部地区 正射画像（速報）（2024年9月24日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県珠洲市、輪島市、能登町 |
| `20240923rain_wajimaseibu_0924do_sokuho` | 令和6年9月20日からの大雨 輪島西部地区 正射画像（速報）（2024年9月24日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県輪島市 |
| `20240923rain_wajima_0923do_sokuho` | 令和6年9月20日からの大雨 輪島地区 正射画像（速報）（2024年9月23日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜石川県珠洲市、輪島市、能登町 |
| `20240726rain_mogamigawa_0726dansaizu` | 令和6年7月25日からの大雨 浸水推定図 最上川水系最上川（2024年7月26日14時作成）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜最上川水系最上川 |
| `20230629rain_0711shinsui` | 令和5年6月29日からの大雨 浸水推定図 筑後川水系筑後川（2023年7月11日1時作成）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜筑後川水系筑後川 |
| `20220804rain_0804dansaizu` | 令和4年8月3日からの大雨 浸水推定図 村上市坂町周辺（2022年8月4日17時作成）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜村上市坂町周辺 |
| `20210815oame_0815dansaizu` | 令和3年8月の大雨 浸水推定図 六角川（2021年8月15日15時作成）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜六角川 |
| `20210705oame_0706do` | 令和3年7月1日からの大雨 正射画像 熱海伊豆山地区（7/6撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜熱海伊豆山地区 |
| `20210705oame_0706do_sokuho` | 令和3年7月1日からの大雨 正射画像（速報） 熱海伊豆山地区（7/6撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜熱海伊豆山地区 |
| `20200703oame_kumagawahitoyoshi_0704dansaizu` | 令和2年7月豪雨 浸水推定図 球磨川水系球磨川 人吉市周辺（2020年7月4日13時作成）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜球磨川水系球磨川 人吉市周辺 |
| `20200703oame_kumagawa_0704dansaizu` | 令和2年7月豪雨 浸水推定図 球磨川水系球磨川（2020年7月4日20時作成）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜球磨川水系球磨川 |
| `20200703oame_sashikigawayunouragawaashikita_0704dansaizu` | 令和2年7月豪雨 浸水推定図 佐敷川及び湯浦川流域 芦北町周辺（2020年7月4日22時作成）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜佐敷川及び湯浦川流域 芦北町周辺 |
| `20200703oame_omuta_0707dansaizu` | 令和2年7月豪雨 浸水推定図 大牟田市周辺（2020年7月7日9時作成）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜大牟田市周辺 |
| `20200703oame_hita_0707dansaizu` | 令和2年7月豪雨 浸水推定図 筑後川水系花月川 日田市友田周辺（2020年7月7日14時作成）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜筑後川水系花月川 日田市友田周辺 |
| `20200703oame_miyama_0708dansaizu` | 令和2年7月豪雨 浸水推定図 矢部川水系矢部川 みやま市周辺（2020年7月8日9時作成）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜矢部川水系矢部川 みやま市周辺 |
| `20200703oame_chikugogawa_0708dansaizu` | 令和2年7月豪雨 浸水推定図 筑後川水系筑後川（2020年7月8日16時作成）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜筑後川水系筑後川 |
| `20200703oame_chikugogawa_0709dansaizu` | 令和2年7月豪雨 浸水推定図 筑後川水系筑後川第2報（2020年7月9日18時作成）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜筑後川水系筑後川周辺 |
| `20200729rain_mogamigawa_0729dansaizu` | 令和2年7月豪雨 浸水推定図 最上川水系最上川（2020年7月29日12時作成）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜最上川水系最上川 |
| `20200729rain_mogamigawa_0729dansaizu2` | 令和2年7月豪雨 浸水推定図 最上川水系最上川（2020年7月29日20時作成）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜最上川水系最上川 |
| `20191025oame_sakura_1026do_sokuho` | 令和元年10月の低気圧に伴う大雨 正射画像（速報） 佐倉地区（千葉県千葉市、佐倉市、四街道市、印西市）佐倉地区（10/26撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜千葉県千葉市、佐倉市、四街道市、印西市 |
| `20191025oame_mobara_1026do_sokuho` | 令和元年10月の低気圧に伴う大雨 正射画像（速報） 茂原地区（千葉県茂原市、睦沢町、長生村、長南町）茂原地区（10/26撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜千葉県茂原市、睦沢町、長生村、長南町 |
| `20191025oame_sakura_1026dansaizu_sokuho` | 令和元年10月の低気圧に伴う大雨 浸水推定段彩図 速報版 千葉県佐倉市周辺｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜千葉県佐倉市周辺 |
| `20191025oame_mobara_1026dansaizu_sokuho` | 令和元年10月の低気圧に伴う大雨 浸水推定段彩図 速報版 千葉県茂原市・大網白里市周辺｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜千葉県茂原市・大網白里市周辺 |
| `20191025oame_mobara_1028dansaizu_handoku` | 令和元年10月の低気圧に伴う大雨 浸水推定段彩図 空中写真判読版 一宮川水系（一宮川・豊田川・阿久川）茂原駅周辺｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜一宮川水系（一宮川・豊田川・阿久川）茂原駅周辺 |
| `20191012typhoon19_tamagawa_1013do` | 令和元年台風第19号 正射画像 多摩川地区（東京都大田区、世田谷区、八王子市、立川市、府中市、昭島市、調布市、日野市、国立市、福生市、狛江市、多摩市、稲城市、あきる野市、神奈川県川崎市）多摩川地区（10/13撮影)｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜東京都大田区、世田谷区、八王子市、立川市、府中市、昭島市、調布市、日野市、国立市、福生市、狛江市、多摩市、稲城市、あきる野市、神奈川県川崎市 |
| `20191012typhoon19_tokigawa_1013do` | 令和元年台風第19号 正射画像 都幾川地区（埼玉県川越市、東松山市、坂戸市、嵐山町、川島町）都幾川地区（10/13撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜埼玉県川越市、東松山市、坂戸市、嵐山町、川島町 |
| `20191012typhoon19_nakagawa_1017do` | 令和元年台風第19号 正射画像 那珂川地区（茨城県水戸市、ひたちなか市、常陸大宮市、那珂市、城里町）那珂川地区（10/17撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜茨城県水戸市、ひたちなか市、常陸大宮市、那珂市、城里町 |
| `20191012typhoon19_kujigawa_1017do` | 令和元年台風第19号 正射画像 久慈川地区（茨城県日立市、常陸太田市、常陸大宮市、那珂市、東海村）久慈川地区（10/17撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜茨城県日立市、常陸太田市、常陸大宮市、那珂市、東海村 |
| `20191012typhoon19_kujigawa_daigo_1017do` | 令和元年台風第19号 正射画像 久慈川（大子）地区（茨城県大子町）久慈川（大子）地区（10/17撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜茨城県大子町 |
| `20191012typhoon19_marumori_1021do_sokuho` | 令和元年台風第19号 正射画像（速報） 丸森地区（宮城県白石市、角田市、丸森町、福島県相馬市、伊達市）丸森地区（10/21撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜宮城県白石市、角田市、丸森町、福島県相馬市、伊達市 |
| `20191012typhoon19_marumori_1020do_sokuho` | 令和元年台風第19号 正射画像（速報） 丸森地区（宮城県白石市、角田市、丸森町、福島県相馬市、伊達市）丸森地区（10/20撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜宮城県白石市、角田市、丸森町、福島県相馬市、伊達市 |
| `20191012typhoon19_chikumagawa_1016do_sokuho` | 令和元年台風第19号 正射画像（速報） 千曲川地区（長野県長野市、須坂市、中野市、千曲市、小布施町、山ノ内町）千曲川地区（10/16撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜長野県長野市、須坂市、中野市、千曲市、小布施町、山ノ内町 |
| `20191012typhoon19_naruse_1014dansaizu` | 令和元年台風第19号 浸水推定段彩図 鳴瀬川水系（吉田川）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜吉田川 |
| `20191012typhoon19_abukuma_1014dansaizu` | 令和元年台風第19号 浸水推定段彩図 阿武隈川水系（阿武隈川）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜阿武隈川 |
| `20191012typhoon19_shinano_1013dansaizu` | 令和元年台風第19号 浸水推定段彩図 信濃川水系（千曲川）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜千曲川 |
| `20191012typhoon19_kuji_1014dansaizu` | 令和元年台風第19号 浸水推定段彩図 久慈川水系（久慈川）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜久慈川 |
| `20191012typhoon19_naka_1014dansaizu` | 令和元年台風第19号 浸水推定段彩図 那珂川水系（那珂川）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜那珂川 |
| `20191012typhoon19_arakawa_1014dansaizu` | 令和元年台風第19号 浸水推定段彩図 荒川水系（入間川・越辺川・都幾川）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～15｜荒川水系（入間川・越辺川・都幾川） |
| `20190828kyusyu_sagachiku_0830do` | 令和元年8月の前線に伴う大雨 正射画像 佐賀地区（佐賀県佐賀市、唐津市、多久市、伊万里市、武雄市、小城市、嬉野市、大町町、江北町、白石町）佐賀地区（8/30撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜佐賀県佐賀市、唐津市、多久市、伊万里市、武雄市、小城市、嬉野市、大町町、江北町、白石町 |
| `20190828kyusyu_sagachiku_0831do` | 令和元年8月の前線に伴う大雨 正射画像 佐賀地区（佐賀県佐賀市、唐津市、多久市、伊万里市、武雄市、小城市、嬉野市、大町町、江北町、白石町）佐賀地区一部（8/31撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜佐賀県佐賀市、唐津市、多久市、伊万里市、武雄市、小城市、嬉野市、大町町、江北町、白石町 |
| `20190828kyusyu_sagachiku_0830do_sokuho` | 令和元年8月の前線に伴う大雨 正射画像（速報） 佐賀地区（佐賀県佐賀市、唐津市、多久市、伊万里市、武雄市、小城市、嬉野市、大町町、江北町、白石町）佐賀地区（8/30撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜佐賀県佐賀市、唐津市、多久市、伊万里市、武雄市、小城市、嬉野市、大町町、江北町、白石町 |
| `20190828kyusyu_sagachiku_0831do_sokuho` | 令和元年8月の前線に伴う大雨 正射画像（速報） 佐賀地区（佐賀県佐賀市、唐津市、多久市、伊万里市、武雄市、小城市、嬉野市、大町町、江北町、白石町）佐賀地区一部（8/31撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜佐賀県佐賀市、唐津市、多久市、伊万里市、武雄市、小城市、嬉野市、大町町、江北町、白石町 |
| `20190828_kyusyu_0828dansaizu` | 令和元年8月の前線に伴う大雨 浸水推定段彩図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～16｜佐賀県佐賀市、唐津市、多久市、伊万里市、武雄市、小城市、嬉野市、大町町、江北町、白石町 |
| `20190828kyusyu_matsuurakawa_digital` | 令和元年8月の前線に伴う大雨 デジタル標高地形図 松浦川水系松浦川周辺｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～16｜松浦川水系松浦川周辺 |
| `20190828kyusyu_ushidu_digital` | 令和元年8月の前線に伴う大雨 デジタル標高地形図 六角川水系牛津川周辺｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～16｜六角川水系牛津川周辺 |
| `20190828kyusyu_kose_digital` | 令和元年8月の前線に伴う大雨 デジタル標高地形図 筑後川水系巨瀬川周辺｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～16｜筑後川水系巨瀬川周辺 |
| `20190704_kagoshima_chuou_0704do` | 令和元年度6月下旬からの大雨 正射画像 鹿児島中央地区（鹿児島県鹿児島市、日置市、南九州市）（2019年7月4日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜鹿児島県鹿児島市、日置市、南九州市 |
| `20190704_kagoshima_soo_0707do` | 令和元年度6月下旬からの大雨 正射画像 曽於地区（鹿児島県曽於市、霧島市、鹿屋市、志布志市、大崎町、宮崎県都城市）（2019年7月7日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜鹿児島県曽於市、霧島市、鹿屋市、志布志市、大崎町、宮崎県都城市 |
| `201807H3007gouu_iwakuni_0719do` | 平成30年7月豪雨 正射画像 岩国地区（山口県岩国市・周南市など）（2018年7月19日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜山口県岩国市・周南市 |
| `201807H3007gouu_fukuyamahokubu_0718do` | 平成30年7月豪雨 正射画像 福山北部地区（広島県福山市・岡山県井原市など）（2018年7月18日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島県福山市・岡山県井原市など |
| `201807H3007gouu_hijikawa_0718do` | 平成30年7月豪雨 正射画像 肱川地区（愛媛県大洲市）（2018年7月18日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜愛媛県大洲市 |
| `201807H3007gouu_fukuyama_0713do` | 平成30年7月豪雨 正射画像 福山地区（広島県福山市）（2018年7月13,16日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島県福山市 |
| `201807H3007gouu_kuretoubu_0715do` | 平成30年7月豪雨 正射画像 呉東部地区（広島県呉市・東広島市など）（2018年7月15日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島県呉市・東広島市など |
| `201807H3007gouu_miharaonomichi_0715do` | 平成30年7月豪雨 正射画像 三原尾道地区（広島県三原市・尾道市など）（2018年7月15,16日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島県三原市・尾道市など |
| `201807H3007gouu_miharahokubu_0715do` | 平成30年7月豪雨 正射画像 三原北部地区（広島県三原市・府中市など）（2018年7月15日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島県三原市・府中市など |
| `201807H3007gouu_etajima_0716do` | 平成30年7月豪雨 正射画像 江田島地区（広島県江田島市）（2018年7月16日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島県江田島市 |
| `201807H3007gouu_higashihiroshima_0710do` | 平成30年7月豪雨 正射画像 東広島地区（広島県広島市安芸区・東広島市など）（2018年7月10,11,14日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島県広島市安芸区・東広島市など |
| `201807H3007gouu_kuretoubu_0713do` | 平成30年7月豪雨 正射画像 呉東部地区（広島県呉市・東広島市など）（2018年7月13日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島県呉市・東広島市など |
| `201807H3007gouu_takahashigawa_0712do` | 平成30年7月豪雨 正射画像 高梁川地区（岡山県倉敷市・総社市など）（2018年7月12日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜岡山県倉敷市・総社市など |
| `201807H3007gouu_miharaonomichi_0713do` | 平成30年7月豪雨 正射画像 三原尾道地区（広島県三原市・尾道市など）（2018年7月13日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島県三原市・尾道市など |
| `201807H3007gouu_takeharamihara_0712do` | 平成30年7月豪雨 正射画像 竹原三原地区（広島県竹原市・三原市など）（2018年7月10,11,12日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島県竹原市・三原市など |
| `201807H3007gouu_sakachou_0711do` | 平成30年7月豪雨 正射画像 広島坂町地区（広島県広島市・坂町など）（2018年7月9,11日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島県広島市・坂町など |
| `201807H3007gouu_ozu_0711do` | 平成30年7月豪雨 正射画像 大洲地区（愛媛県大洲市・西予市など）（2018年7月11日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜愛媛県大洲市・西予市など |
| `201807H3007gouu_uwajima_0711do` | 平成30年7月豪雨 正射画像 宇和島地区（宇和島市など）（2018年7月11日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜愛媛県宇和島市など |
| `201807H3007gouu_takahashigawa_0711do` | 平成30年7月豪雨 正射画像 高梁川地区（岡山県倉敷市・総社市など）（2018年7月11日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜岡山県倉敷市・総社市など |
| `201807H3007gouu_takahashigawa_0709do` | 平成30年7月豪雨 正射画像 高梁川地区（岡山県倉敷市・総社市など）（2018年7月9日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜岡山県倉敷市・総社市など |
| `201807H3007gouu_takahashigawa_dansaizu` | 平成30年7月豪雨 浸水推定段彩図（空中写真判読版） 高梁川（岡山県倉敷市など）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 6～16｜岡山県倉敷市など |
| `201807H3007gouu_hijikawa_dansaizu` | 平成30年7月豪雨 浸水推定段彩図（空中写真判読版） 肱川（愛媛県大洲市など）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 6～16｜愛媛県大洲市など |
| `201807H3007gouu_kurashiki_0707dansaizu` | 平成30年7月豪雨 浸水推定段彩図（速報版） 岡山県倉敷市（2018年7月7日時点）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 6～16｜岡山県倉敷市 |
| `201807H3007gouu_ozu_0707dansaizu` | 平成30年7月豪雨 浸水推定段彩図（速報版） 愛媛県大洲市（2018年7月7日時点）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 6～16｜愛媛県大洲市 |
| `201807H3007gouu_kurashiki_digital` | 平成30年7月豪雨 デジタル標高地形図 岡山県倉敷市｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 6～16｜岡山県倉敷市 |
| `201807H3007gouu_hokaichiline_1` | 平成30年7月豪雨 崩壊地等分布図（ライン）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～17｜岡山県、広島県、山口県、愛媛県 |
| `20180411_ooita_dosha` | 平成30年大分県中津市土砂災害 正射画像（ヘリ撮影画像（2018年4月11日撮影））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜中津市 |
| `20170705typhoon3_0713dol2` | 平成29年7月九州北部豪雨 正射画像（空中写真（東峰地区）（2017年7月13日撮影））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜東峰地区 |
| `20170705typhoon3_0713dol1` | 平成29年7月九州北部豪雨 正射画像（空中写真（朝倉地区）（2017年7月13日撮影））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜朝倉地区 |
| `20170705typhoon3_0710dol` | 平成29年7月九州北部豪雨 正射画像（ヘリ撮影画像（2017年7月10日撮影））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜日田市小野川周辺 |
| `20170705typhoon3_0708dol1` | 平成29年7月九州北部豪雨 正射画像（ヘリ撮影画像（2017年7月8日撮影））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜朝倉市杷木志波平榎・黒川馬場・佐田疣目・黒川西原・赤谷川・高木・妙見川、東峰村・日田市大肥川付近 |
| `20170705typhoon3_0707dol3` | 平成29年7月九州北部豪雨 正射画像（UAV撮影画像（2017年7月7日撮影））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜朝倉市山田奈良ヶ谷付近 |
| `20170705typhoon3_0707dol` | 平成29年7月九州北部豪雨 正射画像（ヘリ撮影画像（2017年7月7日撮影））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜朝倉市桂川、日田市鶴河内鶴城・小野付近 |
| `20160830typhoon10_0907dol1` | 平成28年台風第10号 岩手県岩泉町安家地区正射画像（2016年9月7日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜岩手県岩泉町 安家地区付近 |
| `20160830typhoon10_1007dol1` | 平成28年台風第10号 岩手県岩泉町穴沢地区正射画像（2016年10月7日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜岩手県岩泉町 穴沢地区付近 |
| `20160830typhoon10_1007dol2` | 平成28年台風第10号 岩手県岩泉町鼠入地区正射画像（2016年10月7日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜岩手県岩泉町 鼠入地区付近 |
| `20160830typhoon10_0907dol2` | 平成28年台風第10号 岩手県岩泉町穴沢地区正射画像（2016年9月7日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜岩手県岩泉町 穴沢地区付近 |
| `20160830typhoon10_0907dol3` | 平成28年台風第10号 岩手県岩泉町鼠入地区正射画像（2016年9月7日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜岩手県岩泉町 鼠入地区付近 |
| `20160820typhoon11_9_0825dol` | 平成28年台風第11号及び第9号 常呂川周辺 正射画像（2016年8月25日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜北海道北見市 常呂川周辺 |
| `20150912dol` | 平成27年9月関東・東北豪雨 大崎地区 正射画像（2015年9月12日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜大崎地区付近 |
| `20150929dol` | 平成27年9月関東・東北豪雨 常総地区 正射画像（2015年9月29日午前撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 14～18｜常総地区付近 |
| `20150915dol` | 平成27年9月関東・東北豪雨 常総地区 正射画像（2015年9月15日午前撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜常総地区付近 |
| `20150913dol` | 平成27年9月関東・東北豪雨 常総地区 正射画像（2015年9月13日午前撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜常総地区付近 |
| `20150911dol2` | 平成27年9月関東・東北豪雨 常総地区 正射画像（2015年9月11日午後撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜常総地区付近 |
| `20150911dol1` | 平成27年9月関東・東北豪雨 常総地区 正射画像（2015年9月11日午前撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜常総地区付近 |
| `20150911dol3` | 平成27年9月関東・東北豪雨 鹿沼地区 正射画像（2015年9月11日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜鹿沼地区付近 |
| `20150911dol4` | 平成27年9月関東・東北豪雨 鬼怒川温泉地区 正射画像（2015年9月11日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜鬼怒川温泉地区付近 |
| `20150911dol5` | 平成27年9月関東・東北豪雨 結城地区 正射画像（2015年9月11日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜結城地区付近 |
| `20140831dol` | 平成26年8月豪雨（広島市内）正射画像（2014年8月30・31日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島市内 |
| `20140830dol` | 平成26年8月豪雨（広島市内）正射画像（2014年8月30日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島市内 |
| `20140828dol` | 平成26年8月豪雨（広島市内）正射画像（2014年8月28日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島市内 |
| `19620000dol` | 平成26年8月豪雨（広島市内）過去の正射画像（1962年）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島市内 |
| `19480000dol` | 平成26年8月豪雨（広島市内）過去の正射画像（1947年～1948年）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島市内 |
| `20140820dol` | 平成26年8月豪雨（広島市安佐南区八木）斜め写真による正射画像（2014年8月撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島市安佐南区八木付近 |
| `20140820dol2` | 平成26年8月豪雨（広島市安佐南区山本）斜め写真による正射画像（2014年8月撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島市安佐南区山本付近 |
| `20140820dol3` | 平成26年8月豪雨（広島市安佐北区可部）斜め写真による正射画像（2014年8月撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜広島市安佐北区可部付近 |
| `20140819dol` | 平成26年8月豪雨（丹波市市島地区）正射画像（2014年8月撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜丹波市市島付近 |
| `20140813dol` | 平成26年台風第12号・第11号の大雨等（北川村）正射画像（2014年8月13日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜北川村付近 |
| `20140711dol` | 平成26年台風第8号及び梅雨前線等（南木曽町）斜め写真による正射画像（2014年7月撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 8～18｜南木曽町付近 |
| `20131017dol2` | 平成25年台風第26号・第27号の大雨（大島町）正射画像（2013年10月28日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18 |
| `20131017dol` | 平成25年台風第26号の大雨（大島町）正射画像（2013年10月17日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18 |
| `201204dol` | 平成25年台風第26号・第27号による大雨（大島町）被災前正射画像（2012年4月撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 8～18 |
| `20130902dol` | 平成25年9月2日に発生した突風 正射画像（2013年9月9日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18 |
| `20130717dol2` | 平成25年7月17日からの大雨 山口地方「須佐地区」正射画像（2013年8月7日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18 |
| `20130717dol` | 平成25年7月17日からの大雨 山口地方「須佐地区」正射画像（2013年7月31日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18 |
| `20180717_sekisyokurittai_tarumae` | 樽前山 赤色立体地図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～18｜樽前山周辺 |
| `H30-H27_tikeihenka_kusatsushiranesan` | 平成30年1月23日噴火前後の地形変化量図（本白根山周辺）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～18｜草津白根山付近 |
| `2018_kazantaisaku_kusatsushirane` | 草津白根山の火山活動 火山災害対策用図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜草津白根山付近 |
| `2018_kazantaisaku_kagamiike` | 草津白根山の火山活動 火山災害対策用図（鏡池周辺）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜草津白根山付近 |
| `20180127kusatsushirane_apsar180127sn` | 草津白根山の火山活動 航空機SAR画像（速報）（2018年1月27日観測（南から北））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜草津白根山付近 |
| `20180127kusatsushirane_apsar180127nesw` | 草津白根山の火山活動 航空機SAR画像（速報）（2018年1月27日観測（北東から南西））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜草津白根山付近 |
| `20180124kusatsushirane_0216uav` | 草津白根山の火山活動 UAV撮影による正射画像（2018年2月16,27日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜草津白根山付近 |
| `20190121_olsorittai_kusatsushiranesan` | 草津白根山の火山活動 平成30年1月23日噴火後のオルソ立体地図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～18｜本白根山周辺および白根山北西部 |
| `20190121_sekisyokurittai_kusatsushiranesan` | 草津白根山の火山活動 平成30年1月23日噴火後の赤色立体地図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～18｜本白根山周辺および白根山北西部 |
| `20180130_kusatsushiranesan_sekishokurittai` | 草津白根山の火山活動 平成30年1月23日噴火前の赤色立体地図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 3～18｜草津白根山付近 |
| `kazantaisaku_ooshima` | 伊豆大島の火山活動 火山災害対策用図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～18｜伊豆大島 |
| `ooshimared` | 伊豆大島 赤色立体地図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～18｜伊豆大島 |
| `kazantaisaku_miyakejima` | 三宅島の火山活動 火山災害対策用図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～18｜三宅島 |
| `sekisyokurittai_miyakejima` | 三宅島 赤色立体地図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～18｜三宅島 |
| `20140928dol` | 御嶽山の噴火活動 斜め写真による正射画像（2014年9月28日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜御嶽山付近 |
| `20140930dol` | 御嶽山の噴火活動 航空機SAR画像（2014年9月30日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜御嶽山付近 |
| `20140929dol2` | 御嶽山の噴火活動 航空機SAR画像（2014年9月29日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜御嶽山付近 |
| `20150911dol` | 口永良部島の火山活動 UAV撮影による正射画像（2015年9月8,11,12日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 14～18｜口永良部島付近 |
| `20150714dol` | 口永良部島の火山活動 UAV撮影による正射画像（2015年7月14日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 14～18｜口永良部島付近 |
| `kuchinoerabured` | 口永良部島の火山活動 赤色立体地図｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～18｜口永良部島 |
| `20180419kirishima_apsar180420nesw` | 霧島山の噴火活動 航空機SAR画像（えびの高原（硫黄山）、2018年4月20日観測（北東から観測した画像））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜新燃岳付近 |
| `20180419kirishima_apsar180420swne` | 霧島山の噴火活動 航空機SAR画像（えびの高原（硫黄山）、2018年4月20日観測（南西から観測した画像））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜新燃岳付近 |
| `20180419kirishima_apsar180226nesw` | 霧島山の噴火活動 航空機SAR画像（えびの高原（硫黄山）、2018年2月26日観測（北東から観測した画像））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜新燃岳付近 |
| `20180419kirishima_apsar180226swne` | 霧島山の噴火活動 航空機SAR画像（えびの高原（硫黄山）、2018年2月26日観測（南西から観測した画像））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜新燃岳付近 |
| `20180309_kazantaisaku_kirishima` | 霧島山の噴火活動 火山災害対策用図（新燃岳周辺）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～18｜新燃岳付近 |
| `20171011kirishima_apsar171012we` | 霧島山の噴火活動 航空機SAR画像（新燃岳、2017年10月12日観測（西から東））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜新燃岳付近 |
| `20171011kirishima_apsar171012ew` | 霧島山の噴火活動 航空機SAR画像（新燃岳、2017年10月12日観測（東から西））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜新燃岳付近 |
| `20171011kirishima_apsar141105we` | 霧島山の噴火活動 航空機SAR画像（新燃岳、2014年11月5日観測（西から東））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜新燃岳付近 |
| `20171011kirishima_apsar141105ew` | 霧島山の噴火活動 航空機SAR画像（新燃岳、2014年11月5日観測（東から西））｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜新燃岳付近 |
| `20180309_sekisyokurittai_kirishima` | 霧島山の噴火活動 赤色立体地図（新燃岳周辺）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2～18｜新燃岳付近 |
| `20230202_nishinoshima_dol` | 西之島付近噴火活動 正射画像（2023年2月2日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西之島付近 |
| `20220119_nishinoshima_dol` | 西之島付近噴火活動 正射画像（2022年1月19日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西之島付近 |
| `20180117dol` | 西之島付近噴火活動 正射画像（2018年1月17日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西之島付近 |
| `20161220dol` | 西之島付近噴火活動 正射画像（2016年12月20日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西之島付近 |
| `20160725dol` | 西之島付近噴火活動 正射画像（2016年7月25日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西之島付近 |
| `20160303dol` | 西之島付近噴火活動 正射画像（2016年3月3日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西之島付近 |
| `20151209dol` | 西之島付近噴火活動 正射画像（2015年12月9日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 13～18｜西之島付近 |
| `20150728dol` | 西之島付近噴火活動 正射画像（2015年7月28日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 14～18｜西之島付近 |
| `20150301doh` | 西之島付近噴火活動 正射画像（2015年3月1日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西之島付近 |
| `20141210doh` | 西之島付近噴火活動 正射画像（2014年12月10日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西之島付近 |
| `20141204doh` | 西之島付近噴火活動 正射画像（2014年12月4日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西之島付近 |
| `20140704dol` | 西之島付近噴火活動 正射画像（2014年7月4日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西之島付近 |
| `20140322dol` | 西之島付近噴火活動 正射画像（2014年3月22日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西之島付近 |
| `20140216doh` | 西之島付近噴火活動 正射画像（2014年2月16日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西之島付近 |
| `20131217doh` | 西之島付近噴火活動 正射画像（2013年12月17日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西之島付近 |
| `20131204doh` | 西之島付近噴火活動 正射画像（2013年12月4日撮影）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 10～18｜西之島付近 |
| `20180117dd5` | 西之島付近噴火活動 標高タイル（2018年1月17日）｜.txt｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 15｜西之島付近 |
| `20160725dd5` | 西之島付近噴火活動 標高タイル（2016年7月25日）｜.txt｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 15｜西之島付近 |
| `20160303dd5` | 西之島付近噴火活動 標高タイル（2016年3月3日）｜.txt｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 15｜西之島付近 |
| `20151209dd5` | 西之島付近噴火活動 標高タイル（2015年12月9日）｜.txt｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 15｜西之島付近 |
| `20150728dd5` | 西之島付近噴火活動 標高タイル（2015年7月28日）｜.txt｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 15｜西之島付近 |
| `20150301dd5` | 西之島付近噴火活動 標高タイル（2015年3月1日）｜.txt｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 15｜西之島付近 |
| `20141204dd5` | 西之島付近噴火活動 標高タイル（2014年12月4日）｜.txt｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 15｜西之島付近 |
| `20140704dd5` | 西之島付近噴火活動 標高タイル（2014年7月4日）｜.txt｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 15｜西之島付近 |
| `20140322dd5` | 西之島付近噴火活動 標高タイル（2014年3月22日）｜.txt｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 15｜西之島付近 |
| `20140216dd5` | 西之島付近噴火活動 標高タイル（2014年2月16日）｜.txt｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 15｜西之島付近 |
| `20131217dd5` | 西之島付近噴火活動 標高タイル（2013年12月17日）｜.txt｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 15｜西之島付近 |
| `shinsaidenshoushisetsu` | 震災伝承施設｜.geojson｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 7｜青森県、岩手県、宮城県、福島県 |
| `rinya` | 森林（国有林）の空中写真（林野庁）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 14～18｜日本全国 |
| `rinya_m` | 森林（民有林）の空中写真｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 14～18｜日本全国 |
| `minato_icon` | みなとオアシス（港湾局）（アイコン）｜.geojson｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2 ※地理院地図サイトでのデータ表示は、以下のズームレベルで行っています。 アイコン：5～9、ポリゴン：10～18｜日本全国 |
| `minato_polygon` | みなとオアシス（港湾局）（ポリゴン）｜.geojson｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 2 ※地理院地図サイトでのデータ表示は、以下のズームレベルで行っています。 アイコン：5～9、ポリゴン：10～18｜日本全国 |
| `gmld_glcnmo2` | 土地被覆（GLCNMO）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 0～7｜全球 |
| `gmld_ptc2` | 植生（樹木被覆率）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 0～7｜全球 |
| `dem1a_png` | 標高タイル（基盤地図情報数値標高モデル）（DEM1A PNG形式）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 1～17（DEM1A） 1～15（DEM5A、DEM5B、DEM5C） 1～14（DEM10B）｜標高モデルの更新情報をご覧ください。 |
| `dem5a_png` | 標高タイル（基盤地図情報数値標高モデル）（DEM5A PNG形式）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 1～17（DEM1A） 1～15（DEM5A、DEM5B、DEM5C） 1～14（DEM10B）｜標高モデルの更新情報をご覧ください。 |
| `dem5b_png` | 標高タイル（基盤地図情報数値標高モデル）（DEM5B PNG形式）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 1～17（DEM1A） 1～15（DEM5A、DEM5B、DEM5C） 1～14（DEM10B）｜標高モデルの更新情報をご覧ください。 |
| `dem5c_png` | 標高タイル（基盤地図情報数値標高モデル）（DEM5C PNG形式）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 1～17（DEM1A） 1～15（DEM5A、DEM5B、DEM5C） 1～14（DEM10B）｜標高モデルの更新情報をご覧ください。 |
| `dem_png` | 標高タイル（基盤地図情報数値標高モデル）（DEM10B PNG形式）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 1～17（DEM1A） 1～15（DEM5A、DEM5B、DEM5C） 1～14（DEM10B）｜標高モデルの更新情報をご覧ください。 |
| `dem5a` | 標高タイル（基盤地図情報数値標高モデル）（DEM5A テキスト形式）｜.txt｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 1～17（DEM1A） 1～15（DEM5A、DEM5B、DEM5C） 1～14（DEM10B）｜標高モデルの更新情報をご覧ください。 |
| `dem5b` | 標高タイル（基盤地図情報数値標高モデル）（DEM5B テキスト形式）｜.txt｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 1～17（DEM1A） 1～15（DEM5A、DEM5B、DEM5C） 1～14（DEM10B）｜標高モデルの更新情報をご覧ください。 |
| `dem` | 標高タイル（基盤地図情報数値標高モデル）（DEM10B テキスト形式）｜.txt｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 1～17（DEM1A） 1～15（DEM5A、DEM5B、DEM5C） 1～14（DEM10B）｜標高モデルの更新情報をご覧ください。 |
| `demgm_png` | 標高タイル（地球地図全球版標高第2版）（PNG形式）｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 0～8 |
| `demgm` | 標高タイル（地球地図全球版標高第2版）（テキスト形式）｜.txt｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 0～8 |
| `lakedepth` | 湖水深タイル｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 14｜湖沼調査を実施した湖沼のうち「湖沼データ」として公開済みの湖沼部（調査実施湖沼一覧を参照）。 |
| `lakedepth_standard` | 基準水面標高タイル｜.png｜2. 基本測量成果以外で出典の記載のみで利用可能なもの｜ZL 14｜湖沼調査を実施した湖沼のうち「湖沼データ」として公開済みの湖沼部（調査実施湖沼一覧を参照）。 |
| `skhb01` | 指定緊急避難場所（洪水）｜.geojson｜3. 上記以外のもの｜ZL 10 ※地理院地図サイトでのデータ表示は、ズームレベル11～18で行っています。｜市町村別公開日・更新日一覧をご覧ください。 |
| `skhb02` | 指定緊急避難場所（崖崩れ、土石流及び地滑り）｜.geojson｜3. 上記以外のもの｜ZL 10 ※地理院地図サイトでのデータ表示は、ズームレベル11～18で行っています。｜市町村別公開日・更新日一覧をご覧ください。 |
| `skhb03` | 指定緊急避難場所（高潮）｜.geojson｜3. 上記以外のもの｜ZL 10 ※地理院地図サイトでのデータ表示は、ズームレベル11～18で行っています。｜市町村別公開日・更新日一覧をご覧ください。 |
| `skhb04` | 指定緊急避難場所（地震）｜.geojson｜3. 上記以外のもの｜ZL 10 ※地理院地図サイトでのデータ表示は、ズームレベル11～18で行っています。｜市町村別公開日・更新日一覧をご覧ください。 |
| `skhb05` | 指定緊急避難場所（津波）｜.geojson｜3. 上記以外のもの｜ZL 10 ※地理院地図サイトでのデータ表示は、ズームレベル11～18で行っています。｜市町村別公開日・更新日一覧をご覧ください。 |
| `skhb06` | 指定緊急避難場所（大規模な火事）｜.geojson｜3. 上記以外のもの｜ZL 10 ※地理院地図サイトでのデータ表示は、ズームレベル11～18で行っています。｜市町村別公開日・更新日一覧をご覧ください。 |
| `skhb07` | 指定緊急避難場所（内水氾濫）｜.geojson｜3. 上記以外のもの｜ZL 10 ※地理院地図サイトでのデータ表示は、ズームレベル11～18で行っています。｜市町村別公開日・更新日一覧をご覧ください。 |
| `skhb08` | 指定緊急避難場所（火山現象）｜.geojson｜3. 上記以外のもの｜ZL 10 ※地理院地図サイトでのデータ表示は、ズームレベル11～18で行っています。｜市町村別公開日・更新日一覧をご覧ください。 |
| `sih` | 指定避難所（一般）｜.geojson｜3. 上記以外のもの｜ZL 10 ※地理院地図サイトでのデータ表示は、ズームレベル11～18で行っています。｜市町村別公開日・更新日一覧をご覧ください。 |
| `sfh` | 指定避難所（福祉）｜.geojson｜3. 上記以外のもの｜ZL 10 ※地理院地図サイトでのデータ表示は、ズームレベル11～18で行っています。｜市町村別公開日・更新日一覧をご覧ください。 |
| `disaster_lore_all` | 自然災害伝承碑（すべて）｜.geojson｜3. 上記以外のもの｜ZL 7｜掲載市区町村一覧をご覧ください。 |
| `disaster_lore_flood` | 自然災害伝承碑（洪水）｜.geojson｜3. 上記以外のもの｜ZL 7｜掲載市区町村一覧をご覧ください。 |
| `disaster_lore_sediment` | 自然災害伝承碑（土砂災害）｜.geojson｜3. 上記以外のもの｜ZL 7｜掲載市区町村一覧をご覧ください。 |
| `disaster_lore_hightide` | 自然災害伝承碑（高潮）｜.geojson｜3. 上記以外のもの｜ZL 7｜掲載市区町村一覧をご覧ください。 |
| `disaster_lore_earthquake` | 自然災害伝承碑（地震）｜.geojson｜3. 上記以外のもの｜ZL 7｜掲載市区町村一覧をご覧ください。 |
| `disaster_lore_tsunami` | 自然災害伝承碑（津波）｜.geojson｜3. 上記以外のもの｜ZL 7｜掲載市区町村一覧をご覧ください。 |
| `disaster_lore_volcano` | 自然災害伝承碑（火山災害）｜.geojson｜3. 上記以外のもの｜ZL 7｜掲載市区町村一覧をご覧ください。 |
| `disaster_lore_other` | 自然災害伝承碑（その他）｜.geojson｜3. 上記以外のもの｜ZL 7｜掲載市区町村一覧をご覧ください。 |

### 取りうる値: `自然災害伝承碑の災害種別 — 一覧ページの備考が列挙している値`

| 値 | 意味 |
|---|---|
| `洪水` |  |
| `土砂災害` |  |
| `高潮` |  |
| `地震` |  |
| `津波` |  |
| `火山災害` |  |
| `その他` |  |

## Jグランツ MCP Server (`jgrants-mcp`)

- 出所: 入力は仕様由来、戻り値は実データ由来
- 抽出方法: 入力項目は MCP のツール定義。戻り値の項目は実レスポンスから列挙し、説明は公式 OpenAPI（補助金情報取得API 1.0）の同名項目から引いた。仕様側のオブジェクト定義も併記している
- 参照元: https://files.microcms-assets.io/assets/7c793323a46a46b7bb9a2ac7d0023301/2bad5ef79255448f8381d9cf2a14dbfc/jgrants-api.yaml

### get_file_content（入力）

保存されたファイルの内容を取得（Markdown形式またはBASE64形式）

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `subsidy_id` | string | 必須 |  |
| `filename` | string | 必須 |  |
| `return_format` | string |  | `markdown` |

### get_subsidy_detail（入力）

補助金の詳細情報を取得し、添付ファイルを自動的にダウンロードします。

| 項目 | 型 | 説明 |
|---|---|---|
| `subsidy_id` | string | 補助金ID（例: "a0WJ200000CDR9HMAX"） |

### get_subsidy_overview（入力）

補助金の最新状況を把握します。締切期間別、金額規模別の集計を提供。

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `output_format` | string | 出力形式 ("json" または "csv")。デフォルトは "json" | `json` |

### ping（入力）

サーバーの応答を確認するためのユーティリティ。

| 項目 | 型 | 説明 |
|---|---|---|

### search_subsidies（入力）

高度な検索条件で補助金を検索します。

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `keyword` | string | 必須 |  |
| `use_purpose` | string |  | `None` |
| `industry` | string |  | `None` |
| `target_number_of_employees` | string |  | `None` |
| `target_area_search` | string |  | `None` |
| `sort` | string |  | `acceptance_end_datetime` |
| `order` | string |  | `ASC` |
| `acceptance` | integer |  | `1` |

### search_subsidies の戻り値（subsidies[]）

検索にヒットした補助金 1 件分。説明は公式 OpenAPI の同名項目から引いている。

| 項目 | 型 | 説明 |
|---|---|---|
| `acceptance_end_datetime` | string | 募集終了日時（Acceptance end date） |
| `acceptance_start_datetime` | string | 募集開始日時（Acceptance start date） |
| `id` | string |  |
| `institution_name` | null | 制度名（Institution name） / サンプル内では常に null |
| `name` | string |  |
| `subsidy_max_limit` | number | 補助額上限（Subsidy maximum amount） 入力値以下の補助額上限が設定されている補助金に絞り込む。 |
| `target_area_search` | string |  |
| `target_number_of_employees` | string | 従業員数（Number of employees） |
| `title` | string |  |

### get_subsidy_detail の戻り値

補助金 1 件の詳細。files は MCP サーバーが添付を保存した結果で、公式 API には無い項目。

| 項目 | 型 | 説明 |
|---|---|---|
| `acceptance_end` | string |  |
| `acceptance_start` | string |  |
| `application_url` | null | サンプル内では常に null |
| `description` | string |  |
| `files` | object |  |
| `id` | string |  |
| `last_updated` | null | サンプル内では常に null |
| `save_directory` | string |  |
| `status` | string |  |
| `subsidy_max_limit` | number | 補助額上限（Subsidy maximum amount） 入力値以下の補助額上限が設定されている補助金に絞り込む。 |
| `target` | object |  |
| `title` | string |  |

### file_data（公式 OpenAPI 由来）

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `name` | string | ファイル名（File name） | `ガイドライン.pdf` |
| `data` | string | データ（File data） Base64形式 |  |

### type_1（公式 OpenAPI 由来）

補助金詳細照会結果情報（Result of querying subsidy detail）

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `id` | string | 補助金ID（Subsidy ID） | `S0J0w00wer0wUgr77E` |
| `name` | string | 補助金番号（Subsidy number） | `S-01100011` |
| `title` | string | 補助金名（Subsidy name） | `小規模事業者補助金` |
| `subsidy_catch_phrase` | string | 補助金のキャッチコピー（Advertising slogan） | `小規模事業者の生産性向上と持続的発展を図る` |
| `detail` | string | 補助金のサマリー（Purpose / Overview） | `小規模事業者が取り組む販路開拓等の取組の経費の一部を補助することにより、生産性向上と持続的発展を図ることを目的とします。` |
| `use_purpose` | string | 利用目的（Use of subsidies） 値が複数ある場合は、「 / 」（半角スペース＋半角スラッシュ＋半角スペース）で区切る。 ・新たな事業を行いたい ・販路拡大・海外展開をしたい ・イベント・事業運営支援がほしい ・事業を引き継ぎたい ・研究開発・実証事業を行いたい ・人材育成を行いたい ・資金繰りを改善したい ・設備整備・IT導入をしたい ・雇用・職場環境を改善したい ・エコ・SDGs活動支援がほしい ・災害（自然災害、感染症等）支援がほしい ・教育・子育て・少子化支援がほしい ・スポーツ・文化支援がほしい ・安全・防災対策支援がほしい ・まちづくり・地域振興支援がほしい | `新たな事業を行いたい / 設備整備・IT導入をしたい` |
| `industry` | string | 業種（Industry） 値が複数ある場合は、半角スペース＋半角スラッシュ＋半角スペース）で区切る。 ・農業、林業 ・漁業 ・鉱業、採石業、砂利採取業 ・建設業 ・製造業 ・電気・ガス・熱供給・水道業 ・情報通信業 ・運輸業、郵便業 ・卸売業、小売業 ・金融業、保険業 ・不動産業、物品賃貸業 ・学術研究、専門・技術サービス業 ・宿泊業、飲食サービス業 ・生活関連サービス業、娯楽業 ・教育、学習支援業 ・医療、福祉 ・複合サービス事業 ・サービス業（他に分類されないもの） ・公務（他に分類されるものを除く） ・分類不能の産業 | `情報通信業 / 教育、学習支援業` |
| `target_area_search` | string | 補助対象地域（Target area to search） 値が複数ある場合は、「 / 」（半角スペース＋半角スラッシュ＋半角スペース）で区切る。 ・全国 ・北海道地方 ・東北地方 ・関東・甲信越地方 ・東海・北陸地方 ・近畿地方 ・中国地方 ・四国地方 ・九州・沖縄地方 ・北海道 ・青森県 ・岩手県 ・宮城県 ・秋田県 ・山形県 ・福島県 ・茨城県 ・栃木県 ・群馬県 ・埼玉県 ・千葉県 ・東京都 ・神奈川県 ・新潟県 ・富山県 ・石川県 ・福井県 ・山梨県 ・長野県 ・岐阜県 ・静岡県 ・愛知県 ・三重県 ・滋賀県 ・京都府 ・大阪府 ・兵庫県 ・奈良県 ・和歌山県 ・鳥取県 ・島根県 ・岡山県 ・広島県 ・山口県 ・徳島県 ・香川県 ・愛媛県 ・高知県 ・福岡県 ・佐賀県 ・長崎県 ・熊本県 ・大分県 ・宮崎県 ・鹿児島県 ・沖縄県 ・海外 | `東京都 / 大阪府` |
| `target_area_detail` | string | 補助対象地域詳細（Target area detail） | `全国` |
| `target_number_of_employees` | string | 従業員数（Number of employees） | `20名以下` |
| `subsidy_rate` | string | 補助率（Subsidy rate） | `20%` |
| `subsidy_max_limit` | integer | 補助額上限（Subsidy maximum amount） 入力値以下の補助額上限が設定されている補助金に絞り込む。 | `10000000` |
| `acceptance_start_datetime` | string | 募集開始日時（Acceptance start date） | `2020-02-28 16:41:41.090000+00:00` |
| `acceptance_end_datetime` | string | 募集終了日時（Acceptance end date） | `2021-02-28 16:41:41.090000+00:00` |
| `project_end_deadline` | string | 事業終了期限（Project end deadline） | `2020-07-31 15:00:00+00:00` |
| `request_reception_presence` | string | 申請受付有無（Request acceptability） ・有：申請を受付ける ・無：申請を受付けない | `有` |
| `is_enable_multiple_request` | boolean | 複数回申請可否（Multiple requests acceptability） ・true：申請可 ・false：申請不可 | `False` |
| `front_subsidy_detail_page_url` | string | 事業者向け補助金詳細画面URL | `https://jgrants-2-xxx/subsidy/999999999999999999` |
| `application_guidelines` | file_data[] | 公募要領（Application guidelines） | `{'name': '公募要領.pdf', 'data': 'JVBERi0xLjQKJe'}` |
| `outline_of_grant` | file_data[] | 交付要綱.pdf | `{'name': '交付要綱.pdf', 'data': 'JVBERi0xLjQKJe'}` |
| `application_form` | file_data[] | 申請様式（Application form） | `{'name': '申請様式.pdf', 'data': 'JVBERi0xLjQKJe'}` |
| `institution_name` | string | 制度名（Institution name） | `小規模事業者生産性向上支援事業` |

### subsidy-details-response（公式 OpenAPI 由来）

補助金詳細照会結果情報（Result of querying subsidy detail）

| 項目 | 型 | 説明 |
|---|---|---|
| `metadata` | Metadata | API仕様公開URL（API Specification URL） |
| `result` | type_1[] | 補助金詳細照会結果情報（Result of retrieving subsidy detail） |

### type（公式 OpenAPI 由来）

補助金一覧検索結果情報（Result of querying subsidies list）

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `id` | string | 補助金ID（Subsidy ID） | `S0J0w00wer0wUgr77E` |
| `name` | string | 補助金番号（Subsidy number） | `S-01100011` |
| `title` | string | 補助金名（Subsidy name） | `小規模事業者補助金` |
| `target_area_search` | string | 補助対象地域（Target area to search） 値が複数ある場合は、「 / 」（半角スペース＋半角スラッシュ＋半角スペース）で区切る。 ・全国 ・北海道地方 ・東北地方 ・関東・甲信越地方 ・東海・北陸地方 ・近畿地方 ・中国地方 ・四国地方 ・九州・沖縄地方 ・北海道 ・青森県 ・岩手県 ・宮城県 ・秋田県 ・山形県 ・福島県 ・茨城県 ・栃木県 ・群馬県 ・埼玉県 ・千葉県 ・東京都 ・神奈川県 ・新潟県 ・富山県 ・石川県 ・福井県 ・山梨県 ・長野県 ・岐阜県 ・静岡県 ・愛知県 ・三重県 ・滋賀県 ・京都府 ・大阪府 ・兵庫県 ・奈良県 ・和歌山県 ・鳥取県 ・島根県 ・岡山県 ・広島県 ・山口県 ・徳島県 ・香川県 ・愛媛県 ・高知県 ・福岡県 ・佐賀県 ・長崎県 ・熊本県 ・大分県 ・宮崎県 ・鹿児島県 ・沖縄県 ・海外 | `東京都 / 大阪府` |
| `subsidy_max_limit` | number | 補助額上限（Subsidy maximum amount） 入力値以下の補助額上限が設定されている補助金に絞り込む。 | `10000000` |
| `acceptance_start_datetime` | string | 募集開始日時（Acceptance start date） | `2020-02-28 16:41:41.090000+00:00` |
| `acceptance_end_datetime` | string | 募集終了日時（Acceptance end date） | `2021-02-28 16:41:41.090000+00:00` |
| `target_number_of_employees` | string | 従業員数（Number of employees） | `20名以下` |
| `institution_name` | string | 制度名（Institution name） | `小規模事業者生産性向上支援事業` |

### subsidiesRequest（公式 OpenAPI 由来）

| 項目 | 型 | 説明 |
|---|---|---|
| `keyword` | string | 検索キーワード（Keyword for search） 最小文字数は2文字とする（スペース入力不可）。 大文字・小文字や全角・半角の表記ゆれを許容する（例：IoTとIOT、IoTとⅠoＴ、カタカナとｶﾀｶﾅを区別しない）。 |
| `sort` | string | ソート項目名（Field name to order by） ソート項目名で指定した項目をソート順で並替える。 ・created_date：作成日時 ・acceptance_start_datetime：募集開始日時 ・acceptance_end_datetime：募集終了日時 |
| `order` | string | ソート順（Sort order） ソート項目名で指定した項目をソート順で並替える。 ・ASC：昇順 ・DESC：降順 |
| `acceptance` | string | 募集期間内絞込要否（Within an acceptance period） ・0：否 ・1：要 |
| `use_purpose` | string | 利用目的（Use of subsidies） 値が複数ある場合は、「 / 」（半角スペース＋半角スラッシュ＋半角スペース）で区切る。 ・新たな事業を行いたい ・販路拡大・海外展開をしたい ・イベント・事業運営支援がほしい ・事業を引き継ぎたい ・研究開発・実証事業を行いたい ・人材育成を行いたい ・資金繰りを改善したい ・設備整備・IT導入をしたい ・雇用・職場環境を改善したい ・エコ・SDGs活動支援がほしい ・災害（自然災害、感染症等）支援がほしい ・教育・子育て・少子化支援がほしい ・スポーツ・文化支援がほしい ・安全・防災対策支援がほしい ・まちづくり・地域振興支援がほしい |
| `industry` | string | 業種（Industry） 値が複数ある場合は、半角スペース＋半角スラッシュ＋半角スペース）で区切る。 ・農業、林業 ・漁業 ・鉱業、採石業、砂利採取業 ・建設業 ・製造業 ・電気・ガス・熱供給・水道業 ・情報通信業 ・運輸業、郵便業 ・卸売業、小売業 ・金融業、保険業 ・不動産業、物品賃貸業 ・学術研究、専門・技術サービス業 ・宿泊業、飲食サービス業 ・生活関連サービス業、娯楽業 ・教育、学習支援業 ・医療、福祉 ・複合サービス事業 ・サービス業（他に分類されないもの） ・公務（他に分類されるものを除く） ・分類不能の産業 |
| `target_number_of_employees` | string | 従業員数（Number of employees） |
| `target_area_search` | string | 補助対象地域（Target area to search） |
| `institution_name` | string | 制度名（Institution name） |

### subsidy-summaries-response（公式 OpenAPI 由来）

補助金一覧検索結果情報（Result of querying subsidies list）

| 項目 | 型 | 説明 |
|---|---|---|
| `metadata` | Metadata |  |
| `result` | type[] | 補助金一覧検索結果情報（Result of querying subsidies list） |

### ResultFile（公式 OpenAPI 由来）

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `name` | string | ファイル名（File name） | `ガイドライン.pdf` |
| `data` | string | データ（File data） Base64形式 |  |

### Workflow（公式 OpenAPI 由来）

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `id` | string | ワークフローID（id） | `a0GBE000005RJTW2A4` |
| `target_area_search` | string | 補助対象地域（Target area to search） 値が複数ある場合は、「 / 」（半角スペース＋半角スラッシュ＋半角スペース）で区切る。 ・全国 ・北海道地方 ・東北地方 ・関東・甲信越地方 ・東海・北陸地方 ・近畿地方 ・中国地方 ・四国地方 ・九州・沖縄地方 ・北海道 ・青森県 ・岩手県 ・宮城県 ・秋田県 ・山形県 ・福島県 ・茨城県 ・栃木県 ・群馬県 ・埼玉県 ・千葉県 ・東京都 ・神奈川県 ・新潟県 ・富山県 ・石川県 ・福井県 ・山梨県 ・長野県 ・岐阜県 ・静岡県 ・愛知県 ・三重県 ・滋賀県 ・京都府 ・大阪府 ・兵庫県 ・奈良県 ・和歌山県 ・鳥取県 ・島根県 ・岡山県 ・広島県 ・山口県 ・徳島県 ・香川県 ・愛媛県 ・高知県 ・福岡県 ・佐賀県 ・長崎県 ・熊本県 ・大分県 ・宮崎県 ・鹿児島県 ・沖縄県 ・海外 | `東京都 / 大阪府` |
| `target_area_detail` | string | 補助対象地域詳細（Target area detail） | `全国` |
| `fiscal_year_round` | string | 募集名（fiscal_year_round） | `第54回` |
| `acceptance_start_datetime` | string | 募集開始日時（Acceptance start date） | `2020-02-28 16:41:41.090000+00:00` |
| `acceptance_end_datetime` | string | 募集終了日時（Acceptance end date） | `2021-02-28 16:41:41.090000+00:00` |
| `project_end_deadline` | string | 事業終了期限（Project end deadline） | `2020-07-31 15:00:00+00:00` |

### type_1_v2（公式 OpenAPI 由来）

補助金詳細照会結果情報 V2（Result of querying subsidy detail V2）

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `id` | string | 補助金ID（Subsidy ID） | `S0J0w00wer0wUgr77E` |
| `name` | string | 補助金番号（Subsidy number） | `S-01100011` |
| `title` | string | 補助金名（Subsidy name） | `小規模事業者補助金` |
| `subsidy_catch_phrase` | string | 補助金のキャッチコピー（Advertising slogan） | `小規模事業者の生産性向上と持続的発展を図る` |
| `detail` | string | 補助金のサマリー（Purpose / Overview） | `小規模事業者が取り組む販路開拓等の取組の経費の一部を補助することにより、生産性向上と持続的発展を図ることを目的とします。` |
| `use_purpose` | string | 利用目的（Use of subsidies） 値が複数ある場合は、「 / 」（半角スペース＋半角スラッシュ＋半角スペース）で区切る。 ・新たな事業を行いたい ・販路拡大・海外展開をしたい ・イベント・事業運営支援がほしい ・事業を引き継ぎたい ・研究開発・実証事業を行いたい ・人材育成を行いたい ・資金繰りを改善したい ・設備整備・IT導入をしたい ・雇用・職場環境を改善したい ・エコ・SDGs活動支援がほしい ・災害（自然災害、感染症等）支援がほしい ・教育・子育て・少子化支援がほしい ・スポーツ・文化支援がほしい ・安全・防災対策支援がほしい ・まちづくり・地域振興支援がほしい | `新たな事業を行いたい / 設備整備・IT導入をしたい` |
| `industry` | string | 業種（Industry） 値が複数ある場合は、半角スペース＋半角スラッシュ＋半角スペース）で区切る。 ・農業、林業 ・漁業 ・鉱業、採石業、砂利採取業 ・建設業 ・製造業 ・電気・ガス・熱供給・水道業 ・情報通信業 ・運輸業、郵便業 ・卸売業、小売業 ・金融業、保険業 ・不動産業、物品賃貸業 ・学術研究、専門・技術サービス業 ・宿泊業、飲食サービス業 ・生活関連サービス業、娯楽業 ・教育、学習支援業 ・医療、福祉 ・複合サービス事業 ・サービス業（他に分類されないもの） ・公務（他に分類されるものを除く） ・分類不能の産業 | `情報通信業 / 教育、学習支援業` |
| `target_number_of_employees` | string | 従業員数（Number of employees） | `20名以下` |
| `subsidy_rate` | string | 補助率（Subsidy rate） | `20%` |
| `subsidy_max_limit` | integer | 補助額上限（Subsidy maximum amount） 入力値以下の補助額上限が設定されている補助金に絞り込む。 | `10000000` |
| `request_reception_presence` | string | 申請受付有無（Request acceptability） ・有：申請を受付ける ・無：申請を受付けない | `有` |
| `is_enable_multiple_request` | boolean | 複数回申請可否（Multiple requests acceptability） ・true：申請可 ・false：申請不可 | `False` |
| `front_subsidy_detail_page_url` | string | 事業者向け補助金詳細画面URL | `https://jgrants-2-xxx/subsidy/999999999999999999` |
| `granttype` | string | 類型（granttype） | `一般型` |
| `application_guidelines` | ResultFile[] | 公募要領（Application guidelines） | `{'name': '公募要領.pdf', 'data': 'JVBERi0xLjQKJe'}` |
| `outline_of_grant` | ResultFile[] | 交付要綱.pdf | `{'name': '交付要綱.pdf', 'data': 'JVBERi0xLjQKJe'}` |
| `application_form` | ResultFile[] | 申請様式（Application form） | `{'name': '申請様式.pdf', 'data': 'JVBERi0xLjQKJe'}` |
| `workflow` | Workflow[] | ワークフロー（workflow） | `[{'id': 'a0GBE000005RJTW2A4', 'target_area_search': '大分県', 'target_area_detail': '全国', 'fiscal_year_round': '第54回', 'acceptance_start_datetime': '2025-10-01T15:00Z', 'acceptance_end_datetime': '2026-03-21T15:00Z', 'project_end_deadline': '2027-12-31T15:00Z'}]` |
| `institution_name` | string | 制度名（Institution name） | `小規模事業者生産性向上支援事業` |

### subsidy-details-response-v2（公式 OpenAPI 由来）

補助金詳細照会結果情報 V2（Result of querying subsidy detail V2）

| 項目 | 型 | 説明 |
|---|---|---|
| `metadata` | Metadata | API仕様公開URL（API Specification URL） |
| `result` | type_1_v2[] | 補助金詳細照会結果情報（Result of retrieving subsidy detail） |

### Metadata（公式 OpenAPI 由来）

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `type` | string | API仕様公開URL（API Specification URL） | `https://developers.digital.go.jp/documents/jgrants/api/` |
| `resultset` | Resultset |  |  |

### Resultset（公式 OpenAPI 由来）

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `count` | integer | 取得件数（Number of results） | `1` |

### 500-error-response（公式 OpenAPI 由来）

エラー情報（Result of error）

| 項目 | 型 | 説明 | 例 |
|---|---|---|---|
| `type` | string | API仕様公開URL（API Specification URL） | `https://developers.digital.go.jp/documents/jgrants/api/` |
| `errorCode` | string | エラーコード（Error code） ・E-ML-9999：内部サーバエラー | `E-ML-9999` |
| `title` | string | エラータイトル（Error title） | `Internal Server Error` |
| `instance` | string | HTTPリクエストURI（HTTP request URI） | `/api/subsidies` |
