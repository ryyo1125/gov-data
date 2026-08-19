# 取得できる項目の一覧

**このファイルは `registry/build.py` が `results/fields.json` から生成する。**
更新するには `verify/extract_fields.py` を実行してからビルドし直す。

- 生成日時: 2026-08-19T08:24:43+00:00

項目の出所は情報源ごとに違う。**仕様由来**は提供側が定義した正式な項目、
**実データ由来**はレスポンスを実際に読んで列挙したもので、サンプルに現れなかった
項目は落ちている可能性がある。どちらなのかを各節の冒頭に示す。


## e-Gov 法令 API Version 2 (`egov-hourei-api`)

- 出所: 仕様由来（提供側が定義した正式な項目）
- 抽出方法: OpenAPI 2.1.139 の components/schemas
- 参照元: https://laws.e-gov.go.jp/api/2/swagger-ui/lawapi-v2.yaml

### attached_file

| 項目 | 型 | 説明 |
|---|---|---|
| `law_revision_id` | string | 法令ID |
| `src` | string | 法令XML中のFig要素のsrc属性 |
| `updated` | string | 正誤等による更新日時 |

### attached_files_info

| 項目 | 型 | 説明 |
|---|---|---|
| `image_data` | string | 添付ファイルデータ（添付ファイルをフォルダ名pictに収集し、フォルダ全体をZip形式で圧縮したファイルをBase64でエンコードした文字列） |
| `attached_files` | attached_file[] | 添付ファイル一覧 |

### error_info

| 項目 | 型 | 説明 |
|---|---|---|
| `code` | string | エラーコード<br> |
| `message` | string | エラーメッセージ |

### keyword_response

| 項目 | 型 | 説明 |
|---|---|---|
| `total_count` | integer | 指定`keyword`でヒットした総件数 |
| `sentence_count` | integer | レスポンス単位で表示した`sentences`数の総和 |
| `next_offset` | integer | 次指定する`offset`値。末尾まで取得が完了した場合はnull |
| `items` | object[] | 法令ID単位の情報リスト<br> |

### law_data_response

| 項目 | 型 | 説明 |
|---|---|---|
| `attached_files_info` | attached_files_info |  |
| `law_info` | law_info |  |
| `revision_info` | revision_info |  |
| `law_full_text` | object | 法令本文<br><br> |

### law_info

| 項目 | 型 | 説明 |
|---|---|---|
| `law_type` | law_type | 法令種別 |
| `law_id` | string | 法令ID |
| `law_num` | string | 法令番号 |
| `law_num_era` | law_num_era | 法令番号の元号 |
| `law_num_year` | integer | 法令番号の年 |
| `law_num_type` | law_num_type | 法令番号の法令種別 |
| `law_num_num` | string | 法令番号の号数 |
| `promulgation_date` | string | 公布日 |

### law_revisions_response

| 項目 | 型 | 説明 |
|---|---|---|
| `law_info` | law_info |  |
| `revisions` | revision_info[] | 版一覧 |

### laws_response

| 項目 | 型 | 説明 |
|---|---|---|
| `total_count` | integer | 取得件数の上限（`limit`）、何件目から取得するか（`offset`）適用前のリストに含まれる項目数（検索条件にマッチした全件数） |
| `count` | integer | 返却するリスト（取得件数の上限（`limit`）、何件目から取得するか（`offset`）適用後）に含まれる項目数 |
| `next_offset` | integer | 次の何件目から取得するか（`offset`）。末尾まで取得が完了した場合はnull |
| `laws` | object[] | 法令ID単位の法令情報 |

### revision_info

