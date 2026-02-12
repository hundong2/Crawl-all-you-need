# 🔐 환경 변수 설정 가이드

AI Web Crawler를 사용하기 위해 LLM API 키를 시스템 환경 변수로 설정하는 방법입니다.

## 📋 필요한 API 키

사용하려는 LLM 제공자의 API 키를 준비하세요:

- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys
- **Google**: https://ai.google.dev/

## 🍎 macOS / Linux 설정

### 1. 터미널 열기

### 2. 쉘 설정 파일 편집

사용 중인 쉘 확인:
```bash
echo $SHELL
```

**zsh (macOS 기본):**
```bash
nano ~/.zshrc
```

**bash:**
```bash
nano ~/.bashrc
```

### 3. 파일 끝에 환경 변수 추가

```bash
# AI Web Crawler API Keys
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AIza..."
```

### 4. 저장 및 종료
- `Ctrl + O` → Enter (저장)
- `Ctrl + X` (종료)

### 5. 환경 변수 적용

```bash
# zsh
source ~/.zshrc

# bash
source ~/.bashrc
```

### 6. 확인

```bash
echo $OPENAI_API_KEY
# 키가 출력되면 성공!
```

---

## 🪟 Windows 설정

### 방법 1: GUI 사용 (추천)

#### 1. 시스템 속성 열기
- `Windows 키 + R` → `sysdm.cpl` 입력 → Enter
- 또는: 제어판 → 시스템 → 고급 시스템 설정

#### 2. 환경 변수 설정
1. `고급` 탭 → `환경 변수` 버튼 클릭
2. `사용자 변수` 영역에서 `새로 만들기` 클릭
3. 각 API 키 추가:
   - 변수 이름: `OPENAI_API_KEY`
   - 변수 값: `sk-proj-your-key-here`
   - `확인` 클릭
4. 같은 방법으로 `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` 추가

#### 3. 적용
- 모든 창에서 `확인` 클릭
- **터미널/PowerShell 재시작** (중요!)

### 방법 2: PowerShell 사용

#### 1. PowerShell을 관리자 권한으로 실행

#### 2. 명령어 실행

```powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-proj-your-key', 'User')
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'sk-ant-your-key', 'User')
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', 'AIza-your-key', 'User')
```

#### 3. PowerShell 재시작 후 확인

```powershell
$env:OPENAI_API_KEY
# 키가 출력되면 성공!
```

### 방법 3: CMD 사용

```cmd
setx OPENAI_API_KEY "sk-proj-your-key"
setx ANTHROPIC_API_KEY "sk-ant-your-key"
setx GOOGLE_API_KEY "AIza-your-key"
```

**주의**: CMD 재시작 필요!

---

## 🐳 Docker 사용 시

### docker run
```bash
docker run \
  -e OPENAI_API_KEY="your-key" \
  -e ANTHROPIC_API_KEY="your-key" \
  -e GOOGLE_API_KEY="your-key" \
  your-image
```

### docker-compose.yml
```yaml
services:
  app:
    image: your-image
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
```

---

## 📄 .env 파일 사용 (대안)

시스템 환경 변수 대신 프로젝트 폴더에 `.env` 파일을 만들 수 있습니다:

### 1. .env 파일 생성
```bash
cp .env.example .env
```

### 2. .env 파일 편집
```bash
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=AIza-your-key-here
```

### 3. Git에 커밋하지 마세요!
`.env` 파일은 이미 `.gitignore`에 포함되어 있습니다.

---

## ✅ 설정 확인

앱을 실행하고 확인:
```bash
streamlit run app.py
```

- ✅ 환경 변수가 설정되었다면: 사이드바에 "시스템 환경 변수에서 자동 로드됨" 표시
- ⚠️ 설정되지 않았다면: "환경 변수가 설정되지 않았습니다" 경고 (직접 입력 가능)

---

## 🔒 보안 팁

1. **절대 API 키를 코드에 직접 작성하지 마세요**
2. **Git에 .env 파일을 커밋하지 마세요**
3. **API 키를 공개 저장소에 올리지 마세요**
4. **정기적으로 API 키를 갱신하세요**
5. **사용하지 않는 키는 즉시 삭제하세요**

---

## 🆘 문제 해결

### Q: 환경 변수를 설정했는데 앱에서 인식하지 못해요
A: 터미널/PowerShell을 **완전히 종료하고 다시 시작**하세요.

### Q: macOS에서 .zshrc를 수정했는데 적용이 안 돼요
A: `source ~/.zshrc` 명령어를 실행하거나 터미널을 재시작하세요.

### Q: Windows에서 setx 명령어가 작동하지 않아요
A: CMD를 **관리자 권한**으로 실행하고 다시 시도하세요.

### Q: .env 파일을 만들었는데 작동하지 않아요
A: 파일 이름이 정확히 `.env`인지 확인하세요 (`.env.txt` 아님).

---

## 🎯 우선순위

애플리케이션은 다음 순서로 API 키를 찾습니다:

1. **시스템 환경 변수** (우선)
2. **.env 파일**
3. **앱 내 직접 입력** (마지막)

시스템 환경 변수 설정을 권장합니다! 🌟
