# Lessons (이터레이션 누적 기록)
<!-- 매 턴: 무엇을 등재했고 / 무엇을 배웠고 / 다음 턴이 알아야 할 것 -->

## turn 1
- 등재: ralph-loop (README 03절 "현재 주입 상태" 문장에 L2 항목으로 추가)
- 배운 것: ralph-loop 은 반복 실행 오케스트레이터라 L1/L3 이 아니라 L2(파이프라인)에 넣는 게 맞다. 현황 문장은 L1·L3만 있었어서 L2 절을 새로 끼움.
- 다음 턴: update-doctor (남은 누락 1개) — CLI/모델 자동 갱신 복구 스킬이라 L1 atomic 으로 등재 검토

## turn 2
- 등재: update-doctor (README 03절 "현재 주입 상태" 문장의 L1 목록에 `/update-doctor` 추가)
- 배운 것: turn 1 힌트대로 L1 atomic 으로 등재. update-doctor 는 CLI/모델 자동 갱신 오작동 진단·복구라 단일 책임 atomic skill 성격이 맞음. 기존 L1 나열(`/commit` `/push` `/tech-qna` `/skill-stat`) 끝에 한 항목만 append.
- 다음 턴: 없음 — 목표 달성 예상. 검증 `for s in $(ls .claude/skills/); do grep -q "$s" README.md || echo MISSING; done` 결과 누락 0개 확인됨.