| 項目 | 型 | 説明 |
|---|---|---|
| `law_revision_id` | string | 法令履歴ID |
| `law_type` | law_type | 法令種別 |
| `law_title` | string | 法令名 |
| `law_title_kana` | string | 法令名読み |
| `abbrev` | string | 法令略称 |
| `category` | string | 法令分野分類 |
| `updated` | string | 正誤等による更新日時 |
| `amendment_promulgate_date` | string | 改正法令公布日 |
| `amendment_enforcement_date` | string | 改正法令施行期日（この履歴に対応する改正の施行期日） |
| `amendment_enforcement_comment` | string | 施行期日規定等の参考情報（この履歴に対応する改正の施行期日） |
| `amendment_scheduled_enforcement_date` | string | 擬似的な施行期日（実際の施行期日とは限らない）（この履歴に対応する改正の施行期日） |
| `amendment_law_id` | string | 改正法令の法令ID（この履歴に対応する改正法令） |
| `amendment_law_title` | string | 改正法令名 |
| `amendment_law_title_kana` | string | 改正法令名読み |
| `amendment_law_num` | string | 改正法令番号 |
| `amendment_type` | amendment_type | 改正種別 |
| `repeal_status` | repeal_status | 廃止等の状態 |
| `repeal_date` | string | 廃止日 |
| `remain_in_force` | boolean | 廃止後の効力（`true`:廃止後でも効力を有するもの / `false`:廃止後に効力を有しないもの） |
| `mission` | mission | 新規制定又は被改正法令（`New`）・一部改正法令（`Partial`） |
| `current_revision_status` | current_revision_status | 履歴の状態 |

### 取りうる値が決まっている項目

| 項目 | 値 |
|---|---|
| `amendment_type` | `1`, `3`, `8` |
| `category_cd` | `001`, `002`, `003`, `004`, `005`, `006`, `007`, `008`, `009`, `010`, `011`, `012`, `013`, `014`, `015`, `016`, `017`, `018`, `019`, `020`, `021`, `022`, `023`, `024`, `025`, `026`, `027`, `028`, `029`, `030`, `031`, `032`, `033`, `034`, `035`, `036`, `037`, `038`, `039`, `040`, `041`, `042`, `043`, `044`, `045`, `046`, `047`, `048`, `049`, `050` |
| `current_revision_status` | `CurrentEnforced`, `UnEnforced`, `PreviousEnforced`, `Repeal` |
| `file_type` | `xml`, `json`, `html`, `rtf`, `docx` |
| `law_num_era` | `Meiji`, `Taisho`, `Showa`, `Heisei`, `Reiwa` |
| `law_num_type` | `Constitution`, `Act`, `CabinetOrder`, `ImperialOrder`, `MinisterialOrdinance`, `Rule`, `Misc` |
| `law_type` | `Constitution`, `Act`, `CabinetOrder`, `ImperialOrder`, `MinisterialOrdinance`, `Rule`, `Misc` |
| `mission` | `New`, `Partial` |
| `repeal_status` | `None`, `Repeal`, `Expire`, `Suspend`, `LossOfEffectiveness` |
| `response_format` | `json`, `xml` |

## e-Gov データポータル（CKAN API） (`egov-data-catalog`)

- 出所: 実データ由来（レスポンスを読んで列挙。網羅の保証は無い）
- 抽出方法: package_search で取得した 20 件のデータセットに現れた項目の和
- 参照元: https://data.e-gov.go.jp/data/api/3/action/package_search

### package（データセット）

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
| `frequency_of_update` | string |  |
| `groups` | array |  |
| `history_information` | string |  |
| `id` | string |  |
| `index_id` | string |  |
| `isopen` | boolean |  |
| `landingPage` | string |  |
| `language` | string |  |
| `license_id` | null | サンプル内では常に null |
| `license_title` | null | サンプル内では常に null |
| `local_government` | string |  |
| `maintainer` | null | サンプル内では常に null |
| `maintainer_email` | null | サンプル内では常に null |
| `metadata_created` | string |  |
| `metadata_modified` | string |  |
| `name` | string |  |
| `notes` | string |  |
| `num_resources` | number |  |
| `num_tags` | number |  |
| `opendata_id` | string |  |
| `organization` | object |  |
| `owner_org` | string |  |
| `private` | boolean |  |
| `provider_last_modified_date` | string |  |
| `provider_metadata_modified` | string |  |
| `publisher` | string |  |
| `related_documents` | string |  |
| `relationships_as_object` | array |  |
| `relationships_as_subject` | array |  |
| `resources` | array |  |
| `spatial` | string |  |
| `state` | string |  |
| `subtitle` | string |  |
| `tags` | array |  |
| `temporal` | string |  |
| `title` | string |  |
| `type` | string |  |
| `url` | null | サンプル内では常に null |
| `version` | string |  |

