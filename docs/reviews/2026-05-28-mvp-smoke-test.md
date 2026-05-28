# Code Review Report

> 자동 생성 — `/review-pr` 오케스트레이터 (MVP)

## 메타

| 항목 | 값 |
|---|---|
| 생성 시각 | 2026-05-28T22:15:00+09:00 |
| 모드 | local (scope=all) |
| 입력 | 작업 트리 + untracked (origin/main 대비) |
| 베이스 | origin/main |
| 헤드 | main (working tree 포함) |
| 변경 파일 수 | 4 (`.omc/*` 상태 파일 9개는 노이즈로 제외) |
| 변경 라인 수 | +532 / -1 (synthetic diff 기준) |
| 호출된 리뷰어 | code-reviewer |

## 요약

🔴 BLOCKER: 0 · 🟠 HIGH: 2 · 🟡 MEDIUM: 5 · 🟢 LOW: 4

**다음 권고 액션**: HIGH 2건(3-dot vs 2-dot 불일치, 헤더 레벨 불일치) 검토 후 결정. BLOCKER가 없어 머지/사용 자체는 가능하나, HIGH 둘 다 *워크플로우 결과의 정확성/일관성*에 영향이 있어 곧 패치 권장.

## 변경 파일 목록

- `README.md` (modified, +2/-0)
- `.claude/agents/code-reviewer.md` (new, +180)
- `.claude/skills/review-pr/SKILL.md` (new, just patched, +250)
- `.claude/skills/review-pr/templates/report.md` (new, +70)

**노이즈로 제외된 파일** (`.gitignore` 등재 권장):
- `.omc/project-memory.json`
- `.omc/state/agent-replay-*.jsonl` (3개)
- `.omc/state/subagent-tracking.json`
- `.omc/sessions/*.json` (4개)

## 리뷰 결과

### code-reviewer

## code-reviewer 결과

요약: 🔴 0 / 🟠 2 / 🟡 5 / 🟢 4

### 🔴 BLOCKER

(없음)

### 🟠 HIGH

- **.claude/skills/review-pr/SKILL.md:133** `SCOPE=all` 분기에서 `git diff ${BASE}..HEAD` (2-dot)로 명시하면서 옆 주석에 "주의: 3점 X, 2점 (단순 비교)"라고 적어두었다.
  - 문제: `SCOPE=committed` 절(L96–98)은 동일한 변경분에 대해 `${BASE}...HEAD` (3-dot, merge-base 기준)을 쓴다. 같은 "committed 부분"을 `committed` 모드와 `all` 모드에서 *다른 의미*로 본다는 뜻 — `main`이 앞서 나간 상황에서 `all` 모드는 무관한 main 커밋까지 diff에 포함하게 된다. 의도가 "푸시하면 올라갈 모든 것"이라면 3-dot이 맞다.
  - 제안: L133–134도 `${BASE}...HEAD`로 통일하거나, 2-dot이 진짜 의도였다면 `committed` 절도 2-dot으로 통일하고 주석으로 *왜* 모드별로 다른지 명시.
- **.claude/skills/review-pr/templates/report.md:39 vs .claude/agents/code-reviewer.md:99** 헤더 레벨 불일치로 토큰 치환 시 깨진 마크다운이 나올 수 있다.
  - 문제: 템플릿은 `### code-reviewer` (H3) 아래에 `{{CODE_REVIEWER_OUTPUT}}`를 삽입하는데, 에이전트 스펙의 출력 포맷은 `## code-reviewer 결과` (H2)로 시작하고 그 아래 `### 🔴 BLOCKER` (H3)를 쓴다. 그대로 끼우면 리포트에 H3 아래 H2가 등장(역계층) → 일부 마크다운 렌더러에서 TOC/스타일이 망가짐. 또 템플릿 예시 주석(L48)은 `#### 🔴 BLOCKER` (H4)라고 적혀 있어 *세 곳이 전부 다르다*.
  - 제안: 한쪽으로 통일. 에이전트가 `### code-reviewer 결과` (H3)로 시작하고 하위는 `#### 🔴 ...` (H4)로 내리거나, 템플릿 헤더를 `## 리뷰 결과 / code-reviewer` 같은 구조로 바꿔 에이전트 출력이 자연스럽게 들어가게.

### 🟡 MEDIUM

- **.claude/skills/review-pr/SKILL.md:113–123** untracked 파일을 synthetic diff로 만드는 `for f in $(git ls-files ...)` 루프는 *공백 포함 파일명*에서 깨진다.
  - 문제: word-split 때문에 `My File.txt`가 `My`와 `File.txt` 두 항목으로 분리됨. `awk` 호출이 실패하고 결과 diff가 사일런트로 빠진다.
  - 제안: `git ls-files -z ... | while IFS= read -r -d '' f; do ...; done` 패턴으로 교체. 또한 newline-only 보장 위해 `awk 'BEGIN{} {print "+"$0}'` 대신 직접 sed로 처리하거나 EOF 라인 보장 로직 추가.
