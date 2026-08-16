# 単一利用者向けリモートホスティング

この構成は、Notion などのクラウドMCPクライアントから、公開データを扱う読み取り専用MCPへ安全に接続するためのPoCです。複数利用者・機密データ・書き込み操作を扱う本番環境では、OAuth、利用者別認可、監査ログ、レート制限を備えたMCP Gatewayへ置き換えてください。

## 構成

```text
Notion
  -> HTTPS（SliplaneまたはAWSのマネージド入口）
  -> gateway（Bearer tokenを検証）
  -> mcp-server（同じBearer tokenを再検証）
  -> 行政手続の公開データ
```

- `gateway` だけを公開します。
- `mcp-server` は同じホストのプライベートネットワーク内だけで待ち受けます。
- Tokenは両方のサービスにSecret環境変数として設定します。
- `/health` はデプロイ監視用に認証なしで公開します。MCPツールやデータは返しません。
- MCPエンドポイントは `/mcp` です。

## 必須環境変数

| サービス | 変数 | 値 |
|---|---|---|
| gateway | `MCP_AUTH_TOKEN` | 32文字以上のランダムなSecret |
| gateway | `UPSTREAM_URL` | 非公開MCPの内部URL |
| mcp-server | `MCP_AUTH_TOKEN` | gatewayと同じSecret |
| mcp-server | `ADMIN_PROCEDURES_REQUIRE_AUTH` | `1` |
| mcp-server | `ADMIN_PROCEDURES_TRANSPORT` | `streamable-http` |
| mcp-server | `ADMIN_PROCEDURES_PATH` | `/mcp` |
| mcp-server | `MCP_NO_UI` | `1` |

Tokenはリポジトリ、Docker image、ログ、URLへ入れないでください。

## Sliplane

同じGitHubリポジトリから2つのサービスを同一サーバーへ配置します。

### mcp-server

- Dockerfile: `Dockerfile`
- 公開: オフ
- Protocol: HTTP
- Health check: `/health`
- 環境変数: 上表の `mcp-server` 欄

### gateway

- Dockerfile: `gateway/Dockerfile`
- 公開: オン
- Protocol: HTTP
- Health check: `/health`
- `UPSTREAM_URL`: Sliplaneがmcp-serverへ割り当てた内部ホストとポート
- `MCP_AUTH_TOKEN`: mcp-serverと同じSecret

GitHubのmainブランチへのpushを自動デプロイ対象にします。Notionには、gatewayの管理ドメインに `/mcp` を付けたURLとBearer tokenを登録します。

## ローカル検証

Dockerが利用できる環境で、`.env.example` を `.env` にコピーしてTokenを差し替えます。

```bash
docker compose up --build
curl http://localhost:8080/health
curl -i http://localhost:8080/mcp
curl -i -H "Authorization: Bearer $MCP_AUTH_TOKEN" http://localhost:8080/mcp
```

未認証の `/mcp` は `401`、認証済みのMCPリクエストだけがmcp-serverへ転送されます。

## AWS移行

アプリケーションはSliplane APIやファイルシステムへ依存していません。以下のいずれにも同じ2つのimageと環境変数を移せます。

- Lightsail Container Service: gatewayをpublic endpoint、mcp-serverを内部containerにする
- ECS/Fargate: gatewayだけをALBへ接続し、mcp-serverはprivate subnet/service discoveryに置く
- Lightsail/EC2: `compose.yaml` を利用し、gatewayだけを公開する

AWS側のHTTPS、Secret保管、ログ、予算アラートはAWSの管理サービスへ置き換えます。移行時もNotion側は接続URLとTokenを差し替えるだけです。
