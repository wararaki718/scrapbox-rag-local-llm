# Scrapbox RAG Backend

Scrapbox の知見をベクトル検索し、ローカル LLM (Gemma 3) で回答する RAG システムのバックエンド。

## 1. 概要
- **Search Engine**: Elasticsearch 8.16 (kuromoji, rank_features)
- **Sparse Embedding**: SPLADE (naver/splade-v2-distilbert-gop)
- **LLM**: Gemma 3 4B (via Ollama)
- **Framework**: FastAPI (Python 3.12+)

## 2. ディレクトリ構成
```text
backend/
├── app/
│   ├── api/                # API ルート定義 (v1/search.py, v1/ingest.py)
│   ├── core/               # 設定 (config.py)
│   ├── models/             # Pydantic スキーマ
│   ├── services/           # ロジック (Scrapbox, Encoder, ES, LLM)
│   └── main.py             # メイン API エントリポイント (Port 8000)
├── scripts/                # CLI ツール (import_scrapbox.py)
├── encoder_app.py          # SPLADE 推論 API (Port 8001)
├── pyproject.toml          # uv パッケージ管理
└── .env                    # 環境変数
```

## 3. セットアップ

### 必要な環境
- Docker (Elasticsearch 用)
- Ollama (LLM 推論用)
- Python 3.12+ / [uv](https://github.com/astral-sh/uv)

### 手順

#### 1. Elasticsearch の起動
```bash
docker run -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.16.0
```

#### 2. Ollama で Gemma 3 を準備
```bash
ollama run gemma3:4b
```

#### 3. バックエンドのパッケージインストール
```bash
cd backend
uv sync
```
※ `torch` や `transformers` が必要です。

#### 4. SPLADE Encoder API の起動
ローカルで SPLADE 推論を行うための軽量サーバーを起動します。
```bash
uv run python encoder_app.py
```
- Port: `8001` で待機します。
- 初回起動時に Hugging Face からモデルをダウンロードします。
- Apple Silicon (Mac) の場合は自動的に `mps` (Metal) を使用します。

#### 5. メイン API の起動
検索機能とインポート機能を提供します。
```bash
uv run python -m app.main
```
- Port: `8000` で待機します。

## 4. API 仕様

### `POST /api/v1/ingest`
Scrapbox のエクスポート JSON をアップロードし、インデックスを作成します。
- **Request**: `multipart/form-data` (file)
- **Process**: チャンク分割 -> SPLADE 変換 -> ES 登録

### `POST /api/v1/search`
自然言語クエリによる RAG 検索。
- **Request Body**:
  ```json
  {
    "query": "質問内容",
    "top_k": 5
  }
  ```
- **Response**:
  ```json
  {
    "answer": "Gemma 3 による回答",
    "sources": [
      { "title": "...", "url": "...", "text": "..." }
    ]
  }
  ```

## 5. CLI インポート
大量のデータをコマンドラインからインポートする場合：
```bash
uv run python scripts/import_scrapbox.py /path/to/your/scrapbox.json
```
