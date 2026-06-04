---
name: team-conventions
type: 팀 컨텍스트 (biz·dev·qa)
scope: 협업 규칙 — 커밋·PR·계정 정책
trigger: "커밋·PR·푸시 작업 시" — 항상 필요한 핵심만 추리면 CLAUDE.md 전역 승격 후보
---

# 팀 협업 컨벤션

> "우리가 일하는 방식". 커밋·PR·계정 정책처럼 **세션과 무관하게 유지**되는 규칙.
> 핵심(항상 필요한 것)은 추후 CLAUDE.md 전역으로 승격하고, 나머지는 여기 둔다.

## 1. 커밋 컨벤션 (Conventional Commits)

```
<type>(<scope>): <Subject>

<optional body>
```

- **type**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`
- **scope**: 변경된 파일/디렉터리 경로 또는 컴포넌트명 (예: `README.md`, `.claude/agents`)
- **Subject**: 영문, 첫 글자 대문자, 명령형 현재 시제, 마침표 없음
- **body(선택)**: 변경 이유·맥락. 필요 시 bullet

예시:
- `docs(README.md): Add initial lecture README`
- `feat(.claude/agents): Add code-reviewer agent`

## 2. PR 규칙

1. 최신 커밋만이 아니라 **전체 커밋 히스토리** 분석
2. `git diff <base>...HEAD` 로 전체 변경 확인
3. 포괄적 PR 요약 + 테스트 플랜(TODO 포함)
4. 새 브랜치는 `-u` 플래그로 푸시

## 3. 계정 정책 (이 저장소)

- GitHub 계정: `jaenyeong`
- Git author: `jaenyeong <22907395+jaenyeong@users.noreply.github.com>`
- remote origin: `https://github.com/jaenyeong/Lecture_ClaudeCode-Os`

작업 전 활성 계정 확인, 다르면 스위칭 후 진행. (다른 계정으로 커밋/푸시 금지)

## 4. 리뷰어가 이 파일을 볼 때

`code-reviewer` 는 코드 *내적 품질*만 본다 — 커밋 메시지·PR 형식은 스코프 밖.
다만 변경이 위 컨벤션과 충돌하는 흔적(예: 잘못된 author 설정 파일)이 보이면 "📝 다른 영역" 노트로만 남긴다.
