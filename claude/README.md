# Site-to-Document Generator

웹사이트 전체를 크롤링하고, LLM으로 콘텐츠를 정리하여 하나의 통합 문서(Markdown/PDF)로 생성하는 앱입니다.

## 주요 기능

- **멀티 LLM 지원**: OpenAI (GPT-4o), Anthropic (Claude), Google (Gemini) 선택 가능
- **전체 사이트 크롤링**: Crawl4AI 기반 BFS 딥 크롤링, JS 렌더링 지원
- **문서 자동 생성**: 목차(TOC) 생성 + 콘텐츠 정리 + 단일 문서로 병합
- **다중 출력 포맷**: Markdown, PDF
- **환경 변수 API Key**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` 자동 로드
- **Gradio 웹 UI**: 브라우저에서 간편하게 사용

## 빠른 시작

```bash
# 1. 초기 설정 (최초 1회)
make setup

# 2. API Key 환경 변수 설정 (사용할 프로바이더 중 하나 이상)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="AI..."

# 3. 앱 실행
make start        # http://localhost:7860 에서 접속
```

## Make 명령어

```
make help       사용 가능한 명령어 목록 표시
make setup      의존성 설치 및 프로젝트 초기 설정
make start      앱 시작 (백그라운드, http://localhost:7860)
make stop       앱 중지
make restart    앱 재시작
make status     앱 실행 상태 확인
make logs       앱 로그 확인
make clean      앱 중지 및 임시 파일 정리
```

## 프로젝트 구조

```
├── Makefile                  # 빌드/실행 자동화
├── README.md                 # 이 파일
├── LICENSE
└── claude/                   # 소스 코드
    ├── app.py                # Entry point (Gradio 실행)
    ├── requirements.txt      # Python 의존성
    ├── config/               # 설정 (모델 목록, 상수)
    ├── ui/                   # Gradio UI 레이아웃 + 이벤트 핸들러
    ├── crawler/              # Crawl4AI 기반 사이트 크롤러
    ├── llm/                  # LLM 프로바이더 (OpenAI, Anthropic, Google)
    ├── document/             # 문서 생성 (Markdown, PDF)
    └── pipeline/             # 전체 파이프라인 오케스트레이터
```

## 지원 모델

| Provider | Models |
|----------|--------|
| OpenAI | GPT-4o, GPT-4o-mini |
| Anthropic | Claude Sonnet 4.5, Claude Haiku 3.5 |
| Google | Gemini 2.0 Flash, Gemini 1.5 Pro |

## 시스템 요구사항

- Python 3.10+
- macOS: `brew install cairo pango gdk-pixbuf libffi` (PDF 변환용)
- Linux: `apt-get install libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0`

## 라이선스

MIT License
