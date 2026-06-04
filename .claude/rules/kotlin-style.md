---
name: kotlin-style
type: 전문성 컨텍스트 (test·ux·tech)
scope: Spring Kotlin 백엔드 (Gradle)
trigger: "*.kt 작성·리뷰 시" — 전역(CLAUDE.md)에 두지 않고 코드 작업/리뷰 컨텍스트에서만 주입
---

# Kotlin 코딩 지침 (Spring · Gradle)

> 회사 Spring Kotlin 실무에서 AI에게 **반복해서 설명하던 기술 기준**을 컨텍스트로 박제한 것.
> 컨텍스트 오염(Context Rot)을 피하려 전역이 아닌 *코드 작업·리뷰 시점에만* 로딩한다.

## 1. Request/Response DTO 위치 (강제)

`XxxRequest` / `XxxResponse` 같은 API DTO 는 **반드시 별도 파일**로 추출한다.

다음 패턴은 모두 **금지**:
- 서비스/도메인 클래스(예: `MypageService`)의 **inner class** 로 정의
- 같은 `.kt` 파일 끝에 **dangling `data class XxxRequest(...)`** (트레일링 클래스 패턴)
- **`companion object` 안에** 정의

표준 위치:
- Request: `controller/request/XxxRequest.kt`
- Response: `controller/response/XxxResponse.kt`

DTO 에 종속된 변환 함수(예: 레거시 HashMap 변환)는 **DTO 의 멤버 메서드**로 둔다.
서비스 내부의 `private fun XxxRequest.toLegacyDataMap()` 같은 service-side extension 패턴은 지양.

`ModelAndView.toXxxResponse()` 처럼 **외부 타입에 대한 확장**은 호출하는 서비스/어댑터 안에 `private` 으로 유지
(DTO 가 `ModelAndView` 같은 외부 타입을 알게 만들지 않는다).

기존 코드에 위 규칙 위반이 보이면 **새 작업 스코프 안에서 같이 추출·정리** — 단, 무관한 위치까지 sweep 하지 않는다.

## 2. 린트 (작업 완료 후 강제)

코드 변경 작업 완료 후 반드시:
1. `./gradlew ktlintFormat` — 자동 수정 먼저
2. `./gradlew ktlintCheck` — 린트 통과 확인
3. 자동 수정 불가 항목(예: max line length)은 **수동 수정 후 재확인**

## 3. 테스트 철학 (TDD)

- 새 기능·버그 수정은 **테스트부터** (RED → GREEN → REFACTOR)
- 버그 수정 시: "버그를 고치기 전에 Red 테스트를 먼저 만들고, 그 다음 고친다"
- 커버리지 80%+ 지향

## 4. 감사(audit) 파라미터 정책 (프로젝트 고유)

모든 `@Service` 의 **public 메서드 첫 번째 파라미터는 반드시 `actorId: Long`** 이어야 한다.
(누가 이 행위를 했는지 호출자 추적·감사 로깅을 강제하기 위함.)
`userId`, `memberId`, `id` 등 **다른 이름은 금지** — 발견 시 🟠 HIGH 로 지적하고 `actorId` 로 변경 제안.

> 이 규칙은 이 프로젝트에만 있는 컨벤션이다. (A/B 검증 시, 이 룰이 주입돼야만 잡히는 신호로 사용)

## 5. 리뷰어가 이 파일을 볼 때

`code-reviewer` 가 `.kt` diff 를 리뷰할 때 위 규칙을 **명시 기준**으로 대조한다.
특히 **DTO 위치 위반**은 🟡 MEDIUM 이상으로 지적하고, 표준 위치를 제안한다.
