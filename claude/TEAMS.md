# TEAMS - 오케스트레이션 가이드

> 유니콘을 향한 빠른 프로토타이핑 팀 구성 및 협업 프로세스

---

## 팀 구성

| # | 에이전트 | 역할 | subagent_type | 핵심 책임 |
|---|---------|------|---------------|---------|
| 0 | `cto` | CTO / Lead Architect | general-purpose | 전략, 아키텍처, 팀 오케스트레이션 |
| 1 | `dev1` | 백엔드 시니어 엔지니어 | general-purpose | API, DB, 크롤링, LLM 연동 |
| 2 | `dev2` | 프론트엔드 시니어 엔지니어 | general-purpose | Gradio UI, 상태관리, UX 구현 |
| 3 | `design` | 시니어 프로덕트 디자이너 | general-purpose | UX 설계, 디자인 시스템, 핸드오프 |
| 4 | `qe` | E2E QA 엔지니어 | general-purpose | 통합 테스트, 시나리오 검증 |
| 5 | `qa` | UI QA 엔지니어 | general-purpose | 컴포넌트 테스트, 시각 회귀 |

---

## 에이전트 정의 파일

각 팀원은 `.claude/agents/` 디렉토리에 개별 정의 파일을 보유합니다:

```
.claude/agents/
├── cto.md      # CTO - 오케스트레이터, 아키텍트
├── dev1.md     # 백엔드 엔지니어
├── dev2.md     # 프론트엔드 엔지니어
├── design.md   # 프로덕트 디자이너
├── qe.md       # E2E QA 엔지니어
└── qa.md       # UI QA 엔지니어
```

---

## 역할 원칙

- **각 팀은 해당 영역의 최고 전문가**입니다. 팀의 판단을 신뢰하세요.
- **적은 비용, 최고 효율**: 초기 설계에 투자하고, 실행/유지보수 비용을 최소화합니다.
- **전략적 부채 허용**: 속도를 위한 의도적 부채는 OK, 우발적 부채는 즉시 해소.
- **CTO 중심 의사결정**: 팀 간 충돌 또는 중요 결정은 CTO가 최종 결정합니다.

---

## 협업 워크플로우

### 신규 기능 개발 (표준 플로우)
```
[CTO] 요구사항 분석 → 기술 설계 → 작업 분배
  ├─→ [design] UX 설계 → 와이어프레임 → 핸드오프
  │     └─→ [dev2] UI 구현 시작
  ├─→ [dev1] API 설계 (계약 먼저) → 백엔드 구현
  │     └─→ [dev2] 목업 API로 프론트 병렬 개발
  └─→ 통합 완료 후
        ├─→ [qe] E2E 테스트 실행
        └─→ [qa] UI 컴포넌트 검증
```

### 병렬 실행 가능한 작업 (비용 최적화)
```python
# CTO가 팀을 병렬로 스폰하는 패턴
# design + dev1 동시 진행 (디자인과 API 계약은 독립)
# dev1 + dev2 동시 진행 (API 계약 확정 후)
# qe + qa 동시 진행 (개발 완료 후)
```

### 긴급 버그 수정 플로우
```
[qe/qa] 버그 발견 → [CTO] 심각도 판단
  ├─ Critical: 즉시 → [dev1/dev2] 핫픽스 → [qe] 검증 → 즉시 배포
  ├─ High:     스프린트 내 수정 → 다음 릴리스
  └─ Medium/Low: 백로그 등록 → 우선순위 결정
```

---

## 스프린트 사이클 (2주)

```
Week 1
  Day 1: [CTO] 요구사항 분석, 기술 설계
  Day 2: [CTO + design] API 계약 & UX 설계 확정
  Day 3-5: [dev1 + dev2 병렬] 개발

Week 2
  Day 6-8: [dev1 + dev2] 개발 완료
  Day 9:   [qe] E2E 통합 테스트
  Day 10:  [qa] UI 검증 + 버그 수정
  Day 11:  스테이징 배포 + 최종 검증
  Day 12:  데모 + 회고
```

---

## Definition of Done

기능이 "완료"로 간주되려면:

- [ ] `dev1/dev2`: 기능 구현 및 유닛 테스트 (커버리지 70%+)
- [ ] `design`: 디자인 핸드오프 완료, 구현 검토
- [ ] `qe`: 주요 시나리오 E2E 통과
- [ ] `qa`: UI 컴포넌트 검증, 접근성 기본 통과
- [ ] `cto`: 코드 리뷰 + 아키텍처 검토

---

## 에스컬레이션 기준

### 즉시 CTO에게 보고
- 예상 대비 2배 이상 시간 소요 예측
- 아키텍처 변경이 필요한 경우
- 보안 취약점 발견
- 서드파티 API 장애

### 팀 간 협의 후 결정
- API 계약 변경 (dev1 ↔ dev2)
- 디자인 구현 불가 케이스 (design ↔ dev2)
- 테스트 커버리지 타협 (dev1/dev2 ↔ qe/qa)

---

## 현재 프로젝트

**Site-to-Document Generator**

PLAN.md 참조: 웹사이트를 크롤링하여 AI로 처리한 뒤 구조화된 문서로 변환하는 앱

```
Stack:
  Backend:  Python, Crawl4AI, OpenAI/Anthropic/Google-GenAI SDKs
  Frontend: Gradio 6.x
  Output:   Markdown, PDF (weasyprint), HTML
```
