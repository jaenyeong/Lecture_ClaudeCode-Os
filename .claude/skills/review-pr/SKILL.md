---
name: review-pr
description: 코드 변경분(PR 또는 로컬 diff)을 리뷰어 에이전트로 분석하고 리포트를 생성하는 오케스트레이터. "/review-pr", "리뷰해줘", "PR 리뷰" 같은 트리거에 반응한다. PR URL/번호를 주면 GitHub PR을 가져오고, 인자가 없으면 로컬 git diff를 본다. **MVP 단계**라 현재는 `code-reviewer` 단독 호출이며, 추후 security/test/architecture/spec/side-effect/hygiene 리뷰어로 확장 예정.
---

# /review-pr (MVP)

NEXTSTEP "나만의 Claude OS 만들기" 1주차 PRACTICE(`1주차.pdf` p25–26 "오케스트레이터")의 산출물. **스킬 + 에이전트가 협력해 목표(코드 리뷰)를 달성하는 워크플로우**의 첫 사이클(MVP).

## 0) 이 스킬의 위치 (L2 Pipeline)

프로젝트 README의 4-Layer 구조에서 **L2 Pipeline Skill**에 해당. L1 atomic skill(`/commit` 등)이나 L3 agent(`code-reviewer` 등)를 *조합*해 목적을 달성한다.

> MVP 흐름 (3단계, 단일 라운드):
>
> ```
> [1. Intake]  →  [2. Code Review]  →  [3. Report]
> ```
>
> v5 풀 스펙(9단계, 다관점 병렬, clarification, iteration)으로 가는 길은 본 파일 *맨 아래* "가지치기 로드맵" 참고.

## 트리거

다음 모두에 반응:

- `/review-pr` (인자 없음 또는 `<PR URL>` / `#<번호>`)
- 자연어: "리뷰해줘", "PR 리뷰", "코드 리뷰 부탁"
- 자연어 + URL: "https://github.com/.../pull/42 리뷰해줘"

옵션 플래그:
- `--comment` — 결과를 PR 코멘트로도 게시 (PR 모드일 때만)
- `--working` — local 모드의 서브스코프를 *working tree + untracked* 로 한정 (작업 중 점검용)
- `--committed` — local 모드의 서브스코프를 *origin/main...HEAD* (커밋만) 로 한정 (푸시 직전 점검용)
- 플래그가 없으면 local 모드는 기본 `all` 스코프 (committed + working + untracked 합집합) — *지금 푸시하면 올라갈 모든 것*을 본다는 의미

## 1) Intake — 입력 형태 판정 + diff 수집

### 1-A) 모드 + 서브스코프 판정

먼저 모드(pr / local):

| 신호 | 모드 |
|---|---|
| 인자에 PR URL (`https://github.com/.../pull/N`) 포함 | **pr** |
| 인자에 `#N` 또는 `--pr N` 포함 | **pr** |
| 인자 없음 (또는 local 서브스코프 플래그만) | **local** |

PR 모드 신호가 있는데 `gh` CLI가 인증 안 되어 있으면 사용자에게 안내 후 중단.

local 모드일 때 추가로 **서브스코프** 판정:

| 플래그 | 서브스코프 | 의미 | 비교 대상 |
|---|---|---|---|
| (없음) | **all** (기본) | 지금 푸시하면 올라갈 모든 것 | `origin/main..HEAD` ∪ `git diff HEAD` ∪ untracked |
| `--committed` | **committed** | 커밋만 (작업 트리 무시) | `origin/main...HEAD` |
| `--working` | **working** | 작업 트리만 (커밋 무시) | `git diff HEAD` ∪ untracked |

→ 이 표에서 `SCOPE` 변수를 정한다.

### 1-B) PR 모드

```bash
# PR 메타 조회
gh pr view <PR> --json number,title,body,baseRefName,headRefName,files

# diff 가져오기
gh pr diff <PR>
```

→ 변수 정리:
- `BASE_REF` = `baseRefName`
- `HEAD_REF` = `headRefName`
- `INPUT_REF` = PR URL 또는 `#<번호>`
- `FILES_LIST` = `files[].path` (+ 추가/삭제 라인 수)

### 1-C) Local 모드

> **zsh alias 주의**: 일부 환경의 zsh에서 `git diff --stat` 호출이 alias 충돌(`_safe_eval` 등)로 실패할 수 있다. 안전을 위해 `/bin/bash -c '...'` 로 감싸 실행한다.

먼저 공통 변수:

