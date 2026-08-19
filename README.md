# gov-data

日本政府公式MCPの接続と利用の検証。

## 検証済み

| 対象 | 提供元 | 結果 |
|---|---|---|
| [Jグランツ MCP Server](https://github.com/digital-go-jp/jgrants-mcp-server) | デジタル庁 | 接続・全 5 ツールの実行に成功 → [レポート](docs/jgrants-mcp-verification.md) |

## 使い方

```bash
# Jグランツ MCP Server を取得・起動して検証を実行する
./verify/run_jgrants_verification.sh
```

前提: `git`、`uv`、Python 3.11 以上。
サーバー本体は `.work/`（gitignore 済み）に clone され、結果は
`results/jgrants-verification.json` に書き出される。

サーバーを自分で起動済みなら、検証スクリプトだけを実行することもできる。

```bash
python verify/verify_jgrants_mcp.py --url http://127.0.0.1:8000/mcp
```

## 構成

```
verify/verify_jgrants_mcp.py        MCP クライアントとして接続し全ツールを実行する検証スクリプト
verify/run_jgrants_verification.sh  clone〜起動〜検証を通しで行うランナー
docs/jgrants-mcp-verification.md    検証レポート（結果・所見・egress の状況）
results/jgrants-verification.json   検証の生ログ（各ステップの成否・所要時間・戻り値）
```

## 出典

本リポジトリの検証結果に含まれる補助金データは、デジタル庁が運用する
Jグランツ（jGrants）の公開 API から取得したものです。
