# 取得できる項目の一覧

**このファイルは `registry/build.py` が `results/fields.json` から生成する。**
更新するには `verify/extract_fields.py` を実行してからビルドし直す。

- 生成日時: 2026-08-19T09:10:08+00:00

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
| `author` | string | 作成者 |
| `author_email` | null | サンプル内では常に null |
| `compliant_standard` | string |  |
| `contactPoint` | string | 連絡先 |
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
| `spatial` | string |  |
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
| `resource_id` | string |  |
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

### 電文 Body: 気象警報・注意報（Ｈ２７）（実データ由来 / extra フィード）

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
| `Report/Body/Notice` | 要素 |  |
| `Report/Body/Warning` | 要素 |  |
| `Report/Body/Warning/Item` | 要素 |  |
| `Report/Body/MeteorologicalInfos` | 要素 |  |
| `Report/Body/MeteorologicalInfos/TimeSeriesInfo` | 要素 |  |

### 電文 Body: 降灰予報（定時）（実データ由来 / eqvol フィード）

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
| `Report/Head/ValidDateTime` | 要素 |  |
| `Report/Head/EventID` | 要素 |  |
| `Report/Head/InfoType` | 要素 |  |
| `Report/Head/Serial` | 要素 |  |
| `Report/Head/InfoKind` | 要素 |  |
| `Report/Head/InfoKindVersion` | 要素 |  |
| `Report/Head/Headline` | 要素 |  |
| `Report/Head/Headline/Text` | 要素 |  |
| `Report/Head/Headline/Information` | 要素 |  |
| `Report/Body` | 要素 |  |
| `Report/Body/VolcanoInfo` | 要素 |  |
| `Report/Body/VolcanoInfo/Item` | 要素 |  |
| `Report/Body/AshInfos` | 要素 |  |
| `Report/Body/AshInfos/AshInfo` | 要素 |  |
| `Report/Body/VolcanoInfoContent` | 要素 |  |
| `Report/Body/VolcanoInfoContent/VolcanoHeadline` | 要素 |  |
| `Report/Body/VolcanoInfoContent/VolcanoActivity` | 要素 |  |
| `Report/Body/VolcanoInfoContent/VolcanoPrevention` | 要素 |  |

### 電文 Body: 地方海上警報（Ｈ２８）（実データ由来 / other フィード）

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
| `Report/Head/ValidDateTime` | 要素 |  |
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
| `Report/Body/MeteorologicalInfos` | 要素 |  |
| `Report/Body/MeteorologicalInfos/MeteorologicalInfo` | 要素 |  |

## Jグランツ MCP Server (`jgrants-mcp`)

- 出所: 入力は仕様由来、戻り値は実データ由来
- 抽出方法: 入力項目は MCP のツール定義（説明も定義に書かれているもの）。戻り値の項目は実レスポンスから列挙。公式 OpenAPI 仕様 jgrants-api.yaml は microCMS のアセット CDN にあり、当環境の egress ポリシーで取得できないため未反映
- 参照元: http://127.0.0.1:8321/mcp

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

検索にヒットした補助金 1 件分。詳細は id を get_subsidy_detail に渡して取る。

| 項目 | 型 | 説明 |
|---|---|---|
| `acceptance_end_datetime` | string |  |
| `acceptance_start_datetime` | string |  |
| `id` | string |  |
| `institution_name` | null | サンプル内では常に null |
| `name` | string |  |
| `subsidy_max_limit` | number |  |
| `target_area_search` | string |  |
| `target_number_of_employees` | string |  |
| `title` | string |  |

### get_subsidy_detail の戻り値

補助金 1 件の詳細。files に添付ファイルの保存結果が入る。

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
| `subsidy_max_limit` | number |  |
| `target` | object |  |
| `title` | string |  |
