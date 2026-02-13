# Antigravity (한국어 안내)

Antigravity는 웹 페이지의 문서를 크롤링하여 LLM(대규모 언어 모델)이 이해하기 쉬운 형식으로 변환해주는 도구입니다.

![Antigravity 미리보기](antigravity_app_preview.png)

## 주요 기능

- **문서 크롤러**: 웹 문서를 크롤링하여 마크다운(Markdown) 형식으로 변환합니다.
- **재귀적 크롤링**: 깊이 제한(Depth-limit)을 설정하여 문서 사이트 전체를 재귀적으로 수집할 수 있습니다.
- **AI 향상(Enhancement)**: Google Gemini와 연동하여 추출된 콘텐츠를 더 읽기 좋고 구조화된 형태로 리팩토링합니다.
- **LLM 처리**: 수집된 콘텐츠를 다양한 LLM 제공자(Google Gemini, Anthropic Claude, OpenAI)를 통해 추가 가공할 수 있습니다.
- **모던 UI**: React와 Tailwind CSS로 구축된 깔끔하고 반응형인 사용자 인터페이스를 제공합니다.

## 시작하기

### 사전 요구사항

- Python 3.8 이상
- Node.js 18 이상
- `.env` 파일 또는 환경 변수에 LLM API 키 설정 (Google Gemini, Anthropic, OpenAI)

### 설치 및 실행

`Makefile`을 통해 간편하게 프로젝트를 관리할 수 있습니다.

1. **설치 (Setup)**: 백엔드와 프론트엔드의 의존성을 설치합니다.
   ```bash
   make setup
   ```

2. **실행 (Start)**: 백엔드와 프론트엔드 서버를 동시에 실행합니다.
   ```bash
   make start
   ```
   - 프론트엔드: http://localhost:5555
   - 백엔드: http://localhost:5556

3. **중지 (Stop)**: 실행 중인 모든 프로세스를 종료합니다.
   ```bash
   make stop
   ```

## 프로젝트 구조

```
antigravity/
├── backend/      # 크롤링 및 LLM 처리를 담당하는 FastAPI 백엔드
├── frontend/     # React + Vite 프론트엔드
├── Makefile      # 프로젝트 관리 명령어
└── ...
```

## 기여하기

개선 사항에 대한 이슈 제기와 풀 리퀘스트(Pull Request)는 언제나 환영합니다.

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
