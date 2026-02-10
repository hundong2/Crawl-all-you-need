# SiteBooker

SiteBooker crawls a documentation site and generates a single markdown book (`book.md`) with optional LLM cleanup.

## Features
- Provider chooser: OpenAI / Anthropic / Google
- Model chooser per provider
- Same-domain crawler with depth/page limits
- Markdown book export + manifest metadata
- Optional PDF/EPUB/DOCX conversion via pandoc
- Optional LLM post-processing through LiteLLM
- Async build jobs with progress polling
- Simple web UI

## Configuration Policy
- Runtime config (`UV_HOST`, `UV_PORT`, etc.) is loaded from `.env`.
- API keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`) are read only from OS environment variables.
- API keys in `.env` are ignored by design.

## Runtime Settings (.env)
1. Create `.env` from template:
```bash
cp .env.example .env
```
2. Edit values as needed:
- `UV_HOST` (example: `127.0.0.1`)
- `UV_PORT` (example: `8000`)

## API Keys (OS Environment Variables)
Set provider keys in your terminal/OS environment.

Supported keys:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`

### macOS / Linux (zsh, bash)
Temporary (current terminal only):
```bash
export OPENAI_API_KEY=your_key_here
export ANTHROPIC_API_KEY=your_key_here
export GEMINI_API_KEY=your_key_here
```

Persistent (zsh):
```bash
echo 'export OPENAI_API_KEY=your_key_here' >> ~/.zshrc
echo 'export ANTHROPIC_API_KEY=your_key_here' >> ~/.zshrc
echo 'export GEMINI_API_KEY=your_key_here' >> ~/.zshrc
source ~/.zshrc
```

### Windows PowerShell
Temporary (current window only):
```powershell
$env:OPENAI_API_KEY=\"your_key_here\"
$env:ANTHROPIC_API_KEY=\"your_key_here\"
$env:GEMINI_API_KEY=\"your_key_here\"
```

Persistent (user-level):
```powershell
[System.Environment]::SetEnvironmentVariable(\"OPENAI_API_KEY\", \"your_key_here\", \"User\")
[System.Environment]::SetEnvironmentVariable(\"ANTHROPIC_API_KEY\", \"your_key_here\", \"User\")
[System.Environment]::SetEnvironmentVariable(\"GEMINI_API_KEY\", \"your_key_here\", \"User\")
```

## Optional Runtime Vars
- `UV_HOST` (example: `127.0.0.1`)
- `UV_PORT` (example: `8000`)
- `UV_LOG_SENSITIVE` (recommended: `false`)

## Quickstart (uv)
1. Install dependencies:
```bash
uv sync
```
2. Create runtime config:
```bash
cp .env.example .env
```
3. Set API keys in OS environment variables.
4. Run app:
```bash
uv run sitebooker
```
5. Open: `http://127.0.0.1:8000`

## API
- `GET /api/models/{provider}`
- `POST /api/build`
- `POST /api/build/jobs`
- `GET /api/build/jobs/{job_id}`
- `GET /api/build/jobs`
- `GET /api/build/jobs/{job_id}/files`
- `GET /api/build/jobs/{job_id}/download/{filename}`

Example payload:
```json
{
  "provider": "anthropic",
  "model": "claude-3-7-sonnet-latest",
  "root_url": "https://example.com/docs",
  "output_formats": ["md"],
  "max_pages": 30,
  "max_depth": 2,
  "llm_refine": false
}
```

## Outputs
Each run creates:
- `outputs/<timestamp>_<slug>_<runid>/book.md`
- `outputs/<timestamp>_<slug>_<runid>/manifest.json`
- optionally `book.pdf`, `book.epub`, `book.docx` (when pandoc is available)
- job history in `outputs/sitebooker.db` (SQLite)

## pandoc (optional)
If you want PDF/EPUB/DOCX output:
```bash
brew install pandoc
```

## Security notes
- Keep API keys in OS environment variables only.
- Do not put API keys in `.env`.
- Do not hardcode keys in source code or commit them into the repository.
- Do not commit output artifacts containing private docs.
