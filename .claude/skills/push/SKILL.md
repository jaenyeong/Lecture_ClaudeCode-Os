---
name: push
description: 현재 브랜치를 GitHub 리모트(origin)에 push. "푸시해줘", "/push" 등으로 호출되면 무엇이 올라갈지 미리 보여주고 계정·리모트 정책을 확인한 뒤 안전하게 push 한다.
---

# /push

현재 브랜치를 GitHub 리모트 저장소(origin)에 push 한다.
`/commit` 과 짝을 이루는 스킬 — 커밋은 만들지 않고 **이미 만들어진 커밋을 올리는 것**에만 집중한다.

## 1) 현재 상태 확인

다음을 병렬로 실행해서 어떤 상황인지 파악한다.

```bash
git status                          # working tree 상태
git branch --show-current           # 현재 브랜치 이름
git rev-parse --abbrev-ref @{u} 2>/dev/null || echo "NO_UPSTREAM"   # upstream 존재 여부
git remote -v                       # 리모트 URL 확인
```

- **detached HEAD** 상태면 사용자에게 알리고 중단한다 (브랜치 위에서만 push).
- **uncommitted 변경**이 남아있으면 경고하되 자동 커밋하지 않는다 — `/commit` 사용을 안내한다.

## 2) 계정·리모트 정책 점검

CLAUDE.md 정책에 따라 활성 계정과 origin URL을 확인한다.

```bash
gh api user --jq '.login'             # → jaenyeong 이어야 함
git config --local user.email         # → 22907395+jaenyeong@users.noreply.github.com
git remote get-url origin             # → https://github.com/jaenyeong/Lecture_ClaudeCode-Os(.git)
```

다르면 사용자에게 알리고 멈춘다. (자동 스위칭 금지 — 다른 저장소에서 작업 중일 수 있다.)

## 3) Push 미리보기 (필수)

무엇이 올라가는지 사용자에게 보여준다. upstream 유무에 따라 비교 대상이 달라진다.

### upstream 이 있는 경우 (`@{u}` 비교)

```bash
# 푸시될 커밋 목록
git log @{u}..HEAD --oneline

# 변경된 파일 요약 (insertions/deletions 포함)
git diff --stat @{u}..HEAD

# (옵션) 자세히 보고 싶으면
git diff --name-status @{u}..HEAD
```

### upstream 이 없는 신규 브랜치인 경우 (`origin/main` 비교)

```bash
git log origin/main..HEAD --oneline
git diff --stat origin/main..HEAD
```

올라갈 게 없으면 (`Already up-to-date`) 사용자에게 알리고 종료한다. (빈 push 시도 X)

미리보기 출력은 다음 포맷으로 사용자에게 정리해서 보여준다:

```
📤 Push 미리보기
   브랜치: <local> → origin/<remote>  (upstream: 있음/없음)
   커밋 N개:
     - <hash> <subject>
     - ...
   파일 변경: <N files>, +<ins>/-<del>
     - <path>  | +x -y
     - ...
```

## 4) 가드 체크

푸시 직전, 다음 항목을 확인하고 위험 신호가 있으면 사용자 확인을 받는다.

- **main 브랜치 직접 push** — 현재 브랜치가 `main`이면 한 번 더 확인. (강의 리포라 막진 않되 의식적으로 진행하도록.)
- **force push 금지(기본)** — 사용자가 명시적으로 요청하지 않으면 `--force` / `--force-with-lease` 안 쓴다.
- **태그/대용량 파일** — `git log @{u}..HEAD --stat` 로 비정상적으로 큰 변경(수천 줄 단일 커밋, 바이너리 dump 등)이 있으면 짚어준다.
- **비밀 파일 의심 패턴** — 변경 파일 목록에 `.env`, `*.pem`, `*credentials*`, `*secret*` 같은 이름이 보이면 경고하고 사용자 컨펌 받는다.

## 5) Push 실행

upstream 유무에 따라 명령이 다르다.

```bash
# upstream 있음
git push

# upstream 없음 (신규 브랜치)
git push -u origin <current-branch>
```

커밋 메시지나 hook 통과 여부와 무관하게, `git push` 자체가 실패하면 출력 메시지를 사용자에게 그대로 전달하고 원인 분석을 돕는다 (예: non-fast-forward, protected branch, permission denied 등). `--force`로 우회하지 않는다.

## 6) 푸시 후 검증

CLAUDE.md 정책: 원격 최신 커밋 author email 이 정책 이메일과 일치하는지 확인.

```bash
gh api repos/jaenyeong/Lecture_ClaudeCode-Os/commits --jq '.[0].commit.author.email'
# → 22907395+jaenyeong@users.noreply.github.com
```

다르면 사용자에게 즉시 알린다 (회사 계정 등 다른 자격증명으로 푸시되었을 가능성).

## 7) 결과 보고 & 다음 단계

사용자에게 짧게 요약:
- ✅ Push 완료: `<local-branch>` → `origin/<remote-branch>` (커밋 N개)
- 원격 author 검증 결과
- **다음 단계 제안**:
  - 신규 브랜치 + PR 없음 → `gh pr create` 안내 또는 "`PR 올려줘`" 단축 명령 제안
  - 이미 PR 있음 → PR URL 표시 (`gh pr view --json url --jq .url`)
  - `main` 브랜치 push → PR 단계 생략

## 주의

- **이 스킬은 push 만 책임진다.** 커밋이 필요하면 `/commit` 으로 먼저 처리한다.
- **`--force`, `--force-with-lease`, branch 삭제 등 파괴적 명령은 기본 금지.** 사용자 명시 요청이 있을 때만, 그것도 `main` 에는 절대 force push 안 한다.
- 신규 브랜치 push 시 `-u` 플래그를 빠뜨리지 않는다 (다음부터 `git push` 만으로 동작하도록).
- 푸시 실패 시 우회하지 말고 원인(권한, 보호 규칙, non-fast-forward 등)을 짚어 사용자에게 보고한다.
