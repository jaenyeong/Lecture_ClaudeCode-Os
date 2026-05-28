# 나만의 클로드 OS 만들기

[NEXTSTEP 강의 링크](https://edu.nextstep.camp/c/anUjcv0e/)

Claude Code를 기반으로 본인만의 개발 환경(OS)을 구축하는 과정을 학습하며 정리하는 저장소.

## [Settings]
* macOS (Darwin 25.5.0)
* Shell: zsh
* Claude Code (Opus 4.7)

## 나만의 OS 설계 (Day 1)

> 1주차 22p 실습 — 규모보다 **효능감(작업 시간 ↓ · 귀찮음 ↓ · 더 잘하기)** 을 우선한다.

### 01. 내 업무의 중심 워크플로우

내 업무는 **코드 작성/리뷰/PR · 설계/문서화 · 디버깅 · 학습/리서치** 네 영역에 걸쳐
있어서, 단일 워크플로우가 아니라 **4-Layer 구조**로 잡는다.

| Layer | 역할 | 예시 |
|---|---|---|
| **L0. Context Assets** | 작업의 입력 자료 (SSOT) | `CLAUDE.md`, `docs/adr/*`, `docs/prd/*`, `docs/contracts/*`, 강의 자료 |
| **L1. Atomic Skills** | 한 가지만 하는 명령 (Unix 명령처럼) | `/commit`, `/push`, `/lint-*`, `/build-*`, `/test-*` |
| **L2. Pipeline Skills** | L1을 엮은 작업 타입별 워크플로우 | `/start-task`, `/refactor-safely`, `/review-pr`, `/debug-loop`, `/tech-qna` |
| **L3. Agents** | 자율 판단·검증·인터뷰 | `triage`, `interviewer`, `fact-checker`, `side-effect-analyzer` |

> **규약 (L1)**: 모든 atomic skill의 `SKILL.md` `description` 필드에는 자연어 트리거 키워드(예: `"커밋해줘"`, `"푸시해줘"`)를 따옴표로 박아둔다. 슬래시 명령 없이 자연어 입력만으로도 Claude가 자동 매칭하도록 하기 위함이다.

작업 타입은 매번 내가 지정하지 않는다. **L3 `triage` agent가 입력 + 저장소 상태로 자동
분류**해서 적절한 L2 pipeline에 위임한다.

| 작업 타입 | 판별 신호 | 호출 Pipeline |
|---|---|---|
| 신규 구현 | "구현/추가" + 깨끗한 git | `/start-task` |
| 리팩터링 | "리팩터링/정리" + 기존 파일 수정 | `/refactor-safely` |
| PR 리뷰 | PR URL, `gh pr view` | `/review-pr` |
| 디버깅 | 스택트레이스, "안 됨" | `/debug-loop` |
| 학습/QnA | "왜/차이/뭐야" | `/tech-qna` |
| 문서 작업 | "ADR/PRD/README" | `/doc-write` |

subtype(예: 신규 구현 → API/UI/마이그레이션)은 처음엔 적지 않고, 회고(`/skill-stat`)로
자주 마주치는 케이스부터 가지를 친다. 메타 속성(변경 범위·영향 범위·위험도·가역성)은
pipeline 진입 직후 추가 추론해 검증 강도를 조절한다.

작업 시작 전, L2 pipeline은 **컨텍스트 충분성**을 점검한다. PRD/ADR/산출물 명세가 없으면
`interviewer` agent가 질문으로 채우고, 결과를 다시 L0에 영구화한다.

### 02. 핵심 철학 / 관점

1. **Unix Pipeline** — 큰 만능 명령보다 작은 skill 여러 개의 조합.
2. **Red Test First** — 답·코드보다 "검증할 것"을 먼저 정의. 모든 산출물에 검증 장치가
   따라붙는다 (`/tech-qna + fact-checker`처럼).
3. **SSOT (Single Source of Truth)** — 의사결정·요구사항·산출물 명세는 한 곳(L0)에 모은다.
4. **없으면 묻는다** — 필요한 컨텍스트가 비어있으면 자동 진행하지 않고 인터뷰로 보완한 뒤
   결과를 L0에 영구화한다.
5. **굵게 시작해서 가지치기** — 작업 타입·subtype은 최소한으로 시작, 회고 데이터로 자라게
   한다. (= 죽은 문서 만들지 않기)

### 03. OS가 일을 잘 하려면 필요한 컨텍스트 (L0)

| 자산 | 위치 | 역할 |
|---|---|---|
| 프로젝트 규칙 | `CLAUDE.md` | 커밋 컨벤션, 계정 정책, 톤 |
| 강의 자료 | `1주차.pdf` 등 | `/tech-qna`의 우선 근거 |
| 아키텍처 결정 | `docs/adr/*.md` | 왜 그렇게 설계했는지 — 신규 구현·리팩터링의 근거 |
| 제품 요구사항 | `docs/prd/*.md` | 무엇을·왜 만드는지 |
| 산출물 명세 | `docs/contracts/*.md` | 결과물의 데이터 타입·포맷·방향 |
| 작업 타입 분기 규칙 | `docs/os/triage-rules.md` | `triage` agent가 참조하는 분류 기준 |
| 코드 컨벤션·테스트 정책 | 글로벌 룰 + 프로젝트별 보완 | 자동 검증(`/lint-*`, `/test-*`)의 기준 |

> 현재는 L0의 `CLAUDE.md`와 강의 자료만 채워져 있고, L1에는 `/commit` `/push`
> `/tech-qna` `/skill-stat`, L3에는 `fact-checker` 가 있다. 나머지는 실습을 진행하며
> 점진적으로 채운다.

## 학습 내용
* (작성 예정)
