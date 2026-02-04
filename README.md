# Scrapbox RAG System

Scrapboxの知見を最大限に活用し、ローカルLLM（Gemma 3）で回答するRAG（Retrieval-Augmented Generation）システムです。プライバシーを重視し、すべての処理をローカル環境で完結させます。

## 特徴
- **100% ローカル実行**: 外部APIを利用せず、データ漏洩のリスクを最小限に抑えます。
- **Scrapbox連携**: JSONエクスポート、または API 経由での直接インポートに対応。
- **ハイブリッド検索**: Elasticsearch を利用したセマンティック検索。
- **Gemma 3 搭載**: 最新のローカルLLMによる高精度な回答生成。

## システム構成

本システムは以下のコンポーネントで構成されています。

### アーキテクチャ図
- **Frontend (Next.js)**: チャットインターフェースと回答のストリーミング表示。
- **Backend (FastAPI)**: RAGロジックの制御、検索クエリの構築、Ollamaとの通信。
- **Encoder (Python/PyTorch)**: SPLADE (Sparse Lexical and Expansion) アルゴリズムを用いた日本語テキストのsparseベクトル化。
- **Search Engine (Elasticsearch)**: `rank_features` を用いた高速なベクトル検索および全文検索。
- **LLM (Ollama)**: Gemma 3 を用いた回答生成。

### 技術スタック
- **Frontend**: Next.js (App Router), Tailwind CSS, daisyUI, Framer Motion
- **Backend**: FastAPI, Pydantic v2, HTTPX, Elasticsearch-py
- **ML/NLP**: PyTorch, Transformers, SPLADE (`hotchpotch/japanese-splade-v2`), fugashi (MeCab)
- **Infrastructure**: Docker Compose, uv (Python package manager)

## 仕様詳細

### 1. 検索ロジック (SPLADE)
従来のキーワード検索（BM25）と異なり、文章の意味や関連語を考慮した **Sparse Vector 検索** を採用しています。
- **特徴**: キーワードの「重み」を計算し、欠落している単語を補完。例えば「PC」という単語に対して「パソコン」「コンピューター」といった関連語を考慮した検索が可能です。
- **モデル**: 日本語に特化した `hotchpotch/japanese-splade-v2` を使用。

### 2. Scrapbox データの正規化
Scrapbox特有の記法（`[リンク]`、`[画像.jpg]`、`[#ハッシュタグ]` など）をインデックス作成時にパース・クレンジングし、LLMが理解しやすい形式でチャンク分割を行います。

### 3. ストリーミング回答
LLM の回答は SSE (Server-Sent Events) を用いてリアルタイムにストリーミングされます。これにより、長い回答でも生成される端から順次表示され、ユーザーの待ち時間を軽減します。

## 準備

1. **Docker の起動**: Docker Desktop 等を起動しておきます。
2. **Ollama のセットアップ**:
   - [Ollama](https://ollama.ai/) をインストールし、Gemma 3 をプルしておきます。
   ```bash
   ollama pull gemma3:4b
   ```

## セットアップ & 起動

### Docker Compose を使用する場合（推奨）

```bash
# プロジェクトの初期化
make setup

# サービスのビルドと起動
make up
```

### 個別に起動する場合

Docker を使わずに各コンポーネントを個別に起動する場合の手順です。

#### 1. Elasticsearch の起動
```bash
docker run -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:8.16.0
```

#### 2. Backend の起動
```bash
cd backend
# 依存関係のインストール
uv sync

# SPLADE Encoder API の起動 (Port 8001)
uv run python encoder_app.py

# Search API の起動 (Port 8000)
uv run python -m app.main
```

#### 3. Frontend の起動
```bash
cd frontend
npm install
npm run dev
```

## データのインポート

Scrapbox のデータを検索エンジン（Elasticsearch）に登録します。

### 1. API 経由でのインポート（推奨）
Scrapbox のプロジェクト名を指定して直接取り込みます。

```bash
# 公開プロジェクトの場合
make import PROJECT=help-jp

# 非公開（プライベート）プロジェクトの場合
# ブラウザのクッキーから connect.sid を取得して指定
make import PROJECT=your-project-name SID=s%3Axxxxxxxxxxxx...
```

### 2. JSONファイルからのインポート
Scrapbox の設定からエクスポートした JSON ファイルを使用します。

```bash
make import JSON=path/to/backup.json
```

## 使い方

1. [http://localhost:3000](http://localhost:3000) にアクセスします。
2. 質問を入力すると、インポートした Scrapbox の内容に基づき、Gemma 3 が回答を生成します。

## 開発用コマンド

- `make logs`: 全コンテナのログを表示
- `make down`: 全サービスの停止
- `make build`: コンテナの再ビルド
- `make test`: テストの実行
- `make lint`: リンターの実行
