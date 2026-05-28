# Code Review Report

> 자동 생성 — `/review-pr` 오케스트레이터 (MVP)

## 메타

| 항목 | 값 |
|---|---|
| 생성 시각 | {{TIMESTAMP}} |
| 모드 | {{MODE}}  <!-- pr | local --> |
| 입력 | {{INPUT_REF}}  <!-- PR URL/번호 또는 로컬 브랜치 비교 범위 --> |
| 베이스 | {{BASE_REF}} |
| 헤드 | {{HEAD_REF}} |
| 변경 파일 수 | {{FILES_CHANGED}} |
| 변경 라인 수 | +{{LINES_ADDED}} / -{{LINES_REMOVED}} |
| 호출된 리뷰어 | {{REVIEWERS}}  <!-- MVP: code-reviewer 단독 --> |

## 요약

🔴 BLOCKER: {{COUNT_BLOCKER}} · 🟠 HIGH: {{COUNT_HIGH}} · 🟡 MEDIUM: {{COUNT_MEDIUM}} · 🟢 LOW: {{COUNT_LOW}}

**다음 권고 액션**: {{NEXT_ACTION}}
<!--
- BLOCKER ≥ 1 → "BLOCKER 해결 후 재리뷰 권장"
- HIGH ≥ 1, BLOCKER = 0 → "HIGH 검토 후 머지 결정"
- 그 외 → "머지 가능, MEDIUM/LOW는 후속 PR로 처리 가능"
-->

## 변경 파일 목록

{{FILES_LIST}}
<!--
- src/foo.kt (+12 / -3)
- src/bar.kt (+5 / -1)
-->

## 리뷰 결과

### code-reviewer

{{CODE_REVIEWER_OUTPUT}}
<!--
code-reviewer 에이전트가 돌려준 markdown 본문 전체를 그대로 삽입.
형식 예시:

요약: 🔴 1 / 🟠 2 / 🟡 3 / 🟢 1

#### 🔴 BLOCKER
- **src/foo.kt:42** retry 로직이 무한 루프 가능
  - 문제: 종료 조건이 `attempts > max`인데 `attempts`가 증가하지 않음
  - 제안: 루프 마지막에 `attempts++` 추가

#### 🟠 HIGH
- ...

#### 📝 다른 리뷰어 영역 (참고만)
- security-reviewer: `userInput`이 SQL에 직접 들어가는 패턴 발견 (v5에서 자동 검증 예정)
-->

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

_생성: `/review-pr` MVP · 저장 위치: `docs/reviews/{{DATE}}-{{SLUG}}.md`_
