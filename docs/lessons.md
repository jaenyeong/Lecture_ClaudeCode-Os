# Lessons — OS 학습 로그 (자산 축적형 자율 개선 장치)

> 3주차.pdf p55 PRACTICE 2번 산출물. 시스템 루프의 ⑤ "기록" 단계(`docs/system-loop.md`).
> 세션 종료 시 Stop hook(`.claude/hooks/session_lessons.py`)이 여기에 교훈을 쌓도록 유도한다.
> **다음 세션은 이 파일을 먼저 읽어** 같은 마찰을 0부터 다시 겪지 않는다.

## 2026-06-11
- `git`이 zsh의 scm_breeze 래퍼에 깨지면 `command git`으로 우회한다. (커밋이 조용히 실패했었음)
- 이 저장소 작업 전 `gh` 활성 계정이 `jaenyeong`인지 확인하고, 다르면 `gh auth switch -h github.com -u jaenyeong`. (기본이 `jaenyeong-kim`이라 매번 어긋남)
- 서브에이전트는 결과를 짧게만 반환하므로, 완료 판정은 주장이 아니라 메인이 `verify` 명령으로 측정한다.
- `Edit` 도구는 `cat`으로 본 것과 무관하게 **`Read` 도구로 파일을 먼저 읽어야** 동작한다. (settings.json 수정 시 한 번 막혔음)
- Stop hook 같은 자율 개선 장치는 `stop_hook_active`로 무한 루프를 반드시 막아야 한다. (안 그러면 세션이 안 끝남)
- Stop hook은 '세션 종료'가 아니라 **매 어시스턴트 응답 종료마다** 발동한다 → 매 턴 뜨면 과하다. 트리거를 좁혀야 함(예: `lessons.md`에 오늘 날짜 섹션이 이미 있으면 통과 → 하루 1회).
