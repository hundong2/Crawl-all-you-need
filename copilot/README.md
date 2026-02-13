[English](./README.md) | [한국어](./README.kr.md) | [日本語](./README.jp.md) | [中文](./README.zh.md) | [Français](./README.fr.md)

# AI Web Crawler 🕷️

LLM-powered website crawling and document conversion tool.

## Key Features

- ✅ **Multi-LLM provider support**: OpenAI (ChatGPT), Anthropic (Claude), Google (Gemini)
- ✅ **Automatic API connection checks**: Real-time connection status for each provider
- ✅ **Dynamic model loading**: Automatically loads the latest available models from each API
- ✅ **System environment variable integration**: Secure API key management and auto-loading
- ✅ **Flexible crawling**: Crawl a single page or an entire site
- ✅ **Multiple output formats**: Markdown, HTML, plain text
- ✅ **AI content refinement**: Structure and refine content with LLMs
- ✅ **User-friendly GUI**: Intuitive Streamlit-based interface
- ✅ **Real-time progress display**: Visualized crawling progress
- ✅ **Local execution**: Fully open source, runs with only API keys

## UI Preview

![AI Web Crawler UI](docs/images/main.png)
![Running](docs/images/run.png)

With the intuitive Streamlit interface, you can start crawling right away without complex configuration.

### Main Screen Layout

1. **Sidebar (Settings)**
   - **Connection Status**: Automatically validates API keys loaded from environment variables and shows traffic-light style indicators (✅/❌/⚪).
   - **Provider and Model Selection**: Choose connected LLM providers (OpenAI, Anthropic, Gemini) and the latest available models from their APIs.
   - **Crawling Options**: Configure single-page/full-site mode, max page count, and output formats (.md, .html, .txt).

2. **Main Area (Work)**
   - **URL Input**: Enter the target website URL to crawl.
   - **Progress Status**: Shows crawl progress and current task status in real time.
   - **Results and Download**: Preview and download results after crawling completes.

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd Copilot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Playwright (required by Crawl4AI)
```bash
playwright install
```

### 4. Configure environment variables

**Set API keys as system environment variables (recommended)**

#### macOS / Linux
```bash
# Add to ~/.zshrc (zsh) or ~/.bashrc (bash)
export OPENAI_API_KEY="sk-your-openai-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
export GOOGLE_API_KEY="AIza-your-google-key-here"

# Apply changes after saving
source ~/.zshrc  # or source ~/.bashrc
```

#### Windows

**Method 1: System Settings (GUI)**
1. `Control Panel` → `System` → `Advanced system settings`
2. Click `Environment Variables`
3. In `User variables`, click `New`
4. Enter variable names and values:
   - `OPENAI_API_KEY` = `your_key_here`
   - `ANTHROPIC_API_KEY` = `your_key_here`
   - `GOOGLE_API_KEY` = `your_key_here`

**Method 2: PowerShell**
```powershell
# Run PowerShell as administrator
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your_key_here', 'User')
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your_key_here', 'User')
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', 'your_key_here', 'User')
```

**Method 3: CMD**
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

#### Using a `.env` file (optional)
Instead of system environment variables, create a `.env` file in the project directory:
```bash
# Create .env
cp .env.example .env

# Edit .env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
```

> ⚠️ **Security note**: Never commit `.env` files to Git (already included in `.gitignore`)

## Usage

### Run the app
```bash
# Activate virtual environment (first time only)
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Run Streamlit app
streamlit run app.py
```

The app opens automatically in your browser (usually http://localhost:8501).

### Steps
1. **Automatic connection check**: On app startup, API keys are loaded from environment variables and each provider is checked
   - ✅ Green: Connected and available
   - ❌ Red: Connection failed (check API key)
   - ⚪ Gray: No API key
2. **Choose LLM provider**: Select from connected providers (manual API key input is also possible for disconnected providers)
3. **Choose model**: Pick from the latest available models fetched automatically from APIs
4. **Enter URL**: Input the website URL to crawl
5. **Configure crawl options**:
   - Single page or full site
   - Max page count (full-site mode)
   - Output format
7. **Start crawling**: Click the button
8. **Download results**: Download output files after completion

## Project Structure
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

## Tech Stack

- **Crawling**: [Crawl4AI](https://github.com/unclecode/crawl4ai) - LLM-friendly web crawler
- **GUI**: [Streamlit](https://streamlit.io/) - Fast and simple web app framework
- **LLM Integration**:
  - OpenAI API (ChatGPT)
  - Anthropic API (Claude)
  - Google Generative AI (Gemini)
- **Output formats**: Markdown, HTML, plain text

## Usage Examples

### Example 1: Crawl a single documentation page
```
URL: https://code.claude.com/docs/ko/overview
Mode: Single page
Output: Markdown
```

### Example 2: Crawl a full documentation site
```
URL: https://code.claude.com/docs/ko/overview
Mode: Full site
Max pages: 50
Output: HTML
LLM refinement: ON
```

## License

This project is distributed under the MIT License.

## Contributing

Contributions are always welcome. Feel free to open issues or submit PRs.

## References

- [Crawl4AI GitHub](https://github.com/unclecode/crawl4ai)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic API](https://docs.anthropic.com/)
- [Google Gemini API](https://ai.google.dev/)
