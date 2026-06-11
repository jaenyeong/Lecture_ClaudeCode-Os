#!/usr/bin/env python3
"""Stop hook — 자산 축적형 자율 개선 장치 (3주차.pdf p55 PRACTICE 2번 산출물).

시스템 루프의 비어 있던 ⑤ 기록 단계를 메운다(docs/system-loop.md 참조).
세션이 끝날 때 Claude를 한 번 더 깨워, "이번 세션에서 배운 것/반복된 마찰"을
docs/lessons.md 에 append 하도록 유도한다. 다음 세션은 그 파일을 읽어
같은 마찰을 0부터 다시 겪지 않는다.

동작:
- stop_hook_active 가 이미 true 면(= 이 hook이 한 번 깨운 뒤) 그대로 통과 → 무한 루프 방지.
- 아니면 decision=block + reason 으로 Claude에게 기록을 지시.
"""
import sys
import json
import os
import datetime


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # 입력 파싱 실패 시 조용히 통과 (세션을 막지 않는다)

    # 무한 루프 방지: 이미 한 번 깨운 세션이면 통과
    if data.get("stop_hook_active"):
        sys.exit(0)

    today = datetime.date.today().isoformat()
    reason = (
        "세션을 마치기 전 — 이번 세션에서 '배운 것'이나 '반복된 마찰(같은 실수·우회)'이 "
        "있었으면 docs/lessons.md 에 1~3줄 append 하라. "
        f"형식: '## {today}' 헤더 아래 '- <배운 것>'. "
        "정말 남길 게 없으면 한 줄로 그 사실만 보고하고 종료해도 된다. "
        "(자산 축적형 자율 개선 장치 · 3주차.pdf p55 2번 · 시스템 루프 ⑤ 기록 단계)"
    )
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
