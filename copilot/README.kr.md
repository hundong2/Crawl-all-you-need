[English](./README.md) | [한국어](./README.kr.md) | [日本語](./README.jp.md) | [中文](./README.zh.md) | [Français](./README.fr.md)

# AI Web Crawler 🕷️

LLM 기반 웹사이트 크롤링 & 문서 변환 도구

## 주요 기능

- ✅ **다중 LLM 제공자 지원**: OpenAI (ChatGPT), Anthropic (Claude), Google (Gemini)
- ✅ **자동 API 연결 확인**: 각 제공자별 실시간 연결 상태 표시
- ✅ **동적 모델 로딩**: API에서 사용 가능한 최신 모델 자동 로드
- ✅ **시스템 환경 변수 통합**: 안전한 API 키 관리 및 자동 로드
- ✅ **유연한 크롤링**: 단일 페이지 또는 전체 사이트 크롤링
- ✅ **다양한 출력 포맷**: Markdown, HTML, 텍스트
- ✅ **AI 콘텐츠 정제**: LLM을 활용한 콘텐츠 구조화 및 정제
- ✅ **사용자 친화적 GUI**: Streamlit 기반 직관적 인터페이스
- ✅ **실시간 진행 표시**: 크롤링 진행 상황 시각화
- ✅ **로컬 실행 가능**: 완전한 오픈소스, API 키만 있으면 실행

## UI 미리보기

![AI Web Crawler UI](docs/images/main.png)
![Running](docs/images/run.png)

직관적인 Streamlit 인터페이스를 통해 복잡한 설정 없이 바로 크롤링을 시작할 수 있습니다.

### 주요 화면 구성

1. **사이드바 (설정)**
   - **연결 상태**: 환경 변수에서 로드된 API 키의 유효성을 자동으로 확인하고 신호등(✅/❌/⚪)으로 표시합니다.
   - **제공자 및 모델 선택**: 연결된 LLM 제공자(OpenAI, Anthropic, Gemini)와 해당 API에서 사용 가능한 최신 모델을 선택할 수 있습니다.
   - **크롤링 옵션**: 단일 페이지/전체 사이트 모드, 최대 페이지 수, 출력 포맷(.md, .html, .txt) 등을 설정합니다.

2. **메인 화면 (작업)**
   - **URL 입력**: 크롤링할 대상 웹사이트의 URL을 입력합니다.
   - **진행 상태**: 크롤링 진행률과 현재 작업 상태를 실시간으로 보여줍니다.
   - **결과 및 다운로드**: 크롤링이 완료되면 결과를 미리보고 파일로 다운로드할 수 있습니다.

## 설치 방법

### 1. 저장소 클론
```bash
git clone <repository-url>
cd Copilot
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. Playwright 설치 (Crawl4AI 필요)
```bash
playwright install
```

### 4. 환경 변수 설정

**시스템 환경 변수에 API 키 설정 (권장)**

#### macOS / Linux
```bash
# ~/.zshrc (zsh) 또는 ~/.bashrc (bash) 파일에 추가
export OPENAI_API_KEY="sk-your-openai-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
export GOOGLE_API_KEY="AIza-your-google-key-here"

# 파일 저장 후 적용
source ~/.zshrc  # 또는 source ~/.bashrc
```

#### Windows

**방법 1: 시스템 설정에서 (GUI)**
1. `제어판` → `시스템` → `고급 시스템 설정`
2. `환경 변수` 버튼 클릭
3. `사용자 변수`에서 `새로 만들기` 클릭
4. 변수 이름과 값 입력:
   - `OPENAI_API_KEY` = `your_key_here`
   - `ANTHROPIC_API_KEY` = `your_key_here`
   - `GOOGLE_API_KEY` = `your_key_here`

**방법 2: PowerShell 사용**
```powershell
# 관리자 권한으로 PowerShell 실행
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your_key_here', 'User')
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your_key_here', 'User')
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', 'your_key_here', 'User')
```

**방법 3: CMD 사용**
```cmd
setx OPENAI_API_KEY "your_key_here"
setx ANTHROPIC_API_KEY "your_key_here"
setx GOOGLE_API_KEY "your_key_here"
```

#### Docker 환경
```bash
docker run -e OPENAI_API_KEY=your_key \
           -e ANTHROPIC_API_KEY=your_key \
           -e GOOGLE_API_KEY=your_key \
           your_image
