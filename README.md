# gov-data

日本政府公式・および信頼性の高いデータ提供サービスの**情報源台帳**。

提供元・提供方式・情報の種類と形式・更新頻度・接続手順を記録する。ただの一覧ではなく、
**すべてのエントリが再実行可能な検証スクリプトと対になっている**ことが特徴。

## 設計の核

台帳は放っておくと腐り、腐ったことに誰も気づけない。それを防ぐために次の 3 つを守る。

1. **検証ステータスは手で書けない。** `registry/sources/*.yaml` に書けるのは事実と、
   検証を再現するためのポインタだけ。合否・検証日・所要時間は `registry/build.py` が
   `results/` の実行結果から導出する。`status:` を手書きしようとするとビルドが落ちる。
2. **主張には必ず根拠が要る。** `findings` は `claim` と `evidence` の組でしか書けない。
   スキーマがそれを強制する。
3. **「なし」と「不明」を区別する。** 一次資料に記述がない項目は `undocumented`。
   到達できないホストを「存在しない」と書かない。

## 台帳

台帳の中身は [docs/REGISTRY.md](docs/REGISTRY.md)（人間向け）と `registry/registry.json`（機械向け）。
各情報源から実際に取得できる項目は [docs/FIELDS.md](docs/FIELDS.md)。
いずれも `registry/build.py` の生成物なので、ここに一覧を再掲しない — 二重管理は必ずずれる。

## 使い方

```bash
# 全情報源を再検証し、台帳を再生成する
./verify/run_all.sh

# 台帳の生成物が最新かだけ確認する（CI 向け）
.work/toolvenv/bin/python registry/build.py --check
```

前提: `git`、`uv`、Python 3.11 以上。

## 構成

```
.claude/skills/gov-data-registry/  エントリ追加手順のスキル
registry/schema.json          台帳エントリのスキーマ。手書き禁止フィールドをここで縛る
registry/sources/*.yaml       台帳エントリ（1 エンドポイント 1 ファイル、人が書く）
registry/blocked.yaml         到達不能で登録できなかった候補の待避所
registry/build.py             検証 + 生成。status は results/ からのみ導出する
registry/registry.json        生成物（機械向け）
docs/REGISTRY.md              生成物（人間向け）。情報源の一覧と検証状況
docs/FIELDS.md                生成物。各情報源から取得できる項目の一覧
verify/_report.py             検証スクリプト共通の実行記録ユーティリティ
verify/verify_*.py            情報源ごとの検証スクリプト
verify/verify_reachability.py 全ホストの到達性を実測。egress の変化を検知する
verify/extract_fields.py      取得できる項目を仕様と実データから抽出する
verify/run_all.sh             全情報源の再検証 + 台帳再生成
results/*.json                検証の生ログ。台帳の status の唯一の根拠
docs/jgrants-mcp-verification.md  jGrants MCP の詳細な検証レポート
```

## エントリの追加手順

1. `verify/verify_<id>.py` を書く。`verify/_report.py` の `Reporter` を使い、
   `results/<id>.json` に同じ形の JSON を出す
2. 実行して結果を得る（**実行していない手順は台帳に書かない**）
3. `registry/sources/<id>.yaml` を書く。分からないことは `undocumented` と書く
4. `registry/build.py` を実行する。スキーマ違反や結果との不整合はここで落ちる

自環境から到達できない場合は 1 の前で止まり、`registry/blocked.yaml` に候補として
記録する。二次情報だけを根拠にエントリを書かない。

## 出典

台帳および検証結果に含まれる補助金データは、デジタル庁が運用する
Jグランツ（jGrants）の公開 API から取得したものです。
