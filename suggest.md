# Scrapbox to Elasticsearch インポート工程の提案

テックリードとして、ScrapboxのJSONデータをインポートし、SPLADEによるベクトル化を経てElasticsearchに格納するまでのディレクトリ構成と実装手順を提案します。

## 1. フォルダ構成 (Backend)

設計原則として、関心の分離（Separation of Concerns）を徹底し、データ取得、加工、検索のロジックを分離します。

```text
backend/
├── app/
│   ├── api/                # FastAPI ルート定義
│   │   ├── v1/
│   │   │   ├── search.py   # 検索API (Real-time Pipeline)
│   │   │   └── ingest.py   # インポート進捗確認・手動トリガーAPI
│   ├── core/               # 設定、共通定数
│   │   └── config.py       # Elasticsearch/Ollama/SPLADEの接続情報
│   ├── models/             # Pydantic スキーマ
│   │   ├── scrapbox.py     # Scrapbox JSON/Chunkの型定義
│   │   └── search.py       # 検索クエリ・レスポンスの型定義
│   ├── services/           # ビジネスロジック
│   │   ├── scrapbox_service.py # Scrapbox API/JSON処理 & Chunking
│   │   ├── encoder_service.py  # SPLADE Encoder API クライアント
│   │   └── elasticsearch_service.py # ES への Indexing/Search (rank_features対応)
│   └── main.py             # エントリポイント
├── scripts/                # バッチ処理用スクリプト
│   └── import_scrapbox.py  # 初期インポート用コマンドラインツール
├── tests/                  # ユニット・統合テスト
├── pyproject.toml          # uv によるパッケージ管理
└── .env                    # 環境変数
```

## 2. 実装手順 (Implementation Steps)

### フェーズ1: 接地 (Foundations)
1.  **環境セットアップ**: `uv init` でプロジェクト初期化。`fastapi`, `elasticsearch`, `httpx`, `pydantic-settings` などを導入。
2.  **Elasticsearch インデックス設計**: `kuromoji` アナライザを `text` フィールドに適用し、`sparse_vector` フィールドを `rank_features` 型として定義するマッピングを実装。

### フェーズ2: データ収集・抽出 (Extraction & Pre-processing)
3.  **Scrapbox パーサーの実装**:
    - JSONファイルのパース（`models/scrapbox.py`）。
    - チャンク分割ロジック: 単純な文字数ではなく、Scrapboxの箇条書き（Indent）や空行を考慮したセマンティックな分割を `scrapbox_service.py` に実装。
4.  **記法クレンジング**: `[link]` などの Scrapbox 特有記法を、検索に適したプレーンテキストに変換。

### フェーズ3: 変換・格納 (Transformation & Loading)
5.  **SPLADE Encoder 連携**: `encoder_service.py` を作成し、ローカルの SPLADE API へテキストを送信。返却されたスパースベクトル（辞書形式）を取得。
6.  **インデクシング・パイプライン**:
    - `elasticsearch_service.py` で `bulk` API を利用。
    - メタデータ（タイトル、URL、更新日）とスパースベクトルをセットで登録。

### フェーズ4: 運用ツール (Operations)
7.  **CLIツール開発**: `scripts/import_scrapbox.py` を作成。JSONファイルパスを引数に取り、一括してインデックスを構築可能にする。

## 3. テックリードからの技術的留意点

-   **SPLADE の負荷管理**: ローカル環境（Mac/CPU）での実行を考慮し、一括変換時の並列数は `asyncio.Semaphore` 等で制御してください。
-   **冪等性の確保**: ページIDとチャンクインデックスに基づいた `document_id` を生成し、再実行時に重複登録されないように設計します。
-   **拡張性**: 将来的に BM25 とのハイブリッド検索への移行が容易なよう、`elasticsearch_service.py` の検索メソッドを抽象化しておいてください。
