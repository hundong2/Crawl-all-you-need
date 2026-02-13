# LANGUAGE.md

## README 다국어 자동 반영 스킬

이 저장소는 `README.md`를 기준으로 한국어/일본어/중국어/프랑스어 번역 파일을 자동 갱신하는 스킬을 제공합니다.

대상 파일:
- `README.md` (원문)
- `README.kr.md`
- `README.jp.md`
- `README.zh.md`
- `README.fr.md`

공통 실행 스크립트:
- `scripts/readme_i18n_sync.sh`

## 엔진별 사용법

기본 커맨드는 엔진명 그대로 사용합니다:
- Codex: `codex`
- Claude Code: `claude`
- Copilot: `copilot`
- Gemini: `gemini`

기본 실행:

1. Codex
```bash
scripts/readme_i18n_sync.sh --engine codex
```

2. Claude Code
```bash
scripts/readme_i18n_sync.sh --engine claude
```

3. Copilot
```bash
scripts/readme_i18n_sync.sh --engine copilot
```

4. Gemini
```bash
scripts/readme_i18n_sync.sh --engine gemini
```

커맨드를 바꾸고 싶으면 아래 환경변수로 override 가능합니다:
- `README_I18N_CODEX_CMD`
- `README_I18N_CLAUDE_CMD`
- `README_I18N_COPILOT_CMD`
- `README_I18N_GEMINI_CMD`

## 경로 안내 (일반 경로)

- Codex skill: `.codex/skills/readme-i18n-sync/SKILL.md`
- Claude command: `.claude/commands/readme-i18n-sync.md`
- Copilot prompt: `.github/prompts/readme-i18n-sync.prompt.md`
- Gemini command: `.gemini/commands/readme-i18n-sync.md`

## 참고

- 스크립트는 번역 결과의 최상단에 공통 언어 네비게이션 링크를 삽입/정규화합니다.
- 링크/코드블록/경로/URL/표 구조는 유지하고, 설명 문장만 번역하도록 설계되어 있습니다.
