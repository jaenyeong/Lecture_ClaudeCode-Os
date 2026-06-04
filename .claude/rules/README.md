# .claude/rules — 내 OS 컨텍스트 체계

> 2주차 실습 "내 OS 컨텍스트 체계 설계" 산출물.
> 회사 Spring Kotlin 백엔드 실무에서 **AI에게 반복 설명하던 규칙**을 컨텍스트로 박제하고,
> 분류마다 **다른 곳에 주입**해 컨텍스트 오염(Context Rot)을 피한다.

## 설계 원칙

> "정말 *모든* 상황에서 필요한가?" 를 통과한 것만 전역에 둔다. 나머지는 필요할 때만.

## 컨텍스트 3분류 → 주입 방식 매핑

| 분류 | 파일 | 주입 방식 | 트리거 |
|---|---|---|---|
| **전문성** (tech) | `kotlin-style.md` | 리뷰 에이전트에 **참조 주입** + `*.kt` 작업 시 | 코드 작성·리뷰 |
| **팀** (dev/qa) | `team-conventions.md` | 핵심만 추려 **CLAUDE.md 전역 승격** 후보 | 커밋·PR·푸시 |
| **도메인** (payment 등) | `<domain>.md` *(미작성)* | 디렉토리 경로 매칭 / 스킬 참조 | 해당 도메인 작업 |
| **비즈니스/방향** | `vision.md` *(미작성)* | 별도 md + **Lazy**("필요하면 읽어라") | 가끔 |

## 현재 주입 상태

- `kotlin-style.md` → `.claude/agents/code-reviewer.md` 의 "프로젝트 컨벤션 대조" 단계에서 참조
- `team-conventions.md` → (아직 전역 미승격, 참조 대기)

## 검증 (A/B 테스트)

`docs/samples/MypageService.kt` 에 **DTO 위치 위반**(서비스 inner class DTO)을 심어 둠. (rules 디렉토리 *바깥* + 누설 주석 없음 → 변수 격리)

- **A (컨텍스트 無)**: 참조 주입 제거 후 리뷰 → 위반 못 잡거나 약하게
- **B (컨텍스트 有)**: `kotlin-style.md` 참조 상태로 리뷰 → DTO 위치 위반을 명시 규칙으로 지적

차이가 나면 "주입한 컨텍스트가 실제로 활용됨"이 증명된다.

## 다음 단계 (확장 여지)

1. 실제 도메인 1개를 골라 `<domain>.md` 작성 → 경로 매칭 주입
2. `team-conventions.md` 핵심을 CLAUDE.md 전역으로 슬림 승격
3. pre-hook(`additionalContext`)로 경로 기반 자동 주입 실험 (PDF 14p)