### resource（データセットに紐づくファイル）

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
| `language` | string |  |
| `last_modified` | null | サンプル内では常に null |
| `last_modified_date` | string |  |
| `license_id` | string |  |
| `metadata_modified` | string |  |
| `mimetype` | string |  |
| `mimetype_inner` | null | サンプル内では常に null |
| `name` | string |  |
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

- 出所: 実データ由来（レスポンスを読んで列挙。網羅の保証は無い）
- 抽出方法: 4 本のフィードと、それぞれの先頭 entry が指す電文 4 通を実際に読んで列挙。電文種別は多数あり、ここに出るのはその一部
- 参照元: https://www.data.jma.go.jp/developer/xml/feed

### Atom フィード

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

### 電文: 気象警報・注意報（Ｒ０６）（集約通報）（regular フィードより）

| 項目 | 型 | 説明 |
|---|---|---|
| `Report/Control` | element |  |
| `Report/Control/Title` | element |  |
| `Report/Control/DateTime` | element |  |
| `Report/Control/Status` | element |  |
| `Report/Control/EditorialOffice` | element |  |
| `Report/Control/PublishingOffice` | element |  |
| `Report/Head` | element |  |
| `Report/Head/Title` | element |  |
| `Report/Head/ReportDateTime` | element |  |
| `Report/Head/TargetDateTime` | element |  |
| `Report/Head/EventID` | element |  |
| `Report/Head/InfoType` | element |  |
| `Report/Head/Serial` | element |  |
| `Report/Head/InfoKind` | element |  |
| `Report/Head/InfoKindVersion` | element |  |
| `Report/Head/Headline` | element |  |
| `Report/Head/Headline/Text` | element |  |
| `Report/Head/Headline/Information` | element |  |
| `Report/Body` | element |  |
| `Report/Body/Warning` | element |  |
| `Report/Body/Warning/Item` | element |  |

### 電文: 気象特別警報・警報・注意報（extra フィードより）

| 項目 | 型 | 説明 |
|---|---|---|
| `Report/Control` | element |  |
| `Report/Control/Title` | element |  |
| `Report/Control/DateTime` | element |  |
| `Report/Control/Status` | element |  |
| `Report/Control/EditorialOffice` | element |  |
| `Report/Control/PublishingOffice` | element |  |
| `Report/Head` | element |  |
| `Report/Head/Title` | element |  |
| `Report/Head/ReportDateTime` | element |  |
| `Report/Head/TargetDateTime` | element |  |
| `Report/Head/EventID` | element |  |
| `Report/Head/InfoType` | element |  |
| `Report/Head/Serial` | element |  |
| `Report/Head/InfoKind` | element |  |
| `Report/Head/InfoKindVersion` | element |  |
| `Report/Head/Headline` | element |  |
| `Report/Head/Headline/Text` | element |  |
| `Report/Head/Headline/Information` | element |  |
| `Report/Body` | element |  |
| `Report/Body/Notice` | element |  |
| `Report/Body/Warning` | element |  |
| `Report/Body/Warning/Item` | element |  |

### 電文: 降灰予報（定時）（eqvol フィードより）

