# 実行環境の egress 設定手順

本プロジェクトは日本政府の一次情報に到達できないと検証が進まない（`ledger/evidence.md`
の `ENV-CCR-01` 参照）。到達可能にするための設定手順。

出典: [Configure cloud environments](https://code.claude.com/docs/en/cloud-environments)（2026-08-19 参照）

## 前提: 現在の遮断理由

クラウドセッションは **cloud environment** の設定でネットワークが制御される。
既定は **Trusted**（パッケージレジストリ・GitHub 等の既定許可リストのみ）。
`.go.jp` はこの既定リストに無いため、全面的に遮断される。

## 手順

1. [claude.ai/code](https://claude.ai/code) を開く
2. メッセージ入力欄の**上の行にあるクラウドアイコン**（現在の環境名が表示されている）を選択。
   → 環境セレクタが開く。**専用の設定ページや直接URLは存在しない**
3. 既存環境（`Default` 等）にホバーして右端に出る**歯車アイコン**を選択。
   既定環境を変えたくない場合は **Add cloud environment** で本プロジェクト専用の環境を新規作成する（推奨）
4. ダイアログの **Network access** を **Custom** にする

   | レベル | 挙動 |
   |---|---|
   | None | セッションのネットワークからの外部接続なし |
   | Trusted（既定） | 既定許可リストのみ（パッケージレジストリ・GitHub・クラウドSDK） |
   | Full | 任意のドメイン |
   | **Custom** | **自前の許可リスト。既定リストの併用も可** |

5. **Allowed domains** に**1行1ドメイン**で記入（下記リスト参照）。先頭 `*.` でサブドメイン全体にマッチ
6. **Also include default list of common package managers** に**必ずチェック**を入れる。
   外すと PyPI に到達できず、MCPサーバーの依存インストールが失敗する
7. 保存し、**新しいセッションを開始する**

### 反映タイミングの注意

ドキュメントに明記があるのは「環境変数はセッション開始時に一度読み込まれ、
**実行中のセッションには反映されない**」という点。ネットワーク許可リストについては
明示の記載が無いため、**新セッションで開始するのが確実**。
なお許可ホストを変更するとセットアップスクリプトが再実行され、キャッシュが再構築される。

## 許可ドメインリスト

### 案A: 最小構成（医療系補助金MVP + 台帳の一次情報検証）

```text
api.jgrants-portal.go.jp
www.jgrants-portal.go.jp
developers.digital.go.jp
api-catalog.e-gov.go.jp
kouseikyoku.mhlw.go.jp
www.mhlw.go.jp
api.e-stat.go.jp
www.e-stat.go.jp
laws.e-gov.go.jp
elaws.e-gov.go.jp
www.data.go.jp
data.go.jp
```

### 案B: 広め（台帳の候補20件すべてを検証対象にする場合）

```text
*.go.jp
```

日本政府ドメイン全体を許可する。本プロジェクトの対象がまさにそれなので実用的だが、
「必要最小限」の原則からは外れる。**まず案Aで始め、必要になった行を足していくのを推奨**
（どのドメインをいつ足したかが、そのまま台帳の検証履歴になる）。

### 補足

- **GitHub 通信はこの許可リストとは独立**の専用プロキシを通るため、記載不要
- **MCPコネクタの通信も対象外**（Anthropic のサーバー経由のため）
- Artifacts を使う場合は `*.frame.claudeusercontent.com` を追加

## 組織共有環境の場合

管理者が作成した**共有環境**を使っている場合、編集は
[claude.ai/admin-settings](https://claude.ai/admin-settings) の **Cloud environments** ページから、
Owner / 管理者のみが行える。組織横断の許可リストを管理者が全員に配る仕組みは無く、
**環境ごとに個別のリストを持つ**。

## 設定後にやること

`ledger/evidence.md` の `ENV-CCR-01` に対して、新しい環境IDを別項目として起こす
（例: `ENV-CCR-02` — `.go.jp` 許可済み）。**環境が変われば同じ手順でも結果が変わるため、
過去の E3 記録を上書きしてはいけない。**
