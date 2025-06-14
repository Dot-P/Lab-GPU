# GPU Monitoring to Notion

本ツールは、研究室内の複数GPUサーバにSSHでアクセスし、各GPUの使用状況と使用ユーザーを取得、[Notion](https://www.notion.so/) データベースに記録・可視化します。cronと組み合わせることで、1分ごとの定期監視も可能です。

---

## 🔧 機能概要

- 10台のGPUマシン（例：`GPU1`～`GPU7`, `GPU200`, `GPU201`, `GPU202`）にSSHで接続
- 各マシン内の複数GPUに対して以下を取得：
  - **使用中かどうか**
  - **使用ユーザー（プロセスPIDから取得）**
- Notion APIを用いて**マシン×GPUの組み合わせ単位**で記録
- 取得成功／失敗ステータスとタイムスタンプも記録
- cronで1分ごとに自動実行可能

---

## 📁 データベース構成（Notion）

| マシン名 | GPU番号 | 状態 | 使用ユーザー | 最終更新時刻 | ステータス |
|----------|----------|------|---------------|----------------|------------|
| GPU1     | 0        | 使用中 | alice         | 2025-06-14 13:00 | 成功     |
| GPU1     | 1        | 空き   |               | 2025-06-14 13:00 | 成功     |

> 📝 Notion データベースはスクリプトが自動生成します（初回実行時）。

---

## 🚀 セットアップ手順

### 1. 必要パッケージのインストール

```bash
pip install -r requirements.txt
````

### 2. Notion API トークンの取得

1. [Notion Developers](https://www.notion.so/my-integrations) で Integration を作成
2. Integration トークン（`secret_xxxx...`）をコピー
3. 対象データベースにIntegrationのアクセスを許可

### 3. 環境変数の設定

`.env` ファイルをルートに作成：

```env
NOTION_TOKEN=secret_xxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxx
```

### 4. スクリプトの実行

```bash
python main.py
```

---

## ⏱️ 定期実行（cron設定）

1分ごとに監視したい場合、以下のように `crontab -e` に追記してください：

```cron
* * * * * /usr/bin/python /path/to/main.py
```

---

## 🛠️ ディレクトリ構成

```plaintext
gpu-monitor/
├── main.py               # 実行スクリプト
├── ssh_utils.py          # SSHでGPU情報取得
├── parser.py             # nvidia-smi出力パース
├── notion_client.py      # Notion API操作
├── .env                  # 認証情報
└── requirements.txt      # 必要パッケージ
```

## 🧪 テスト

本リポジトリには `pytest` を用いたユニットテストが含まれています。以下のコマンドで実行できます。

```bash
pytest -q
```

---

## 📝 備考

* SSHは公開鍵認証が前提です（パスワードなし接続）
* `nvidia-smi`と`ps`コマンドを組み合わせて使用ユーザーを特定します
* ローカルログファイルは保存しません

---
