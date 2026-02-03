# .github Directory

このディレクトリには、プロジェクトの管理設定、GitHub Actions、およびGitHub Copilot用のインストラクションが含まれています。

## ディレクトリ構成

```text
.github/
├── agents/                      # プロジェクト固有のAIエージェント定義
│   ├── backend-engineer.agent.md # バックエンドエンジニア向けプロンプト
│   ├── frontend-architect.agent.md # フロントエンドアーキテクト向けプロンプト
│   ├── leader.agent.md           # プロジェクトリーダー向けプロンプト
│   ├── ml-engineer.agent.md      # MLエンジニア（RAG/LLM）向けプロンプト
│   └── ui-designer.agent.md      # UIデザイナー向けプロンプト
├── README.md                    # 本ファイル
└── copilot-instructions.md      # GitHub Copilot用の共通指示書
```

## 主要ファイルの説明

- **agents/**: 各ロールに特化したAIエージェントの振る舞いを定義したMarkdownファイル群です。
- **copilot-instructions.md**: このプロジェクトでGitHub Copilotを使用する際の全体的なコーディング規約や技術スタックの制約を記述しています。
