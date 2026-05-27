# CLAUDE.md

이 파일은 이 저장소에서 Claude Code(claude.ai/code)가 작업할 때 따라야 할 규칙을 정의합니다.

## 프로젝트 컨텍스트

NEXTSTEP "나만의 클로드 OS 만들기" 강의 실습 저장소입니다.

## 규칙

1. **파일 위치**: 클로드 OS 관련 모든 파일(예: `.claude/` 하위 md 파일 등)은 반드시 이 프로젝트 디렉터리 안에 생성한다. 사용자 글로벌(`~/.claude/`)이 아닌 프로젝트 로컬에 두어 강의 진행 내용이 저장소에 함께 보존되도록 한다.

2. **친절한 설명**: 클로드 OS 만들기 실습 과정이므로, 단순히 결과만 내놓지 말고 대화 과정을 통해 AI와의 협업 방식을 배울 수 있도록 **무엇을·왜·어떻게** 하는지 친절하게 풀어서 설명한다. 명령어/도구 선택 이유, 다음 단계 제안 등을 함께 안내한다.

3. **커밋 컨벤션**: AngularJS 진영의 Conventional Commits 형식을 따른다.

   ```
   <type>(<scope>): <Subject>

   <optional body>
   ```

   - **type**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`
   - **scope**: 변경된 파일/디렉터리 경로 또는 컴포넌트명 (예: `README.md`, `CLAUDE.md`, `.claude/agents`)
   - **Subject**: 영문, 첫 글자 대문자, 명령형 현재 시제, 마침표 없음
   - **body(선택)**: 변경 이유·맥락. 필요 시 bullet 사용

   참고: 사용자의 다른 강의 리포지터리 커밋 히스토리를 컨벤션 레퍼런스로 사용한다.
   - [jaenyeong/Lecture_Unity-game](https://github.com/jaenyeong/Lecture_Unity-game)
   - [jaenyeong/Lecture_Docker-K8S](https://github.com/jaenyeong/Lecture_Docker-K8S)

   예시:
   - `docs(README.md): Add initial lecture README`
   - `docs(CLAUDE.md): Add commit convention guideline`
   - `feat(.claude/agents): Add code-reviewer agent`

4. **계정 정책 (GitHub / Git)**: 이 저장소의 모든 커밋·푸시는 반드시 아래 개인 계정으로 수행한다.

   - **GitHub 계정**: `jaenyeong`
   - **Git author**: `jaenyeong <22907395+jaenyeong@users.noreply.github.com>`
   - **리모트 origin**: `https://github.com/jaenyeong/Lecture_ClaudeCode-Os`

   다른 계정(예: 회사 계정 등)으로 커밋/푸시되지 않도록, 작업 전 아래를 점검하고 다르면 **반드시 스위칭한 뒤** 진행한다.

   ```bash
   # 1) 현재 활성 계정 확인
   gh api user --jq '.login'                              # → jaenyeong 이어야 함
   git config --local user.email                          # → 22907395+jaenyeong@users.noreply.github.com

   # 2) 다르면 스위칭
   gh auth switch -h github.com -u jaenyeong              # gh 활성 계정 전환
   git config --local user.name  "jaenyeong"
   git config --local user.email "22907395+jaenyeong@users.noreply.github.com"

   # 3) Keychain의 다른 계정 토큰을 우회하기 위해 이 저장소만 gh 자격증명 사용
   git config --local --replace-all credential.https://github.com.helper ""
   git config --local --add        credential.https://github.com.helper "!gh auth git-credential"
   ```

   푸시 후에는 원격 커밋의 author 이메일이 `22907395+jaenyeong@users.noreply.github.com` 인지 확인한다.

   ```bash
   gh api repos/jaenyeong/Lecture_ClaudeCode-Os/commits --jq '.[0].commit.author.email'
   ```
