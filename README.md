# AI Web Crawler 🕷️

LLM 기반 웹사이트 크롤링 & 문서 변환 도구

## 주요 기능

- ✅ **다중 LLM 제공자 지원**: OpenAI (ChatGPT), Anthropic (Claude), Google (Gemini)
- ✅ **유연한 크롤링**: 단일 페이지 또는 전체 사이트 크롤링
- ✅ **다양한 출력 포맷**: Markdown, HTML, 텍스트
- ✅ **AI 콘텐츠 정제**: LLM을 활용한 콘텐츠 구조화 및 정제
- ✅ **사용자 친화적 GUI**: Streamlit 기반 직관적 인터페이스
- ✅ **실시간 진행 표시**: 크롤링 진행 상황 시각화
- ✅ **로컬 실행 가능**: 완전한 오픈소스, API 키만 있으면 실행

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
`.env` 파일 생성 (`.env.example` 참고):
```bash
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
```

## 사용 방법

### 앱 실행
```bash
streamlit run app.py
```

### 사용 단계
1. **LLM 제공자 선택**: 좌측 사이드바에서 원하는 제공자 선택
2. **API 키 입력**: 해당 제공자의 API 키 입력
3. **모델 선택**: 사용 가능한 모델 중 선택
4. **URL 입력**: 크롤링할 웹사이트 주소 입력
5. **크롤링 옵션 설정**:
   - 단일 페이지 또는 전체 사이트
   - 최대 페이지 수 (전체 사이트 모드)
   - 출력 포맷 선택
6. **크롤링 시작**: 버튼 클릭
7. **결과 다운로드**: 완료 후 파일 다운로드

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
