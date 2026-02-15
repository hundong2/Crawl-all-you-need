# Git 고수 가이드

## 목차
1. [이번 사건 분석: 브랜치 꼬임](#1-이번-사건-분석-브랜치-꼬임)
2. [Git 핵심 개념](#2-git-핵심-개념)
3. [진단 명령어](#3-진단-명령어)
4. [rebase 완전 정복](#4-rebase-완전-정복)
5. [cherry-pick 완전 정복](#5-cherry-pick-완전-정복)
6. [merge vs rebase vs squash 비교](#6-merge-vs-rebase-vs-squash-비교)
7. [stash 활용](#7-stash-활용)
8. [실수 복구 기술](#8-실수-복구-기술)
9. [오픈소스 기여 전체 워크플로우](#9-오픈소스-기여-전체-워크플로우)
10. [push 전 git pull이 필요한가?](#10-push-전-git-pull이-필요한가)
11. [PR 작성 요령](#11-pr-작성-요령)
12. [.gitignore 패턴](#12-gitignore-패턴)
13. [빠른 참조 카드](#13-빠른-참조-카드)

---

## 1. 이번 사건 분석: 브랜치 꼬임

### 문제 상황
```
로컬 claude 브랜치가 origin/claude와 "35개 vs 2개" 커밋으로 diverge됨
```

### 원인
로컬 `claude` 브랜치가 `origin/main`의 커밋 히스토리를 모두 포함한 채 쌓임.
브랜치의 베이스(base)가 잘못 설정된 상태.

```
origin/main:  A - B - C - D - E - F  (계속 쌓임)

origin/claude:                 G - H  (실제 claude 작업만 있어야 할 브랜치)

로컬 claude:  A - B - C - D - E - F - G' - H' - ...
              ↑ origin/main 이력이 통째로 포함되어 있음 (잘못된 상태)
```

### 진단 명령어
```bash
# 브랜치 diverge 상태 확인
git status
# "다른 커밋이 각각 35개와 2개 있습니다" → 35개 앞서고 2개 뒤쳐짐

# 각 브랜치 히스토리 비교
git log --oneline origin/claude
git log --oneline origin/main

# 특정 폴더만 diff 비교 (핵심 기술)
git diff origin/claude HEAD -- claude/
# 출력이 없으면 해당 폴더는 차이 없음 → reset --hard로 해결 가능
```

### 해결
```bash
# 로컬 브랜치를 원격 브랜치에 강제 맞춤
git reset --hard origin/claude
```

---

## 2. Git 핵심 개념

### HEAD, 브랜치, 커밋의 관계
```
HEAD → feature/login → [abc1234] → [def5678] → [514fbaf]
        ↑브랜치(포인터)   ↑현재커밋     ↑이전커밋      ↑최초커밋
```
- **HEAD**: 내가 지금 보고 있는 위치 (포인터)
- **브랜치**: 특정 커밋을 가리키는 이름표 (브랜치 자체는 파일 1개)
- **커밋**: 변경사항의 스냅샷 (내용 + 부모커밋 해시 포함)

### origin vs local
```
origin/main  ← GitHub의 main (git fetch로 갱신됨)
main         ← 로컬 main (origin/main을 추적)

git fetch    : 원격 정보 가져오기 (워킹디렉토리 변경 없음)
git pull     = git fetch + git merge (또는 rebase)
```

### 3-tree 구조
```
[워킹디렉토리] → git add → [스테이지(Index)] → git commit → [저장소(HEAD)]
                ← git restore              ← git reset HEAD
```

---

## 3. 진단 명령어

### 상태 파악
```bash
git status                           # 현재 상태 한눈에
git log --oneline -10                # 최근 10개 커밋 요약
git log --oneline --graph --all      # 모든 브랜치 그래프 시각화 (최고 자주 씀)
git branch -a                        # 로컬+원격 모든 브랜치 목록
git remote -v                        # 연결된 원격 저장소 목록
```

### 차이 비교
```bash
git diff                             # 스테이지 안된 변경사항 (워킹↔스테이지)
git diff --staged                    # 스테이지된 변경사항 (스테이지↔HEAD)
git diff main HEAD                   # 두 브랜치 전체 비교
git diff main HEAD -- 경로/          # 특정 폴더/파일만 비교
git diff main...HEAD --stat          # 분기 이후 변경된 파일 목록만
```
> `main..HEAD` (두 점): main에 없고 HEAD에만 있는 커밋
> `main...HEAD` (세 점): 공통 조상 이후 양쪽 모두의 변경사항

### 커밋 추적
```bash
git show 커밋해시                    # 특정 커밋 내용 보기
git show 커밋해시 --stat             # 커밋에서 변경된 파일 목록
git log --follow 파일명              # 파일의 전체 히스토리 (이름변경 추적)
git blame 파일명                     # 각 줄이 누가/언제 수정했는지
git log -S "검색어" --oneline        # 해당 문자열을 추가/삭제한 커밋 찾기
git log --author="이름" --oneline    # 특정 사람의 커밋만
```

---

## 4. rebase 완전 정복

### rebase란?
커밋들의 "베이스(시작점)"를 다른 커밋으로 옮기는 작업.
히스토리를 직선으로 만들어 깔끔하게 유지할 때 사용.

```
[merge 결과]                    [rebase 결과]
      main                            main
A-B-C-D                         A-B-C-D
    \   \                                \
     E-F-M (M=merge commit)              E'-F' (커밋이 재작성됨)
```

### 기본 rebase (브랜치 베이스 이동)
```bash
# feature 브랜치를 최신 main 위로 이동
git checkout feature/login
git rebase main

# 또는 원격 main 기준으로
git fetch origin
git rebase origin/main
```

### interactive rebase (커밋 정리 핵심 기술)
```bash
git rebase -i HEAD~3     # 최근 3개 커밋을 인터랙티브하게 편집
git rebase -i 커밋해시   # 해당 커밋 이후를 모두 편집
```

에디터에서 사용하는 명령어:
```
pick   abc1234  feat: 로그인 구현       ← 그대로 유지
squash def5678  fix: 오타 수정          ← 위 커밋에 합치기 (s로 줄여도 됨)
squash ghi9012  fix: 다시 오타 수정     ← 위 커밋에 합치기
reword jkl3456  refactor: 코드 정리     ← 커밋 메시지만 수정 (r로 줄여도 됨)
drop   mno7890  wip: 임시 저장          ← 이 커밋 삭제 (d로 줄여도 됨)
edit   pqr2345  feat: 결제 기능         ← 이 커밋에서 멈추고 수정 허용
```

실전 예시: 3개의 작은 커밋을 1개로 합치기
```bash
git rebase -i HEAD~3
# 에디터에서:
# pick abc1234 feat: 버튼 추가
# s    def5678 fix: 버튼 색상
# s    ghi9012 fix: 버튼 크기
# 저장 후 커밋 메시지 편집 → 깔끔한 1개 커밋 완성
```

### rebase 충돌 해결
```bash
git rebase origin/main
# 충돌 발생 시:
# 1. 충돌 파일 수동 수정
# 2. git add 충돌파일
# 3. git rebase --continue    # 다음 커밋으로 진행
#    git rebase --skip         # 이 커밋 건너뜀
#    git rebase --abort        # rebase 전체 취소 (원래 상태로 복귀)
```

### rebase 후 push
```bash
# rebase는 커밋 해시를 바꾸므로 force push 필요
git push origin feature/login --force-with-lease
# --force-with-lease: 다른 사람이 중간에 push한 게 있으면 거부 (안전)
# --force: 무조건 덮어씀 (위험, 공유 브랜치에서 금지)
```

> **주의**: `main`, `develop` 같은 공유 브랜치에는 절대 force push 금지.
> rebase는 본인의 feature 브랜치에서만 사용할 것.

---

## 5. cherry-pick 완전 정복

### cherry-pick이란?
다른 브랜치의 특정 커밋 하나(또는 여러 개)만 골라서 현재 브랜치에 적용.

```
main:    A - B - C - D
                     ↑
feature: A - B - E - F - G
                     ↑
                     이것만 main에 가져오고 싶다
```

### 기본 사용법
```bash
# 특정 커밋 1개 가져오기
git cherry-pick abc1234

# 여러 커밋 연속으로 가져오기 (abc부터 def까지)
git cherry-pick abc1234..def5678

# 여러 커밋 개별 지정
git cherry-pick abc1234 def5678 ghi9012

# 커밋 내용은 적용하되 커밋은 아직 하지 않기 (스테이지 상태로 멈춤)
git cherry-pick abc1234 --no-commit
```

### 실전 사용 사례
```bash
# 1. hotfix: 급하게 main에 버그 수정 커밋만 가져올 때
git checkout main
git cherry-pick abc1234   # feature 브랜치의 버그수정 커밋만 적용

# 2. 실수로 잘못된 브랜치에 커밋했을 때
git checkout 올바른브랜치
git cherry-pick 잘못된브랜치의커밋해시
git checkout 잘못된브랜치
git reset --hard HEAD~1   # 잘못된 브랜치에서 커밋 제거
```

### cherry-pick 충돌 해결
```bash
git cherry-pick abc1234
# 충돌 발생 시:
# 1. 충돌 파일 수동 수정
# 2. git add 충돌파일
# 3. git cherry-pick --continue   # 계속 진행
#    git cherry-pick --abort      # 취소 (원래 상태로)
```

---

## 6. merge vs rebase vs squash 비교

| 방식 | 히스토리 | 커밋수 | 언제 쓰나 |
|------|---------|--------|-----------|
| `merge` | 분기가 보임 (merge commit 생성) | 유지 | 공유 브랜치 병합 (main←feature) |
| `rebase` | 직선으로 정리됨 | 유지 | PR 전 feature 브랜치 정리 |
| `squash merge` | 직선, 깔끔 | 1개로 합쳐짐 | PR 머지 시 (GitHub 권장) |

### 각 방식 명령어
```bash
# merge (기본, merge commit 생성)
git checkout main
git merge feature/login

# merge --no-ff (fast-forward 방지, 반드시 merge commit 생성)
git merge --no-ff feature/login

# squash merge (feature의 모든 커밋을 1개로 합쳐서 main에 추가)
git merge --squash feature/login
git commit -m "feat: 로그인 기능 추가"

# rebase 후 merge (히스토리 직선)
git checkout feature/login
git rebase main
git checkout main
git merge feature/login   # 이때는 fast-forward로 됨
```

---

## 7. stash 활용

작업 중인 내용을 임시로 서랍에 넣어두는 기능.
브랜치를 급하게 바꿔야 할 때 유용.

```bash
git stash                    # 현재 변경사항 임시 저장
git stash push -m "메시지"   # 이름 붙여서 저장
git stash list               # 저장된 stash 목록 확인
git stash pop                # 가장 최근 stash 꺼내기 (목록에서 삭제)
git stash apply stash@{0}    # 특정 stash 적용 (목록에 유지)
git stash drop stash@{0}     # 특정 stash 삭제
git stash clear              # 모든 stash 삭제
```

실전 흐름:
```bash
# 1. feature/login 작업 중 긴급 버그 발생
git stash push -m "로그인 폼 작업 중"

# 2. hotfix 브랜치로 이동해서 버그 수정
git checkout hotfix/crash
# ... 수정 후 커밋 ...

# 3. 원래 브랜치로 돌아와서 작업 재개
git checkout feature/login
git stash pop
```

---

## 8. 실수 복구 기술

### reset 3종 세트
```bash
git reset --soft HEAD~1    # 커밋만 취소, 변경사항은 스테이지에 유지
git reset --mixed HEAD~1   # 커밋+스테이지 취소, 파일은 유지 (기본값)
git reset --hard HEAD~1    # 커밋+스테이지+파일 모두 되돌림 (위험)
```

### revert (이미 push한 커밋 취소할 때)
```bash
# reset은 히스토리를 지우므로 공유 브랜치에서 금지
# revert는 "취소했다"는 새 커밋을 추가하는 방식 → 안전
git revert abc1234           # 해당 커밋을 되돌리는 새 커밋 생성
git revert HEAD~3..HEAD      # 최근 3개 커밋 모두 revert
git revert abc1234 --no-edit # 커밋 메시지 편집 없이 바로 revert
```

### reflog (최후의 보루)
```bash
git reflog                   # 모든 HEAD 이동 이력 (30일 보존)
# 예시 출력:
# abc1234 HEAD@{0}: reset: moving to origin/claude
# def5678 HEAD@{1}: commit: add claude
# ...
git reset --hard HEAD@{1}    # 원하는 시점으로 복구
```
> `reset --hard`로 날렸어도 reflog로 복구 가능. git의 블랙박스.

### 특정 파일만 복구
```bash
git restore 파일명                       # 마지막 커밋 상태로 복원
git restore --staged 파일명              # 스테이지에서 내리기
git checkout 커밋해시 -- 파일명          # 특정 커밋 시점 파일로 복원
git restore --source=커밋해시 파일명     # 위와 동일 (최신 문법)
```

---

## 9. 오픈소스 기여 전체 워크플로우

### 전체 흐름 (한눈에)
```
[원본 저장소] → Fork → [내 GitHub 저장소] → clone → [로컬]
                                                        ↓ 작업
[원본 저장소] ← PR ← [내 GitHub 저장소] ← push ← [로컬]
```

### Step 1: Fork & Clone
```bash
# GitHub에서 Fork 버튼 클릭 → 내 계정에 복사본 생성

# 내 Fork를 로컬에 clone
git clone https://github.com/내계정/프로젝트.git
cd 프로젝트

# 원본 저장소를 upstream으로 등록 (핵심!)
git remote add upstream https://github.com/원본계정/프로젝트.git

# 확인
git remote -v
# origin    https://github.com/내계정/프로젝트.git (fetch)
# origin    https://github.com/내계정/프로젝트.git (push)
# upstream  https://github.com/원본계정/프로젝트.git (fetch)
# upstream  https://github.com/원본계정/프로젝트.git (push)
```

### Step 2: 작업 브랜치 생성
```bash
# 항상 최신 upstream main에서 시작
git fetch upstream
git checkout upstream/main -b feature/내기능
# 또는
git checkout main
git reset --hard upstream/main
git checkout -b feature/내기능
```

### Step 3: 작업 & 커밋
```bash
# 파일 수정 후
git add 파일명              # 특정 파일만 스테이지
git add -p                  # 변경사항을 hunk 단위로 선택적 스테이지 (강력 추천)
git commit -m "feat: 로그인 기능 추가"

# 커밋 메시지 컨벤션 (Conventional Commits)
# feat: 새 기능
# fix: 버그 수정
# docs: 문서 변경
# style: 코드 스타일 (로직 변경 없음)
# refactor: 리팩토링
# test: 테스트 추가/수정
# chore: 빌드, 설정 변경
```

### Step 4: PR 전 동기화 (핵심 질문 답변)
```bash
# 원본 저장소의 최신 변경사항 반영
git fetch upstream
git rebase upstream/main    # 내 커밋들을 최신 main 위로 이동
# 충돌 있으면 해결 후 git rebase --continue
```

> **여기서 핵심 질문**: `git pull origin main`이 꼭 필요한가? → 다음 섹션 참고

### Step 5: Push & PR 생성
```bash
# 내 Fork에 push
git push origin feature/내기능

# rebase 후 force push가 필요할 수 있음
git push origin feature/내기능 --force-with-lease

# GitHub에서 PR 생성
# base: 원본저장소/main ← compare: 내계정/feature/내기능
```

### Step 6: 리뷰 후 수정
```bash
# 리뷰어 피드백 반영 후
git add 수정파일
git commit -m "fix: 리뷰 반영 - 변수명 수정"
# 또는 이전 커밋에 합치려면
git commit --amend          # 마지막 커밋에 포함
# 그 후 force push
git push origin feature/내기능 --force-with-lease
```

### Step 7: PR 머지 후 정리
```bash
# 머지된 후 로컬 정리
git fetch upstream
git checkout main
git reset --hard upstream/main   # 로컬 main 동기화
git branch -d feature/내기능     # 로컬 브랜치 삭제
git push origin --delete feature/내기능  # 원격 브랜치 삭제
```

---

## 10. push 전 git pull이 필요한가?

이 질문은 상황에 따라 다르다. 명확하게 정리한다.

### 상황 1: 혼자 작업하는 개인 브랜치 (feature 브랜치)

```bash
# 혼자만 사용하는 브랜치라면 pull 없이 push 가능
git push origin feature/내기능   # 바로 push OK
```

단, main이 많이 앞서갔다면 PR 전에 동기화 권장:
```bash
git fetch upstream           # 또는 git fetch origin
git rebase upstream/main     # 내 커밋들을 최신 main 위로 올림
git push --force-with-lease  # rebase 후에는 force push 필요
```

### 상황 2: PR을 올릴 때

```
PR만 올리면 되는가? → 기술적으로 YES. 하지만 충돌이 있으면 GitHub가 merge 거부.
pull이 필요한가?   → 꼭은 아니지만, rebase/merge로 동기화하면 리뷰 받기 쉬움.
```

**PR 전 동기화가 필요한 경우:**
- base 브랜치(main)에 충돌을 일으키는 변경사항이 생겼을 때
- CI/CD 테스트를 최신 코드 기준으로 통과시켜야 할 때
- 리뷰어가 오래된 코드 기반에서 리뷰하지 않게 하려면

```bash
# 방법 A: rebase (권장 - 히스토리 깔끔)
git fetch origin
git rebase origin/main

# 방법 B: merge (히스토리에 merge commit 남음)
git pull origin main   # = git fetch + git merge origin/main
```

### 상황 3: 공유 브랜치(main, develop)에 push할 때

```bash
# 반드시 최신 상태 확인 후 push
git pull origin main         # 최신 받기
# 충돌 해결 후
git push origin main
```

### 한 줄 결론

| 상황 | pull 필요? |
|------|-----------|
| 혼자 쓰는 feature 브랜치 push | 선택사항 (충돌 없으면 불필요) |
| PR 생성 전 | 권장 (충돌 있으면 필수) |
| 공유 브랜치(main)에 push | 필수 |
| rebase 후 force push | pull 대신 fetch+rebase |

> **실무 황금률**: `git push` 전에 `git fetch`는 항상 해서 상태를 파악한다.
> pull = fetch + merge 인데, merge commit이 생기는 게 싫으면 rebase를 쓴다.

---

## 11. PR 작성 요령

### 좋은 PR의 특징
- 하나의 PR = 하나의 목적 (기능 추가 + 버그 수정을 섞지 않음)
- 커밋 단위가 논리적으로 나뉘어져 있음
- 변경 이유, 방법, 테스트 방법이 명확히 기술됨

### PR 제목 컨벤션
```
feat: 로그인 기능 추가 (#이슈번호)
fix: 결제 시 NullPointerException 수정
docs: API 인증 방법 README에 추가
refactor: UserService 의존성 분리
```

### PR 본문 템플릿
```markdown
## 변경 사항
- 로그인 폼 UI 구현
- JWT 토큰 발급 API 연동

## 변경 이유
Fixes #42 - 사용자 인증 기능이 없어 모든 사용자가 모든 데이터에 접근 가능했음

## 테스트 방법
1. `npm start` 로 서버 실행
2. /login 페이지 접속
3. 이메일/비밀번호 입력 후 로그인 확인

## 스크린샷 (UI 변경 시)
(이미지 첨부)

## 체크리스트
- [x] 테스트 추가함
- [x] 문서 업데이트함
- [x] 기존 테스트 모두 통과
```

### GitHub CLI로 PR 생성
```bash
# gh cli 사용 시 터미널에서 PR 생성 가능
gh pr create --title "feat: 로그인 기능" --body "변경사항 설명" --base main

# PR 목록 확인
gh pr list

# PR 상태 확인
gh pr status

# PR 리뷰 요청
gh pr create --reviewer 리뷰어아이디
```

---

## 12. .gitignore 패턴

```gitignore
# 폴더 전체
node_modules/
__pycache__/
.venv/
dist/
build/

# 특정 확장자
*.pyc
*.log
*.env

# 예외 처리 (! 사용)
*.log
!important.log    # important.log는 추적

# OS 파일
.DS_Store
Thumbs.db
```

이미 추적 중인 파일을 .gitignore에 추가할 때:
```bash
git rm --cached 파일명         # 트래킹 중단 (파일은 유지)
git rm --cached -r 폴더/       # 폴더 전체 트래킹 중단
git commit -m "chore: remove tracked build files"
```

---

## 13. 빠른 참조 카드

### 상태 파악
| 목적 | 명령어 |
|------|--------|
| 현재 상태 | `git status` |
| 브랜치 그래프 | `git log --oneline --graph --all` |
| 원격 브랜치 포함 목록 | `git branch -a` |
| 내 커밋만 보기 | `git log origin/main..HEAD --oneline` |
| 분기점 찾기 | `git merge-base main HEAD` |

### 복구
| 목적 | 명령어 |
|------|--------|
| 마지막 커밋 취소 (파일 유지) | `git reset --soft HEAD~1` |
| 특정 파일 되돌리기 | `git restore 파일명` |
| 이미 push한 커밋 취소 | `git revert 커밋해시` |
| 뭔가 날렸을 때 | `git reflog` → `git reset --hard HEAD@{N}` |
| 브랜치를 원격에 맞추기 | `git reset --hard origin/브랜치` |

### 브랜치
| 목적 | 명령어 |
|------|--------|
| 브랜치 생성+이동 | `git switch -c 브랜치명` |
| 브랜치 삭제 (로컬) | `git branch -d 브랜치명` |
| 브랜치 삭제 (원격) | `git push origin --delete 브랜치명` |
| 원격 정리된 브랜치 로컬 정리 | `git remote prune origin` |

### 히스토리 정리
| 목적 | 명령어 |
|------|--------|
| 커밋 합치기 (3개) | `git rebase -i HEAD~3` → squash |
| 최신 main 반영 | `git fetch && git rebase origin/main` |
| 특정 커밋만 가져오기 | `git cherry-pick 커밋해시` |
| 작업 임시 저장 | `git stash push -m "설명"` |
| 임시 저장 꺼내기 | `git stash pop` |

### push 전 체크리스트
```bash
git fetch origin                       # 1. 원격 최신 상태 가져오기
git log origin/main..HEAD --oneline    # 2. 내 커밋 목록 확인
git diff origin/main HEAD --stat       # 3. 변경 파일 확인
git rebase origin/main                 # 4. 충돌 있으면 여기서 해결
git push origin feature/브랜치        # 5. push
```
---

## 14. PR 생성 전 pull이 필요한가? (심화)

### PR 생성과 PR 머지는 다르다

```
git push → gh pr create   ← 충돌 검사 안 함 (항상 성공)
                ↓
         GitHub PR 페이지
                ↓
         Merge 버튼 클릭  ← 여기서 충돌 검사
```

- **PR 생성**: "이 브랜치를 머지 요청합니다" 등록. 충돌 여부와 무관하게 항상 성공
- **PR 머지**: 실제로 main에 합칠 때 충돌 여부 판단

### 충돌이 나는 조건

충돌은 **같은 파일의 같은 줄**을 양쪽이 다르게 수정했을 때만 발생한다.

```
# 충돌 발생하는 케이스
main:    README.md 10번째 줄 → "버전 1.0"으로 수정
feature: README.md 10번째 줄 → "버전 2.0"으로 수정
→ 충돌

# 충돌 발생하지 않는 케이스
main:    git.md 파일 없음
feature: git.md 파일 새로 추가
→ 충돌 없음 (추가만 했으므로)
```

변경사항이 **전부 추가(+)** 인지 확인하는 방법:
```bash
git diff origin/main HEAD --stat
# 출력에 삭제(-)가 없고 추가(+)만 있으면 충돌 불가능
```

### 충돌이 생겼을 때 해결 방법

**방법 A: GitHub에서 알려줌 (머지 전)**

PR 페이지에 "This branch has conflicts that must be resolved" 표시 → Merge 버튼 비활성화

**방법 B: 로컬에서 미리 해결 후 push (권장)**

```bash
git fetch origin
git rebase origin/main      # 충돌 있으면 여기서 발생
# 충돌 파일 수동 수정
git add 충돌파일
git rebase --continue       # 계속 진행
git push origin 브랜치 --force-with-lease  # rebase 후 force push 필요
```

### 상황별 pull/rebase 필요 여부

| 상황 | pull 필요? | 이유 |
|------|-----------|------|
| 파일 추가만 하는 PR | 불필요 | 충돌 자체가 불가능 |
| 기존 파일 수정 포함 | 권장 | 같은 파일 수정 시 충돌 가능 |
| main이 오래됐고 같은 파일 수정 | 필수 | 안 하면 GitHub에서 Merge 버튼 막힘 |

> **핵심 원칙**: PR 생성은 언제든 가능. 충돌은 머지 시점에 판단된다.
> 기존 파일을 수정하는 PR이라면 `git fetch && git rebase origin/main` 후 push하는 습관을 들이자.
