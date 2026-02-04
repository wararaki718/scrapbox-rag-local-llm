# Frontend UI 実装・構成案 (Scrapbox RAG)

テックリードとして、Scrapboxの知見を最大限に引き出し、ユーザーが快適に検索・閲覧できるUIの設計案を定義します。

## 1. デザイン方針
- **Scrapboxらしさの継承**: Scrapbox特有のリンク感や、カード状のレイアウトを取り入れ、既存ユーザーに違和感のないUIを目指す。
- **ローカルLLMの特性への配慮**: Gemma 3の生成待ち時間を軽減するため、ストリーミング表示とスケルトンスクリーンを多用する。
- **モダンな操作感**: `framer-motion` を使用したスムーズな画面遷移と、`daisyUI` によるクリーンなコンポーネント構成。

## 2. コンポーネント構成

### A. チャットビュー (`src/components/chat/`)
- `ChatContainer`: メッセージ履歴の管理とスクロール制御。
- `MessageBubble`: ユーザー/ボットのメッセージ表示。
    - **ScrapboxRenderer**: ボットの回答内にあるScrapbox記法をパースしてレンダリングする心臓部。
- `SourceCard`: 検索結果（引用元）のプレビューカード。クリックで詳細表示。

### B. 検索・入力部 (`src/components/input/`)
- `SearchInput`: プレースホルダー付き入力フォーム。
- `IngestStatus`: ファイルアップロード時のプログレスバー表示。

### C. ナビゲーション (`src/components/layout/`)
- `Sidebar`: 過去の検索履歴や、現在ロードされているScrapboxプロジェクトの一覧。
- `ThemeToggle`: ライト/ダークモード切り替え。

## 3. 重要実装ポイント

### 3.1 Scrapbox記法のレンダリング
単純な Markdown ではなく、Scrapbox記法をパースする必要があります。
- **Library**: `scrapbox-parser` を検討（または正規表現による簡易実装）。
- **実装内容**:
    - `[リンク名]` -> プロジェクト内リンクまたは外部リンクへ。
    - `[画像URL]` -> `<img>` タグへ。
    - `[[強調]]` -> `<strong>` または Scrapbox風の太字へ。
    - `> 引用` -> 引用ブロックへ。

### 3.2 回答のストリーミング (SSE)
`llm_service.py` が生成するトークンをリアルタイムに受信します。
- **Backend API**: `StreamingResponse` (FastAPI)
- **Frontend**: `ReadableStream` を使ったフェッチ処理。
- **UX**: 文字がパラパラと表示されるアニメーションにより、体感速度を向上。

### 3.3 ハイブリッド検索のソース表示
検索結果には「スコア」だけでなく、「最終更新日」や「本文の抜粋（ハイライト）」を含めます。
- インデックス済みのテキストから、検索クエリにヒットした部分を太字にして表示。

## 4. 下準備（次に実行するコマンド）

フロントエンドに必要なライブラリを追加します。

```bash
cd frontend
npm install scrapbox-parser framer-motion lucide-react axios
```

## 5. ロードマップ案
1. **Phase 1**: `ScrapboxRenderer` コンポーネントの作成と、静的なテキストのパース検証。
2. **Phase 2**: APIエンドポイントを `StreamingResponse` に変更し、フロントエンドでのストリーミング受信。
3. **Phase 3**: サイドバーによる「検索履歴」の保存機能（ブラウザの LocalStorage を活用）。

---
この構成案に基づき、まずは `ScrapboxRenderer` の実装から開始しましょう。
