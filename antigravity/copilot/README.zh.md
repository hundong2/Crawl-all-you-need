[English](./README.md) | [한국어](./README.kr.md) | [日本語](./README.jp.md) | [中文](./README.zh.md) | [Français](./README.fr.md)

# AI Web Crawler 🕷️

基于 LLM 的网站爬取与文档转换工具。

## 主要功能

- ✅ **多 LLM 提供商支持**：OpenAI (ChatGPT)、Anthropic (Claude)、Google (Gemini)
- ✅ **自动 API 连接检查**：实时显示各提供商连接状态
- ✅ **动态模型加载**：自动加载各 API 当前可用的最新模型
- ✅ **系统环境变量集成**：安全管理 API 密钥并自动加载
- ✅ **灵活爬取**：支持单页或整站爬取
- ✅ **多种输出格式**：Markdown、HTML、文本
- ✅ **AI 内容优化**：使用 LLM 对内容进行结构化与优化
- ✅ **友好 GUI**：基于 Streamlit 的直观界面
- ✅ **实时进度显示**：可视化爬取进度
- ✅ **可本地运行**：完全开源，仅需 API 密钥即可运行

## UI 预览

![AI Web Crawler UI](docs/images/main.png)
![Running](docs/images/run.png)

通过直观的 Streamlit 界面，无需复杂配置即可立即开始爬取。

### 主要界面组成

1. **侧边栏（设置）**
   - **连接状态**：自动验证从环境变量加载的 API 密钥，并以信号灯样式（✅/❌/⚪）显示。
   - **提供商与模型选择**：可选择已连接的 LLM 提供商（OpenAI、Anthropic、Gemini）以及对应 API 中最新可用模型。
   - **爬取选项**：可配置单页/整站模式、最大页面数、输出格式（.md、.html、.txt）。

2. **主区域（操作）**
   - **URL 输入**：输入要爬取的网站 URL。
   - **进度状态**：实时显示爬取进度和当前任务状态。
   - **结果与下载**：爬取完成后可预览并下载结果文件。

## 安装

### 1. 克隆仓库
```bash
git clone <repository-url>
cd Copilot
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 安装 Playwright（Crawl4AI 所需）
```bash
playwright install
```

### 4. 配置环境变量

**将 API 密钥设置为系统环境变量（推荐）**

#### macOS / Linux
```bash
# 添加到 ~/.zshrc (zsh) 或 ~/.bashrc (bash)
export OPENAI_API_KEY="sk-your-openai-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
export GOOGLE_API_KEY="AIza-your-google-key-here"

# 保存后生效
source ~/.zshrc  # 或 source ~/.bashrc
```

#### Windows

**方法 1：系统设置（GUI）**
1. `Control Panel` → `System` → `Advanced system settings`
2. 点击 `Environment Variables`
3. 在 `User variables` 中点击 `New`
4. 输入变量名和值：
   - `OPENAI_API_KEY` = `your_key_here`
   - `ANTHROPIC_API_KEY` = `your_key_here`
   - `GOOGLE_API_KEY` = `your_key_here`

**方法 2：PowerShell**
```powershell
# 以管理员身份运行 PowerShell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your_key_here', 'User')
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your_key_here', 'User')
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', 'your_key_here', 'User')
```

**方法 3：CMD**
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

#### 使用 `.env` 文件（可选）
可替代系统环境变量，在项目目录创建 `.env` 文件：
```bash
# 创建 .env
cp .env.example .env

# 编辑 .env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
```

> ⚠️ **安全提示**：不要将 `.env` 文件提交到 Git（已包含在 `.gitignore`）

## 使用方法

### 运行应用
```bash
# 激活虚拟环境（仅首次）
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 运行 Streamlit 应用
streamlit run app.py
```

应用会自动在浏览器中打开（通常为 http://localhost:8501）。

### 操作步骤
1. **自动连接检查**：启动时自动从环境变量读取 API 密钥并检查各提供商
   - ✅ 绿色：连接成功且可用
   - ❌ 红色：连接失败（需检查 API 密钥）
   - ⚪ 灰色：无 API 密钥
2. **选择 LLM 提供商**：从已连接提供商中选择（未连接提供商也可手动输入 API 密钥）
3. **选择模型**：从 API 自动获取的最新可用模型列表中选择
4. **输入 URL**：输入要爬取的网站地址
5. **配置爬取选项**：
   - 单页或整站
   - 最大页面数（整站模式）
   - 输出格式
7. **开始爬取**：点击按钮
8. **下载结果**：完成后下载输出文件

## 项目结构
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

## 技术栈

- **Crawling**: [Crawl4AI](https://github.com/unclecode/crawl4ai) - LLM-friendly web crawler
- **GUI**: [Streamlit](https://streamlit.io/) - Fast and simple web app framework
- **LLM Integration**:
  - OpenAI API (ChatGPT)
  - Anthropic API (Claude)
  - Google Generative AI (Gemini)
- **Output formats**: Markdown, HTML, plain text

## 使用示例

### 示例 1：爬取单个文档页面
```
URL: https://code.claude.com/docs/ko/overview
Mode: Single page
Output: Markdown
```

### 示例 2：爬取整站文档
```
URL: https://code.claude.com/docs/ko/overview
Mode: Full site
Max pages: 50
Output: HTML
LLM refinement: ON
```

## 许可证

本项目基于 MIT License 发布。

## 贡献

欢迎贡献！欢迎提交 Issue 或 PR。

## 参考资料

- [Crawl4AI GitHub](https://github.com/unclecode/crawl4ai)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic API](https://docs.anthropic.com/)
- [Google Gemini API](https://ai.google.dev/)