```

#### .env 파일 사용 (선택사항)
시스템 환경 변수 대신 프로젝트 디렉토리에 `.env` 파일 생성:
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
```

> ⚠️ **보안 주의**: `.env` 파일은 Git에 커밋하지 마세요 (이미 .gitignore에 포함됨)

## 사용 방법

### 앱 실행
```bash
# 가상환경 활성화 (처음 한 번만)
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# Streamlit 앱 실행
streamlit run app.py
```

앱이 자동으로 브라우저에서 열립니다 (보통 http://localhost:8501)

### 사용 단계
1. **자동 연결 확인**: 앱 실행 시 환경 변수에서 API 키를 자동으로 불러와 각 제공자의 연결 상태를 확인합니다
   - ✅ 녹색: 연결 성공 및 사용 가능
   - ❌ 빨간색: 연결 실패 (API 키 확인 필요)
   - ⚪ 회색: API 키 없음
2. **LLM 제공자 선택**: 연결된 제공자 중에서 선택 (연결되지 않은 제공자는 수동으로 API 키 입력 가능)
3. **모델 선택**: API에서 자동으로 가져온 최신 사용 가능 모델 목록에서 선택
4. **URL 입력**: 크롤링할 웹사이트 주소 입력
5. **크롤링 옵션 설정**:
   - 단일 페이지 또는 전체 사이트
   - 최대 페이지 수 (전체 사이트 모드)
   - 출력 포맷 선택
7. **크롤링 시작**: 버튼 클릭
8. **결과 다운로드**: 완료 후 파일 다운로드

## 프로젝트 구조
```
Copilot/
├── ai_web_crawler/
│   ├── models/
│   │   └── llm_providers.py    # LLM 통합 레이어
│   ├── utils/
│   │   ├── crawler.py          # 크롤링 로직
│   │   └── file_exporter.py    # 파일 저장 유틸
│   └── output/                 # 출력 파일 디렉토리
├── app.py                      # Streamlit 앱
├── requirements.txt            # 의존성
├── .env.example               # 환경 변수 예시
├── .gitignore                 # Git 제외 파일
├── ENV_SETUP_GUIDE.md         # 환경 변수 설정 상세 가이드
└── README.md                  # 문서
```

## 기술 스택

- **크롤링**: [Crawl4AI](https://github.com/unclecode/crawl4ai) - LLM 친화적 웹 크롤러
- **GUI**: [Streamlit](https://streamlit.io/) - 빠르고 쉬운 웹 앱 프레임워크
- **LLM 통합**:
  - OpenAI API (ChatGPT)
  - Anthropic API (Claude)
  - Google Generative AI (Gemini)
- **출력 포맷**: Markdown, HTML, 텍스트

## 사용 예시

### 예시 1: 단일 문서 페이지 크롤링
```
URL: https://code.claude.com/docs/ko/overview
모드: 단일 페이지
출력: Markdown
```

### 예시 2: 전체 문서 사이트 크롤링
```
URL: https://code.claude.com/docs/ko/overview
모드: 전체 사이트
최대 페이지: 50
출력: HTML
LLM 정제: ON
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여

기여는 언제나 환영합니다! 이슈나 PR을 자유롭게 제출해주세요.

## 참고 자료

- [Crawl4AI GitHub](https://github.com/unclecode/crawl4ai)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic API](https://docs.anthropic.com/)
- [Google Gemini API](https://ai.google.dev/)
