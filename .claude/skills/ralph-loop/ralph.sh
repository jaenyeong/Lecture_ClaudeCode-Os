#!/usr/bin/env bash
#
# ralph.sh — Headless 랄프 루프 (3주차.pdf p8·p17·p18)
#
# 원본(p8):  while :; do cat PROMPT.md | (에이전트); done
# 여기에 p18의 "좋은 종료 조건" = 증명 명령(VERIFY) + 턴 상한(MAX_TURNS) 을 더해
# "목표 달성하면 자동 종료 / 못 하면 N턴 후 중단" 하도록 안전화한 버전.
#
# 평소엔 SKILL.md의 서브 에이전트 방식을 쓰고, 이 스크립트는
# "며칠 동안 사람 없이 돌려야 할 때"(p17)만 쓴다.
#
# 사용법:
#   VERIFY="npm test" MAX_TURNS=20 ./ralph.sh
#   VERIFY="npm run e2e && [ $(측정) -lt 300 ]" MAX_TURNS=15 WORKDIR=./apps/web ./ralph.sh
#
set -uo pipefail

WORKDIR="${WORKDIR:-.}"
MAX_TURNS="${MAX_TURNS:-20}"
VERIFY="${VERIFY:?종료를 판정할 증명 명령(VERIFY)이 필요합니다 (p18: 증명 방법 없는 루프 금지)}"
RALPH_DIR="${WORKDIR}/.ralph"
PROMPT="${RALPH_DIR}/PROMPT.md"
LESSONS="${RALPH_DIR}/lessons.md"

cd "$WORKDIR" || { echo "workdir 없음: $WORKDIR"; exit 1; }
mkdir -p "$RALPH_DIR"
[ -f "$PROMPT" ]  || { echo "# 목표를 PROMPT.md에 먼저 정의하세요 (p9)"; exit 1; }
[ -f "$LESSONS" ] || echo "# Lessons (이터레이션 누적 기록)" > "$LESSONS"

command -v claude >/dev/null 2>&1 || { echo "claude CLI가 필요합니다"; exit 1; }

turn=0
while [ "$turn" -lt "$MAX_TURNS" ]; do
  turn=$((turn + 1))
  echo "🔁 turn ${turn}/${MAX_TURNS} …"

  # (A) 입력 조립: 고정 PROMPT + 누적 컨텍스트(lessons) — p9 흐름도 / p19 재주입
  #     매 호출이 새 프로세스 = 독립 컨텍스트 (p16)
  { cat "$PROMPT"; echo; echo "# 지금까지의 교훈"; cat "$LESSONS"; } \
    | claude -p --dangerously-skip-permissions \
        "위 PROMPT와 교훈을 읽고 목표를 향해 '한 걸음'만 전진하라. \
         배운 것은 .ralph/lessons.md 에 1~3줄 append 하라."

  # (B) 종료 판정: 증명 명령으로 — 주장이 아니라 증거 (p18)
  if eval "$VERIFY"; then
    echo "✅ ${turn}턴 만에 목표 달성 (VERIFY 통과)"
    exit 0
  fi
  echo "  …미충족 → 다음 턴 (이유는 lessons.md 참고)"
done

echo "⛔ ${MAX_TURNS}턴 상한 도달 — 사람이 .ralph/lessons.md 를 보고 개입하세요 (p18 상한)"
exit 1
