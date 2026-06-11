# 목표
README.md의 스킬 목록을 .claude/skills/ 의 실제 스킬과 일치시킨다.
현재 README.md 에 누락된 스킬을 README 의 적절한 위치(스킬 현황 문장/표)에 등재한다.

# 종료 조건 (이게 충족되면 끝)
- 증명(verify): .claude/skills/ 의 모든 디렉토리명이 README.md 안에 존재 (누락 0개)
- 제약: 기존 README 표 구조·형식·문체를 유지한다. 무관한 줄은 건드리지 않는다.
- 상한: 최대 5턴. 넘으면 중단하고 사람에게 보고.

# 작업 규칙
- 한 턴에 "한 걸음"만 전진한다 (누락 스킬을 하나 또는 한 묶음 등재).
- 끝났다고 주장하지 말고, 등재한 스킬명을 명시해 증명한다.
- 진행/교훈은 반드시 .ralph/lessons.md 에 1~3줄 append 한다 (네 기억을 믿지 마라).
- 누락 스킬 확인 방법:
  for s in $(ls .claude/skills/); do grep -q "$s" README.md || echo "MISSING: $s"; done