- **.claude/skills/review-pr/SKILL.md:154** 슬러그 생성 `tr '[:upper:]' '[:lower:]'` 다음 `tr -cs 'a-z0-9' '-'`로 한글/일본어 등 멀티바이트 문자가 전부 단일 하이픈으로 뭉개진다.
  - 문제: 한국어 강의 저장소에서 커밋 메시지(예: `feat(.claude): 커밋 스킬 추가`)가 슬러그 단계에서 `feat-claude-`처럼 거의 빈 문자열이 되고 50자 truncate 후 의미 없는 파일명 생성. 본 프로젝트 컨텍스트에선 거의 매번 트리거된다.
  - 제안: 한글 유지(`iconv -t ascii//TRANSLIT` 또는 한글 그대로 허용)하거나, 슬러그가 빈/너무 짧으면 `${DATE}-review-${SHORT_SHA}` fallback. 빈 슬러그 가드 자체가 현재 없음.
- **.claude/skills/review-pr/SKILL.md:153 (`date +%Y-%m-%d`) 및 L199 (`date -Iseconds`)** macOS 기본 `date`는 `-Iseconds` 미지원.
  - 문제: 본 환경엔 GNU coreutils가 깔려 있어 통과하지만, 기본 macOS 사용자(특히 강의 수강생) 환경에선 `date: illegal option -- I`로 실패. 그러면 리포트 메타의 `{{TIMESTAMP}}`가 빈 문자열 또는 에러 메시지로 치환됨.
  - 제안: `date +%Y-%m-%dT%H:%M:%S%z` 같은 BSD 호환 포맷으로 교체, 또는 `gdate -Iseconds 2>/dev/null || date +%Y-%m-%dT%H:%M:%S%z` fallback.
- **.claude/skills/review-pr/SKILL.md:127–137 (SCOPE=all)** "working 부분"을 어떻게 합칠지의 *합집합 로직*이 산문으로만 적혀 있고("중복 파일은 working 쪽이 우선") 실제 합치는 명령/절차가 없다.
  - 문제: 메인 에이전트가 이 스킬을 실행할 때 "committed diff + working diff를 그냥 이어붙이면 같은 파일이 두 번 등장"하는 케이스를 어떻게 처리해야 할지 비결정. code-reviewer 에이전트가 같은 파일 두 hunk를 받아 혼란.
  - 제안: 간단한 procedure 1-2줄 추가 — 예: "working diff에 등장하는 파일은 committed diff에서 제외한 뒤 이어붙인다." 또는 파일 단위 dict로 머지하는 의사코드.
- **.claude/skills/review-pr/SKILL.md:140 ("변경 0개면 사용자에게 알리고 종료")** 빈 변경 판정 기준 미명세.
  - 문제: SCOPE=all에서 committed 부분은 있고 working은 비어있을 때, 혹은 그 반대, 또는 untracked만 있을 때 모두 "변경 있음"으로 처리해야 하는데 명확한 판정 룰이 없다. 현재 문구만으론 구현자가 잘못 판단할 여지.
  - 제안: "committed diff + working diff + untracked 파일 *총합* 변경 라인 수 = 0일 때만 종료"라고 명시.
- **.claude/skills/review-pr/SKILL.md:189** "에이전트 보고를 수정하지 않고 그대로 삽입"이 원칙인데, 그러면 템플릿의 `{{COUNT_BLOCKER/HIGH/MEDIUM/LOW}}` (L209)는 *별도로* 본문에서 정규식 파싱해 카운트를 산출해야 한다 — 절차 미명시.
  - 문제: 카운트 산출 방법(예: `### 🔴 BLOCKER` 섹션 아래 `- ` bullet 수를 세는지, 에이전트가 적은 "요약: 🔴 N" 라인을 그대로 신뢰하는지)이 정해지지 않아 구현자별로 다른 값이 나올 수 있다.
  - 제안: "에이전트 출력의 첫 `요약:` 라인을 정규식으로 파싱해 그 숫자를 신뢰한다"라고 한 줄 명시.

### 🟢 LOW

- **.claude/skills/review-pr/SKILL.md:96, 97, 98 등** 모든 `git` 호출을 `/bin/bash -c "..."`로 한 줄 한 줄 감쌌다.
  - 문제: zsh alias 회피 의도는 알겠지만, 같은 변수(`${BASE}`)를 매 줄마다 expand하는 형태는 verbose하고, 여러 줄을 하나의 bash 블록으로 묶으면 가독성과 변수 일관성이 좋아진다.
  - 제안: SCOPE별로 `/bin/bash -c '<<EOS ... EOS'` 한 블록으로 묶거나, 짧은 helper 함수(`gd() { /bin/bash -c "git diff $*"; }`) 도입.
- **.claude/agents/code-reviewer.md:4** `tools: Read, Grep, Glob, Bash` 선언이 있는데 본문에선 `Glob` 사용 시나리오가 한 번도 안 나온다 (Read/Grep만 언급).
  - 제안: Glob 사용 예 한 줄 추가하거나(예: "파일 그룹 단위로 패턴 검색이 필요할 때"), 안 쓸 거면 빼서 권한 표면 축소.
