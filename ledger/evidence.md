# 証拠レジスタ

台帳の `evidence_ref` が指す実際の証拠。**証拠のない行は台帳に入れない**ためのバックエンド。

## EV-AJO — awesome-japan-opendata（第三者キュレーション）

- 種別: **E1 二次情報**（有志コミュニティによるリンク集。一次情報ではない）
- 取得方法: `git clone --depth 1 https://github.com/japan-opendata/awesome-japan-opendata.git`
- 取得日: 2026-08-19 / 参照ファイル: `README.md`（631行）
- 位置づけ: **候補の発見源として有用だが、記載内容の正確性は保証されない。**
  ここから拾った情報は必ず一次情報（E2）での裏取りが要る。

## EV-WS — WebSearch 結果要約（第三者・要約経由）

- 種別: **E1 二次情報（さらに要約が挟まる分、EV-AJO より弱い）**
- 実施日: 2026-08-19
- 位置づけ: 検索エンジンの要約を経由しており、原文にあたっていない。
  **候補の存在を知る用途に限定し、仕様・頻度・ライセンスの根拠にしてはならない。**

## EV-JG-MCP — Jグランツ公式MCPサーバー 実行確認

- 種別: **E3 実行確認（部分成功）**
- 実施日時: 2026-08-19T03:04Z / 実行環境: `ENV-CCR-01`（下記）
- 手順と結果: `docs/2026-08-19-jgrants-mcp-verification.md`
- 成功: MCPハンドシェイク / `tools/list`（5ツール）/ `resources/list` / `ping`
- 失敗: `search_subsidies` → `403 Forbidden`（**API本体ではなく実行環境の egress 拒否**）

## 実行環境の定義

### ENV-CCR-01 — Claude Code リモートコンテナ（本セッション）

- Python 3.11.15 / fastmcp 3.4.7
- 全HTTPS通信が egress ポリシープロキシ経由
- **`.go.jp` ドメインを全面遮断**（2026-08-19 実測。curl・WebFetch とも CONNECT 403）
  - 遮断確認済: `api.e-stat.go.jp` `www.e-stat.go.jp` `laws.e-gov.go.jp` `elaws.e-gov.go.jp`
    `api.jgrants-portal.go.jp` `www.mlit.go.jp` `api.houjin-bangou.nta.go.jp`
    `www.hokeniryo.go.jp` `kouseikyoku.mhlw.go.jp` `www.mhlw.go.jp` `data.go.jp`
    `www.jma.go.jp` `opendata.resas-portal.go.jp` `www.reinfolib.mlit.go.jp` `ndlsearch.ndl.go.jp`
- 到達可能: `github.com` / `pypi.org` / WebSearch（Anthropic側）
- **帰結: この環境では日本政府の一次情報に一切到達できない。
  よって現時点で E2（一次情報の直接確認）は原理的に取得不可能であり、
  E3 は GitHub 上のMCPサーバー実装に対してのみ成立する。**
