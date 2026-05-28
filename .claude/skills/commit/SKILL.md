---
name: commit
description: 로컬 변경사항을 Git에 커밋. "커밋해줘", "/commit" 등으로 호출되면 변경사항을 확인하고 이 프로젝트의 Conventional Commits 컨벤션으로 커밋한다.
---

# /commit

로컬 변경사항을 분석해서 이 프로젝트의 컨벤션에 맞게 커밋한다.

## 1) 변경사항 확인

다음을 병렬로 실행해서 무엇이 어떻게 바뀌었는지 파악한다.

```bash
git status              # 어떤 파일이 바뀌었는지
git diff                # unstaged 변경사항
git diff --staged       # staged 변경사항
git log -n 5 --oneline  # 최근 커밋 스타일 참고
```

변경사항이 전혀 없으면 사용자에게 알리고 종료한다. (빈 커밋은 만들지 않는다.)

## 2) 계정 점검 (이 저장소 전용)

CLAUDE.md 계정 정책에 따라 커밋 전에 활성 계정을 확인한다.

```bash
gh api user --jq '.login'         # → jaenyeong 이어야 함
git config --local user.email     # → 22907395+jaenyeong@users.noreply.github.com
```

다르면 사용자에게 알리고 진행을 멈춘다. (자동으로 스위칭하지 않는다 — 다른 저장소 작업 중일 수 있으므로 사용자 확인을 받는다.)

## 3) 커밋 메시지 작성

이 프로젝트는 **Conventional Commits** 형식을 따른다.

```
<type>(<scope>): <Subject>

<optional body>
```

- **type**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`
- **scope**: 바뀐 파일/디렉터리 경로나 컴포넌트명 (예: `README.md`, `CLAUDE.md`, `.claude/skills/commit`)
- **Subject**: 영문, 첫 글자 대문자, 명령형 현재 시제, 마침표 없음
- **body** (선택): 변경 이유·맥락. 필요할 때만, bullet 가능

예시:
- `docs(README.md): Add initial lecture README`
- `feat(.claude/skills/commit): Add commit skill`
- `fix(.claude/agents): Handle empty diff case`

여러 종류 변경이 섞여 있으면 **하나의 type으로 합치지 말고** 분리 커밋을 사용자에게 제안한다.

## 4) 스테이징 & 커밋

추적할 파일만 명시적으로 지정해서 스테이징한다. `git add -A` / `git add .`은 쓰지 않는다 — `.env`나 비밀이 휩쓸려 들어갈 수 있다.

```bash
git add <구체적 파일들>
git commit -m "$(cat <<'EOF'
<type>(<scope>): <Subject>

<optional body>
EOF
)"
```

커밋 메시지는 항상 HEREDOC으로 전달한다 (멀티라인·따옴표 안전).

## 5) 결과 보고

`git status`로 결과를 확인하고 사용자에게:
- 커밋 해시 (앞 7자리)
- 적용한 type/scope/subject
- push가 필요하면 다음 단계 안내 ("`git push -u origin <branch>` 또는 `올려줘`")

를 짧게 알려준다.

## 주의

- **요청받지 않으면 push 하지 않는다.** 커밋까지만이 이 스킬의 책임이다.
- 빌드/테스트 hook이 실패하면 `--no-verify`로 우회하지 말고 원인을 찾아 고친 뒤 **새 커밋**을 만든다 (amend 금지 — 사용자 명시 요청 없을 시).
- 컨벤션 위반(예: 한글 Subject, 마침표, 평서문)을 발견하면 사용자에게 짚어주고 수정 제안한다.
