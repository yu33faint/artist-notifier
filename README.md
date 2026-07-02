# Spotify Artist Auto-Notifier

## プロジェクト概要

Spotifyで監視対象アーティストの最新リリースを定期的に確認し、
新着を検知したときにLINEへ通知するフルスタックWebアプリケーションです。

React製の管理画面から、監視アーティストの登録・削除と、
新着リリースの手動チェックを行えます。

## 主な機能

- Spotify APIを使用したアーティスト検索・登録
- 監視アーティストの一覧表示・削除
- APSchedulerによる1時間ごとの自動新着チェック
- 管理画面からの手動新着チェック
- LINE Messaging APIによる新着通知
- SQLAlchemyを使用した監視アーティスト・通知済みリリースの記録
- 環境変数によるデータベース接続URLの切り替え
- LINE通知失敗時に次回のチェックで再通知する仕組み

## 技術スタック

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- APScheduler
- Spotipy
- SQLite
- PostgreSQL

### Frontend

- React
- TypeScript
- Vite
- ESLint

### External API

- Spotify Web API
- LINE Messaging API

### Development

- Docker Compose

## アーキテクチャ

```text
backend/app/
├── api/           # FastAPIのエンドポイント
├── models/        # SQLAlchemyのDBモデル
├── repositories/  # DB操作を担当する層
├── schemas/       # リクエストデータの定義
├── services/      # Spotify・LINE通知・新着確認処理
├── database.py    # SQLAlchemy接続とテーブル初期化
└── main.py        # FastAPIアプリとスケジューラー

frontend/src/
├── App.tsx     # 管理画面
├── main.tsx    # Reactエントリーポイント
└── types.ts    # TypeScript型定義
```

バックグラウンドの自動チェックと、管理画面からの手動チェックは、
同じ新着確認サービスを利用します。

API層とサービス層からDB操作を分離し、repositories層でSQLAlchemyを使用してデータを操作しています。
現在はSQLiteをデフォルトとして動作し、`DATABASE_URL`を変更することでPostgreSQLにも接続できる構成にしています。
PostgreSQL利用時のテーブル作成・変更管理にはAlembicを使用します。

## ローカル環境でのセットアップ

### 1. リポジトリをクローンする

```powershell
git clone https://github.com/yu33faint/artist-notifier.git
cd artist-notifier
```

---

### 2. Python仮想環境を作成する

Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS・Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 環境変数を設定する

プロジェクト直下に`.env`を作成し、次の値を設定します。

```env
SPOTIPY_CLIENT_ID=SpotifyのクライアントID
SPOTIPY_CLIENT_SECRET=Spotifyのクライアントシークレット
LINE_CHANNEL_ACCESS_TOKEN=LINE Messaging APIのチャネルアクセストークン
LINE_USER_ID=通知先のLINEユーザーID
DATABASE_URL=sqlite:///./notifier.db
VITE_API_BASE_URL=http://localhost:8000
```

`.env`には秘密情報が含まれるため、Gitへコミットしないでください。

### 4. PostgreSQLを使用する場合

PostgreSQLを使用する場合は、Docker Composeで開発用DBを起動します。

```powershell
docker compose up -d db
docker compose ps
```

### 5. データベースマイグレーションを実行する

PostgreSQLを使用する場合は、アプリケーション起動前にAlembicでマイグレーションを適用します。

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

### 6. フロントエンドの依存関係をインストールする

```powershell
cd frontend
npm install
cd ..
```

## アプリケーションの起動

### バックエンド

プロジェクト直下で実行します。

```powershell
uvicorn backend.app.main:app --reload
```

APIドキュメント:

```text
http://localhost:8000/docs
```

### フロントエンド

別のターミナルで実行します。

```powershell
cd frontend
npm run dev
```

管理画面:

```text
http://localhost:5173
```

## フロントエンドの検査

`frontend`ディレクトリで実行します。

```powershell
npm run lint
npm run typecheck
npm run build
```