| 項目 | 型 | 説明 |
|---|---|---|
| `Report/Control` | element |  |
| `Report/Control/Title` | element |  |
| `Report/Control/DateTime` | element |  |
| `Report/Control/Status` | element |  |
| `Report/Control/EditorialOffice` | element |  |
| `Report/Control/PublishingOffice` | element |  |
| `Report/Head` | element |  |
| `Report/Head/Title` | element |  |
| `Report/Head/ReportDateTime` | element |  |
| `Report/Head/TargetDateTime` | element |  |
| `Report/Head/ValidDateTime` | element |  |
| `Report/Head/EventID` | element |  |
| `Report/Head/InfoType` | element |  |
| `Report/Head/Serial` | element |  |
| `Report/Head/InfoKind` | element |  |
| `Report/Head/InfoKindVersion` | element |  |
| `Report/Head/Headline` | element |  |
| `Report/Head/Headline/Text` | element |  |
| `Report/Head/Headline/Information` | element |  |
| `Report/Body` | element |  |
| `Report/Body/VolcanoInfo` | element |  |
| `Report/Body/VolcanoInfo/Item` | element |  |
| `Report/Body/AshInfos` | element |  |
| `Report/Body/AshInfos/AshInfo` | element |  |
| `Report/Body/VolcanoInfoContent` | element |  |
| `Report/Body/VolcanoInfoContent/VolcanoHeadline` | element |  |
| `Report/Body/VolcanoInfoContent/VolcanoActivity` | element |  |
| `Report/Body/VolcanoInfoContent/VolcanoPrevention` | element |  |

### 電文: 地方海上警報（Ｈ２８）（other フィードより）

| 項目 | 型 | 説明 |
|---|---|---|
| `Report/Control` | element |  |
| `Report/Control/Title` | element |  |
| `Report/Control/DateTime` | element |  |
| `Report/Control/Status` | element |  |
| `Report/Control/EditorialOffice` | element |  |
| `Report/Control/PublishingOffice` | element |  |
| `Report/Head` | element |  |
| `Report/Head/Title` | element |  |
| `Report/Head/ReportDateTime` | element |  |
| `Report/Head/TargetDateTime` | element |  |
| `Report/Head/ValidDateTime` | element |  |
| `Report/Head/EventID` | element |  |
| `Report/Head/InfoType` | element |  |
| `Report/Head/Serial` | element |  |
| `Report/Head/InfoKind` | element |  |
| `Report/Head/InfoKindVersion` | element |  |
| `Report/Head/Headline` | element |  |
| `Report/Head/Headline/Text` | element |  |
| `Report/Head/Headline/Information` | element |  |
| `Report/Body` | element |  |
| `Report/Body/Warning` | element |  |
| `Report/Body/Warning/Item` | element |  |
| `Report/Body/MeteorologicalInfos` | element |  |
| `Report/Body/MeteorologicalInfos/MeteorologicalInfo` | element |  |

## Jグランツ MCP Server (`jgrants-mcp`)

- 出所: 入力は仕様由来、戻り値は実データ由来
- 抽出方法: 入力項目は MCP のツール定義、戻り値の項目は実レスポンスから列挙
- 参照元: http://127.0.0.1:8321/mcp

### search_subsidies（入力）

| 項目 | 型 | 説明 |
|---|---|---|
| `keyword` | string | 必須 |
| `use_purpose` | string |  |
| `industry` | string |  |
| `target_number_of_employees` | string |  |
| `target_area_search` | string |  |
| `sort` | string |  |
| `order` | string |  |
| `acceptance` | integer |  |

### ping（入力）

| 項目 | 型 | 説明 |
|---|---|---|

### get_subsidy_overview（入力）

| 項目 | 型 | 説明 |
|---|---|---|
| `output_format` | string |  |

### get_subsidy_detail（入力）

| 項目 | 型 | 説明 |
|---|---|---|
| `subsidy_id` | string | 必須 |

### get_file_content（入力）

| 項目 | 型 | 説明 |
|---|---|---|
| `subsidy_id` | string | 必須 |
| `filename` | string | 必須 |
| `return_format` | string |  |

### search_subsidies の戻り値（subsidies[]）

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