```bash
CURRENT=$(git rev-parse --abbrev-ref HEAD)

# 베이스 (origin/main 우선)
BASE=$(git rev-parse --verify origin/main 2>/dev/null >/dev/null && echo "origin/main" \
       || (git rev-parse --verify origin/master 2>/dev/null >/dev/null && echo "origin/master") \
       || echo "main")
```

서브스코프별 diff 수집:

#### SCOPE = `committed`

```bash
/bin/bash -c "git diff --stat ${BASE}...HEAD"
/bin/bash -c "git diff ${BASE}...HEAD"
/bin/bash -c "git diff --name-only ${BASE}...HEAD"
```

#### SCOPE = `working`

```bash
# tracked 파일의 working tree 변경 (staged + unstaged)
/bin/bash -c "git diff HEAD --stat"
/bin/bash -c "git diff HEAD"
/bin/bash -c "git diff HEAD --name-only"

# untracked 파일 목록 (.gitignore 존중)
/bin/bash -c "git ls-files --others --exclude-standard"
```

untracked 파일은 *전체 내용*을 synthetic diff(`+` 라인)로 변환해 diff 본문에 포함시킨다:

```bash
for f in $(git ls-files --others --exclude-standard); do
  echo "diff --git a/$f b/$f"
  echo "new file mode 100644"
  echo "--- /dev/null"
  echo "+++ b/$f"
  awk '{print "+"$0}' "$f"
done
```

> 거대 파일(>200KB)이나 바이너리는 *파일명만* 포함하고 본문은 "(binary/large file omitted)"로 대체.

#### SCOPE = `all` (기본)

위 `committed` + `working` *합집합*. 중복 파일은 working 쪽이 우선 (가장 최신 상태).

```bash
# committed 부분
/bin/bash -c "git diff ${BASE}..HEAD --stat"     # 주의: 3점 X, 2점 (단순 비교)
/bin/bash -c "git diff ${BASE}..HEAD"

# working 부분 (HEAD 기준 변경 + untracked, 위 working 절차 그대로)
```

→ 모든 SCOPE에 공통:
- 변경 0개면 사용자에게 알리고 종료. (빈 리뷰는 생성하지 않는다.)
- 변수 정리:
  - `BASE_REF` = `${BASE}`
  - `HEAD_REF` = `${CURRENT}` (working 포함 시 `${CURRENT} + working tree`)
  - `INPUT_REF` = SCOPE 따라: `${BASE}...HEAD` / `working tree` / `${BASE}..HEAD + working tree`

### 1-D) 슬러그 생성

리포트 파일명에 쓸 슬러그:
- PR 모드: PR 제목 → 영문 소문자 + 케밥 + 50자 truncate
- Local 모드: `git log -1 --pretty=%s` → 위와 동일 처리

```bash
DATE=$(date +%Y-%m-%d)
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-//;s/-$//' | cut -c1-50)
REPORT_PATH="docs/reviews/${DATE}-${SLUG}.md"
```

`docs/reviews/` 디렉터리가 없으면 만든다.

## 2) Code Review — `code-reviewer` 에이전트 spawn

`Task` 도구로 호출:

```
Task(
  subagent_type="code-reviewer",
  description="Review code correctness/logic/maintainability",
  prompt="""
모드: {{MODE}}
입력: {{INPUT_REF}}
베이스: {{BASE_REF}}
헤드: {{HEAD_REF}}

변경 파일:
{{FILES_LIST}}

(PR 모드 한정) PR 제목: {{PR_TITLE}}
(PR 모드 한정) PR 본문:
{{PR_BODY}}

Diff:
{{DIFF}}
"""
)
```

> diff 본문이 매우 크면 (수만 라인) 핵심 파일만 prompt에 넣고 *나머지는 파일명 리스트와 통계만* 전달. 에이전트가 필요 시 `Read`로 직접 본다.

에이전트가 markdown 보고를 돌려준다. 이 보고는 **수정하지 않고 그대로** 리포트의 `code-reviewer` 섹션에 삽입한다.

## 3) Report — 템플릿 채우기 + 저장 + 콘솔 출력

### 3-A) 템플릿 로딩

`.claude/skills/review-pr/templates/report.md` 를 읽고 `{{...}}` 플레이스홀더를 위에서 수집한 값으로 치환:

| 플레이스홀더 | 값 |
|---|---|
| `{{TIMESTAMP}}` | `date -Iseconds` |
| `{{DATE}}` | 위 `${DATE}` |
| `{{SLUG}}` | 위 `${SLUG}` |
| `{{MODE}}` | `pr` 또는 `local` |
| `{{INPUT_REF}}` / `{{BASE_REF}}` / `{{HEAD_REF}}` | 위에서 정리 |
| `{{FILES_CHANGED}}` | 파일 수 |
| `{{LINES_ADDED}}` / `{{LINES_REMOVED}}` | `git diff --shortstat` 파싱 |
| `{{REVIEWERS}}` | `code-reviewer` (MVP) |
| `{{FILES_LIST}}` | 파일별 `+추가/-삭제` 리스트 |
| `{{CODE_REVIEWER_OUTPUT}}` | 에이전트 보고 본문 |
| `{{COUNT_*}}` | 에이전트 보고의 라벨 카운트 (🔴🟠🟡🟢) |
| `{{NEXT_ACTION}}` | 카운트 기반 한 줄 권고 (템플릿 주석 규칙 참고) |

### 3-B) 파일 저장

치환한 결과를 `${REPORT_PATH}`에 저장.

### 3-C) 콘솔 요약

사용자에게 보여줄 짧은 요약 (5–10줄):

```
✅ Code review 완료

모드: {{MODE}} ({{INPUT_REF}})
변경: {{FILES_CHANGED}} 파일, +{{LINES_ADDED}} / -{{LINES_REMOVED}}
결과: 🔴 N / 🟠 N / 🟡 N / 🟢 N

→ 다음 액션: {{NEXT_ACTION}}
→ 전체 리포트: {{REPORT_PATH}}
```

### 3-D) 옵션: `--comment` (PR 모드 한정)

`--comment` 플래그가 켜져 있고 모드가 `pr`이면, 리포트 본문을 PR 코멘트로 게시:

```bash
gh pr comment <PR> --body-file ${REPORT_PATH}
```

기본은 **게시하지 않음**. 사용자가 명시적으로 켤 때만 한다 (외부에 보이는 액션이라 항상 확인 후).

## 4) 디스커션·반복 정책 (MVP)

MVP는 **단일 라운드**다. 결과를 보고 사용자가 직접:
- 수정 → 다시 `/review-pr` 호출 (새 라운드)
- 의문 → 메인 대화에서 질문 (이 스킬은 답변하지 않음)

> v5에서는 *자동 라운드 1 + 사용자 명시 시 라운드 1 추가* 정책이 들어오지만, MVP에선 단순화. "한 번 돌려보고 아쉬운 부분 수정"(PDF 26p 02번)에 충실.

## 주의

- **이 스킬은 코드를 수정하지 않는다.** 리뷰 결과는 *제안*까지. 수정은 사용자 또는 다른 스킬 영역.
- **에이전트 보고를 임의로 손대지 않는다.** ✅로 늘리거나 🔴를 빼지 않는다. 받은 그대로 리포트에 삽입.
- **PR 코멘트는 명시 플래그가 있을 때만.** 외부에 보이는 액션이라 기본 OFF.
- **변경이 0개면 빈 리뷰를 만들지 않는다.** 빈 커밋 안 만드는 것과 같은 원칙.
- **에이전트 spawn 실패 시** 콘솔에 사유와 함께 "리뷰 미수행"을 명시한다. 조용히 빈 리포트 만들지 않는다.
- **장기적으로** 이 MVP는 v5 풀 스펙으로 진화한다 — 아래 로드맵 참고.

---

## 가지치기 로드맵 (MVP → v5)

| 단계 | 추가할 것 | README 작업 ID |
|---|---|---|
| MVP+1 | `security-reviewer`, `test-reviewer` 추가 (항상 호출 3명 완성) | #5 |
| MVP+2 | `/check-hygiene` L1 skill + `hygiene-reviewer` (1단계 게이트) | #4, #6 |
| MVP+3 | `interviewer` (Pre/Mid 듀얼 모드) | #7 |
| MVP+4 | 조건부 리뷰어 (`architecture`, `spec`, `side-effect`) + 트리거 임계값 | #2, #6 |
| MVP+5 | Synthesize 단계 + `fact-checker` 통합 + clarification + iteration 라운드 2 | #8 확장 |
| MVP+6 | `/commit` 위생 1차 방어 통합 (이중 방어 완성) | #12 |

각 단계는 *실제 사용 피드백을 본 뒤* 가지치기. 본인 철학 "굵게 시작해서 가지치기"(README 핵심 철학 5번)에 따라 미리 만들지 않는다.
