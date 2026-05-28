---
name: skill-stat
description: 누적된 스킬 호출 통계(호출 횟수, 평균/총 소요 시간, 최근 호출 시각)를 표로 보여준다. "/skill-stat", "스킬 통계 보여줘", "어떤 스킬을 많이 썼는지" 같은 트리거에 반응한다.
---

# skill-stat

PreToolUse / PostToolUse 훅이 `.claude/logs/skill-stats.jsonl` 에 쌓아 둔
스킬 호출 로그를 집계해서 CLI 표로 출력하는 스킬이다.

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
| `SKILL` | 스킬 이름 (`tool_input.skill` 값 그대로) |
| `COUNT` | 호출 횟수 |
| `AVG(ms)` | 평균 소요 시간 (PreToolUse → PostToolUse 사이 경과) |
| `TOTAL(ms)` | 총 소요 시간 |
| `LAST USED` | 가장 최근 호출 시각 (UTC, ISO8601) |

정렬은 `COUNT` 내림차순 — 가장 많이 쓴 스킬이 맨 위.

## 데이터 소스

- 로그: `.claude/logs/skill-stats.jsonl`
- 한 줄 = 한 번의 스킬 호출
- 스키마:
  ```json
  {"ts": "2026-05-28T20:30:00Z", "skill": "tech-qna", "duration_ms": 1234, "session_id": "..."}
  ```

훅 자체는 `.claude/settings.json` 의 PreToolUse / PostToolUse 에
`matcher: "Skill"` 로 걸려 있고, 실제 기록 로직은
`.claude/hooks/skill_stat.py` 에 있다.

## 관리 팁

- 통계를 초기화하고 싶으면 `.claude/logs/skill-stats.jsonl` 을 비우면 된다.
  (`: > .claude/logs/skill-stats.jsonl`)
- pending 매칭이 꼬였다 싶으면 `.claude/logs/.skill_stat_pending.json` 도
  같이 비운다.
- 로그 파일은 개인 사용량을 담고 있으므로 git 에는 올리지 않는다
  (`.gitignore` 로 제외됨).