- **README.md:28** 새 줄 "L1 description 필드에 자연어 트리거 키워드를 따옴표로 박아둔다"는 좋은 규약인데 *예시 한 줄이 없다*.
  - 제안: 한 줄 예시 추가 — 예: `description: "커밋해줘"라고 하면 변경분을 Conventional Commits로 묶어 커밋한다.`
- **.claude/skills/review-pr/templates/report.md:10–11** 메타 테이블의 `<!-- pr | local -->` HTML 주석이 마크다운 테이블 셀 안에 있다.
  - 문제: 일부 렌더러(특히 GitHub MD)는 셀 안 HTML 주석을 비표시 처리하지만, raw 보기에서 사용자에게 보이는 게 본 의도라면 위치가 어정쩡. `{{MODE}}` 치환 후엔 주석이 그대로 남아 메타 표가 너저분.
  - 제안: 주석을 셀 밖(테이블 위 또는 아래)으로 빼거나, 치환 단계에서 주석을 제거하는 처리 추가.

### 📝 다른 리뷰어 영역 (참고만)

- **architecture-reviewer**: `code-reviewer` 에이전트 스펙(L19–27)이 5개 카테고리(정확성/유지보수성/설계/성능/관용구)를 한 에이전트에 다 묶었다. "한 모자만 쓴다"는 자기 철학(L17)과 부분적으로 충돌 — `code-quality` vs `design-quality`로 다시 쪼갤지 검토 영역.
- **security-reviewer**: SKILL.md L235 `gh pr comment <PR> --body-file ${REPORT_PATH}`는 리포트에 포함될 수 있는 코드 스니펫에 *시크릿스러운 문자열*이 섞여 있을 때 외부 공개 위험. `--comment` 게이트 외에 본문 시크릿 스캔 단계가 빠져 있다.
- **side-effect-analyzer**: 본 PR에서 새 skill/agent가 추가됐는데, 다른 기존 스킬(`/commit`, `/push`, `tech-qna`)이 `/review-pr`을 자동 트리거하거나 의존하는지(예: `/push` 직전 자동 호출)는 본 스코프 밖이라 확인 안 함.
- **spec-reviewer**: SKILL.md가 "1주차.pdf p25–26"을 근거로 명시하는데, 실제 PDF 내용과의 일치 여부는 본 에이전트가 검증 불가.
- **test-reviewer**: 본 PR엔 테스트 파일이 없다 — 스킬/에이전트 정의 파일이라 자동화 테스트 적용이 미묘하지만, "각 SCOPE 분기에서 diff 수집이 실제로 동작하는지" 검증할 fixture 기반 골든 테스트는 v5에서 고려 가치 있음.

## v5 풀 스펙으로 가는 길 (메모)

MVP 리뷰는 `code-reviewer` 단독 결과만 포함합니다. 다음 리뷰어들이 미실행 상태입니다:

- [ ] security-reviewer (보안 취약점)
- [ ] test-reviewer (테스트 적정성)
- [ ] hygiene-reviewer (위생: 커밋 분할, scope creep)
- [ ] architecture-reviewer (조건부 — 구조 변경 시)
- [ ] spec-reviewer (조건부 — PRD 부합)
- [ ] side-effect-analyzer (조건부 — 외부 참조 영향)

위 영역 결함이 있을 수 있으니, *머지 전 사람 리뷰*는 여전히 필요합니다.

---

## MVP 스모크 테스트 회고 (이 리뷰가 발견한 메타-사항)

1. **첫 사이클에서 SKILL.md의 *local 모드 정의 갭* 발견** — `BASE...HEAD`만 봐서 uncommitted/untracked가 빠지는 문제. 패치 후 재실행해 본 리뷰가 가능했다.
2. **두 번째 사이클(이 리뷰)에서 더 깊은 일관성 문제 발견** — 3-dot vs 2-dot, 헤더 레벨 충돌, 멀티바이트 슬러그, BSD date 호환성 등.
3. **메타-검증**: code-reviewer가 *자기 자신의 정의 파일*까지 객관적으로 지적했다 (스코프 비대화, Glob 미사용 등). "한 모자만 쓴다" 원칙이 작동.
4. **노이즈 처리 갭**: `.omc/*` 상태 파일 9개를 메인 오케스트레이터가 *수동으로* 필터링했다. SKILL.md에 노이즈 필터 절차가 없어 MVP+1 후보로 등재.

다음 사이클 (MVP+1) 후보 우선순위:
- 🟠 HIGH 2건 패치
- 🟡 untracked 공백 파일명 / 슬러그 멀티바이트 / 노이즈 필터
- 🟢 LOW 4건은 MVP+2 이후

---

_생성: `/review-pr` MVP · 저장 위치: `docs/reviews/2026-05-28-mvp-smoke-test.md`_
