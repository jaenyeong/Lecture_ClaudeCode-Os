---
name: skill-stat
description: 누적된 스킬 호출 통계(호출 횟수, 평균/총 소요 시간, 최근 호출 시각)를 표로 보여준다. "/skill-stat", "스킬 통계 보여줘", "어떤 스킬을 많이 썼는지" 같은 트리거에 반응한다.
---

# skill-stat

PreToolUse / PostToolUse / UserPromptSubmit 훅이 `.claude/logs/skill-stats.jsonl`
에 쌓아 둔 스킬 호출 로그를 집계해서 CLI 표로 출력하는 스킬이다.

## 호출 트리거

- 슬래시 명령: `/skill-stat`
- 자연어: "스킬 통계 보여줘", "어떤 스킬을 얼마나 썼는지 정리해줘",
  "skill 통계", "내가 자주 쓴 스킬"

## 동작 절차

1. **Bash 도구로 집계 스크립트를 실행한다.**
   ```
   python3 .claude/skills/skill-stat/stat.py
   ```
2. 표 출력을 그대로 사용자에게 보여준다. 추가 가공 없이 raw output 우선.
3. 출력에 "(아직 기록된 스킬 호출이 없습니다.)" 가 보이면, 사용자에게
   "스킬을 한두 번 더 호출한 뒤 다시 와 달라"고 안내한다.

## 표 컬럼 의미

| 컬럼 | 설명 |
|---|---|
| `SKILL` | 스킬 이름 |
| `COUNT` | 호출 횟수 (사용자 입력 + 어시스턴트 호출 합산) |
| `AVG(ms)` | 평균 소요 시간 — duration 이 측정된 호출만 평균 |
| `TOTAL(ms)` | 총 소요 시간 — duration 이 측정된 호출 합 |
| `LAST USED` | 가장 최근 호출 시각 (UTC, ISO8601) |

`AVG/TOTAL` 가 `—` 인 경우는 해당 스킬이 사용자 입력(`/<skill-name>`)으로만
호출돼서 duration 을 측정할 수 없었다는 뜻이다 (아래 "기록 경로" 참고).
정렬은 `COUNT` 내림차순 — 가장 많이 쓴 스킬이 맨 위.

## 데이터 소스

- 로그: `.claude/logs/skill-stats.jsonl`
- 한 줄 = 한 번의 스킬 호출
- 스키마:
  ```json
  {
    "ts": "2026-05-28T20:30:00Z",
    "skill": "tech-qna",
    "duration_ms": 1234,
    "session_id": "...",
    "source": "skill_tool" | "user_prompt"
  }
  ```

## 기록 경로 두 가지

스킬은 두 가지 방식으로 호출되며, 훅도 두 경로로 기록한다.

| 경로 | 트리거 | 훅 이벤트 | duration_ms | source |
|---|---|---|---|---|
| **Skill tool 호출** | 어시스턴트가 `Skill` 도구를 자율적으로 부름 | `PreToolUse` + `PostToolUse` (matcher=`Skill`) | 측정됨 (ms) | `skill_tool` |
| **사용자 슬래시 입력** | 사용자가 입력창에 `/<name>` 입력 | `UserPromptSubmit` | `null` (측정 불가) | `user_prompt` |

`UserPromptSubmit` 경로는 `.claude/skills/<name>/SKILL.md` 가 실제로 존재할
때만 기록한다 — `/help`, `/clear` 같은 built-in 슬래시 커맨드와 플러그인
네임스페이스(예: `/oh-my-claudecode:ralph`)는 통계 대상에서 제외된다.

훅 등록 위치: `.claude/settings.json`
실제 로직: `.claude/hooks/skill_stat.py`

## 관리 팁

- 통계를 초기화하고 싶으면 `.claude/logs/skill-stats.jsonl` 을 비우면 된다.
  (`: > .claude/logs/skill-stats.jsonl`)
- pending 매칭이 꼬였다 싶으면 `.claude/logs/.skill_stat_pending.json` 도
  같이 비운다.
- 로그 파일은 개인 사용량을 담고 있으므로 git 에는 올리지 않는다
  (`.gitignore` 로 제외됨).
