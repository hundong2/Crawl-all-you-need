# API 연결 기능 업데이트 📡

## 주요 변경사항 (2026-02-09)

### ✨ 새로운 기능

#### 1. 자동 환경 변수 감지 및 로드
- `.env` 파일이나 시스템 환경 변수에서 API 키 자동 로드
- 수동 입력 없이 바로 시작 가능
- 환경 변수: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`

#### 2. 실시간 연결 상태 표시 🔌
- 앱 실행 시 모든 AI 제공자의 연결 상태 자동 확인
- 시각적 상태 표시:
  - ✅ **녹색**: 연결 성공, 즉시 사용 가능
  - ❌ **빨간색**: 연결 실패 (API 키 확인 필요)
  - ⚪ **회색**: API 키 없음 (수동 입력 가능)
- 각 제공자별 사용 가능한 모델 개수 표시

#### 3. 동적 모델 목록 로딩 📡
- 하드코딩된 모델 리스트 대신 API에서 직접 최신 모델 가져오기
- 각 제공자별 실제 사용 가능한 모델만 표시
- OpenAI: `models.list()` API 사용
- Anthropic: 최신 Claude 모델 목록
- Google: `list_models()` API 사용

#### 4. 향상된 사용자 경험
- 연결된 제공자만 선택 가능
- 연결되지 않은 제공자는 수동 입력 옵션 제공
- 모델 선택 시 API에서 가져온 실제 사용 가능한 모델만 표시

### 🔧 기술적 변경사항

#### `llm_providers.py` 업데이트
- `LLMProvider` 추상 클래스에 `check_connection()` 메서드 추가
- 각 제공자 클래스에 연결 확인 로직 구현
- `get_available_models()` 메서드를 API 호출로 업그레이드

#### `app.py` UI 개선
- 사이드바에 연결 상태 섹션 추가
- 자동 환경 변수 감지 로직 구현
- 연결된 제공자만 선택 가능하도록 필터링
- 수동 입력 폴백 옵션 제공

### 📝 추가 파일
- `test_connection.py`: API 연결 상태 테스트 스크립트
- `CHANGELOG_API.md`: 이 문서

### 🎯 사용 방법

#### 환경 변수 설정 (권장)

**macOS/Linux**:
```bash
# ~/.zshrc 또는 ~/.bashrc에 추가
export OPENAI_API_KEY="sk-your-key"
export ANTHROPIC_API_KEY="sk-ant-your-key"
export GOOGLE_API_KEY="AIza-your-key"

# 적용
source ~/.zshrc
```

**Windows (PowerShell)**:
```powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your_key', 'User')
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your_key', 'User')
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', 'your_key', 'User')
```

**또는 .env 파일**:
```bash
# .env 파일 생성
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
GOOGLE_API_KEY=AIza-your-key
```

#### 연결 상태 테스트
```bash
python test_connection.py
```

#### 앱 실행
```bash
streamlit run app.py
```

### 🔄 마이그레이션 가이드

기존 사용자의 경우:
1. 환경 변수 설정 (위 방법 참조)
2. 앱 재시작
3. 사이드바에서 자동으로 연결된 제공자 확인
4. 연결 상태가 ✅ 녹색이면 즉시 사용 가능

### 🐛 알려진 제한사항

1. **Anthropic 연결 확인**: 실제 API 호출이 필요하므로 약간의 비용 발생 (최소 토큰)
2. **Google API**: 일부 모델은 `generateContent`를 지원하지 않을 수 있음
3. **네트워크 오류**: 연결 확인 시 타임아웃이 발생할 수 있음

### 📊 성능 영향

- 초기 로딩 시 각 제공자당 1회 API 호출
- 로딩 시간 약 2-5초 증가 (네트워크 상태에 따라)
- 모델 목록 캐싱으로 후속 선택은 즉시 반영

### 🎉 장점

1. **편의성**: API 키를 매번 입력할 필요 없음
2. **보안**: 환경 변수 사용으로 키 노출 최소화
3. **최신성**: 항상 최신 모델 목록 사용
4. **직관성**: 연결 상태를 한눈에 확인

### 🚀 향후 계획

- [ ] 모델 목록 캐싱 (로딩 속度 개선)
- [ ] 연결 상태 자동 갱신 (주기적 체크)
- [ ] 모델별 상세 정보 표시 (컨텍스트 윈도우, 가격 등)
- [ ] API 사용량 모니터링 기능
