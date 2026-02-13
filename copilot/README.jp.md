[English](./README.md) | [한국어](./README.kr.md) | [日本語](./README.jp.md) | [中文](./README.zh.md) | [Français](./README.fr.md)

# AI Web Crawler 🕷️

LLM ベースの Web サイトクローリングおよびドキュメント変換ツール。

## 主な機能

- ✅ **複数 LLM プロバイダー対応**: OpenAI (ChatGPT), Anthropic (Claude), Google (Gemini)
- ✅ **API 接続の自動確認**: 各プロバイダーの接続状態をリアルタイム表示
- ✅ **動的モデル読み込み**: 各 API で利用可能な最新モデルを自動取得
- ✅ **システム環境変数との統合**: 安全な API キー管理と自動読み込み
- ✅ **柔軟なクロール**: 単一ページまたはサイト全体をクロール
- ✅ **多様な出力形式**: Markdown、HTML、テキスト
- ✅ **AI コンテンツ整形**: LLM によるコンテンツの構造化と整形
- ✅ **使いやすい GUI**: Streamlit ベースの直感的インターフェース
- ✅ **リアルタイム進捗表示**: クロール進行状況を可視化
- ✅ **ローカル実行可能**: 完全オープンソース、API キーのみで実行

## UI プレビュー

![AI Web Crawler UI](docs/images/main.png)
![Running](docs/images/run.png)

直感的な Streamlit インターフェースにより、複雑な設定なしですぐにクロールを開始できます。

### 主要画面構成

1. **サイドバー (設定)**
   - **接続状態**: 環境変数から読み込まれた API キーの有効性を自動検証し、信号表示 (✅/❌/⚪) で示します。
   - **プロバイダーとモデル選択**: 接続済み LLM プロバイダー (OpenAI, Anthropic, Gemini) と、各 API の最新利用可能モデルを選択できます。
   - **クロール設定**: 単一ページ/サイト全体モード、最大ページ数、出力形式 (.md, .html, .txt) を設定できます。

2. **メイン画面 (作業)**
   - **URL 入力**: クロール対象サイトの URL を入力します。
   - **進捗状況**: クロール進行率と現在の処理状態をリアルタイム表示します。
   - **結果とダウンロード**: クロール完了後に結果をプレビューし、ファイルとしてダウンロードできます。

## インストール

### 1. リポジトリをクローン
```bash
git clone <repository-url>
cd Copilot
```

### 2. 依存関係をインストール
```bash
pip install -r requirements.txt
```

### 3. Playwright をインストール (Crawl4AI に必要)
```bash
playwright install
```

### 4. 環境変数を設定

**API キーをシステム環境変数として設定 (推奨)**

#### macOS / Linux
```bash
# ~/.zshrc (zsh) または ~/.bashrc (bash) に追加
export OPENAI_API_KEY="sk-your-openai-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
export GOOGLE_API_KEY="AIza-your-google-key-here"

# 保存後に反映
source ~/.zshrc  # または source ~/.bashrc
```

#### Windows

**方法 1: システム設定 (GUI)**
1. `Control Panel` → `System` → `Advanced system settings`
2. `Environment Variables` をクリック
3. `User variables` で `New` をクリック
4. 変数名と値を入力:
   - `OPENAI_API_KEY` = `your_key_here`
   - `ANTHROPIC_API_KEY` = `your_key_here`
   - `GOOGLE_API_KEY` = `your_key_here`

**方法 2: PowerShell**
```powershell
# 管理者権限で PowerShell を実行
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your_key_here', 'User')
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your_key_here', 'User')
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', 'your_key_here', 'User')
```

**方法 3: CMD**
```cmd
setx OPENAI_API_KEY "your_key_here"
setx ANTHROPIC_API_KEY "your_key_here"
setx GOOGLE_API_KEY "your_key_here"
```

#### Docker
```bash
docker run -e OPENAI_API_KEY=your_key \
           -e ANTHROPIC_API_KEY=your_key \
           -e GOOGLE_API_KEY=your_key \
           your_image
```

#### `.env` ファイルを使用 (任意)
システム環境変数の代わりに、プロジェクトディレクトリに `.env` ファイルを作成します:
```bash
# .env を作成
cp .env.example .env

# .env を編集
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
```

> ⚠️ **セキュリティ注意**: `.env` ファイルを Git にコミットしないでください (すでに `.gitignore` に含まれています)

## 使い方

### アプリ起動
```bash
# 仮想環境を有効化 (初回のみ)
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows

# Streamlit アプリを起動
streamlit run app.py
```

アプリはブラウザで自動的に開きます (通常は http://localhost:8501)。

### 手順
1. **自動接続確認**: 起動時に環境変数から API キーを読み込み、各プロバイダーを確認
   - ✅ 緑: 接続成功・利用可能
   - ❌ 赤: 接続失敗 (API キー確認が必要)
   - ⚪ 灰: API キーなし
2. **LLM プロバイダー選択**: 接続済みプロバイダーから選択 (未接続プロバイダーは手動 API キー入力も可能)
3. **モデル選択**: API から自動取得した最新利用可能モデルから選択
4. **URL 入力**: クロール対象の Web サイト URL を入力
5. **クロール設定**:
   - 単一ページまたはサイト全体
   - 最大ページ数 (サイト全体モード)
   - 出力形式
7. **クロール開始**: ボタンをクリック
8. **結果ダウンロード**: 完了後に出力ファイルをダウンロード

## プロジェクト構成
```
Copilot/
├── ai_web_crawler/
│   ├── models/
│   │   └── llm_providers.py    # LLM integration layer
│   ├── utils/
│   │   ├── crawler.py          # Crawling logic
│   │   └── file_exporter.py    # File export utility
│   └── output/                 # Output directory
├── app.py                      # Streamlit app
├── requirements.txt            # Dependencies
├── .env.example               # Environment variable example
├── .gitignore                 # Git ignored files
├── ENV_SETUP_GUIDE.md         # Detailed environment setup guide
└── README.md                  # Documentation
```

## 技術スタック

- **Crawling**: [Crawl4AI](https://github.com/unclecode/crawl4ai) - LLM-friendly web crawler
- **GUI**: [Streamlit](https://streamlit.io/) - Fast and simple web app framework
- **LLM Integration**:
  - OpenAI API (ChatGPT)
  - Anthropic API (Claude)
  - Google Generative AI (Gemini)
- **Output formats**: Markdown, HTML, plain text

## 使用例

### 例 1: 単一ドキュメントページをクロール
```
URL: https://code.claude.com/docs/ko/overview
Mode: Single page
Output: Markdown
```

### 例 2: ドキュメントサイト全体をクロール
```
URL: https://code.claude.com/docs/ko/overview
Mode: Full site
Max pages: 50
Output: HTML
LLM refinement: ON
```

## ライセンス

このプロジェクトは MIT ライセンスの下で配布されています。

## コントリビューション

コントリビューションは歓迎します。Issue 作成や PR 提出をお気軽にどうぞ。

## 参考資料

- [Crawl4AI GitHub](https://github.com/unclecode/crawl4ai)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic API](https://docs.anthropic.com/)
- [Google Gemini API](https://ai.google.dev/)
