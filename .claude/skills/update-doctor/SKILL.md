---
name: update-doctor
description: Claude Code CLI 와 Opus 모델의 "자동 갱신"이 오작동했을 때 돌리는 진단·복구 스킬. "업데이트 안 돼", "자동 업데이트 고쳐줘", "cli 최신으로", "최신 모델로 올려줘", "오푸스 업그레이드", "/update-doctor" 등으로 호출된다. CLI 버전과 모델을 강제로 최신까지 끌어올리되, 망가진 원인(중복 설치 등)을 찾아 자동 복구한다.
---

# /update-doctor

CLI 버전과 Opus 모델의 **자동 갱신이 오작동했을 때 쓰는 폴백(fallback) 복구 도구**다.

> **전제**: 평소엔 자동으로 갱신돼야 정상이다.
> - **CLI** — native 런처가 새 릴리스를 알아서 받아온다 (`~/.local/share/claude/versions/` 누적).
> - **모델** — `model` 핀이 없는 `default` 상태면 새 기본 Opus를 자동으로 따라간다 (4.7→4.8 처럼).
>
> 이 스킬은 그 자동 경로가 **막혔을 때만** 부른다. 멀쩡하면 건드리지 않는다 (불필요한 변경은 그 자체로 오염).

## 왜 자동 갱신이 막히나 — 알려진 원인

이 스킬은 추측이 아니라 **실제로 겪은 고장 모드**를 기준으로 진단한다.

| 증상 | 원인 | 복구 |
|---|---|---|
| `claude update`가 매번 `Multiple installations found` 경고 | 옛 **npm-global 설치 찌꺼기**가 native와 충돌 (volta image 안에 잔존) | 찌꺼기 제거 (§2) |
| `claude update`가 "up to date"인데 모델이 안 올라감 | CLI는 최신인데 **새 모델 포함 릴리스가 아직 npm에 없음** | 대기 — 로컬로 못 고침 (§3-c) |
| 앱엔 새 Opus가 보이는데 `/model`엔 없음 | **앱=서버 카탈로그**(실시간) vs **CLI=바이너리 카탈로그**(릴리스마다 갱신) | 강제 프로브 시도 (§3-b) |
| `model`이 옛 버전으로 핀 고정됨 | 과거에 특정 ID를 박아둠 | 핀 해제 → `default` (§3-a) |

## 1) 진단 — 무엇이 막혔는지 먼저 측정

아래를 병렬로 돌려 현재 상태를 파악한다. (읽기 전용, 안전)

```bash
# CLI 설치/버전
which -a claude
claude --version
readlink -f "$(which claude)"                                  # native 경로 확인

# 자동 갱신 설정 (native는 autoUpdates:false 가 정상)
jq '{installMethod, autoUpdates, autoUpdatesProtectedForNative, model}' ~/.claude.json

# npm 에 더 새 릴리스가 실제로 있는지 (latest / next / stable)
curl -s https://registry.npmjs.org/@anthropic-ai/claude-code | jq -r '."dist-tags"'

# CLI 바이너리가 아는 Opus 카탈로그 (이 범위까지만 /model 에 뜬다)
strings "$(readlink -f "$(which claude)")" 2>/dev/null | grep -oE 'claude-opus-4-[0-9]+' | sort -u

# 인증 (구독 vs API 키) — 모델 권한 출처 판단
jq -r '{org: .oauthAccount.organizationType, hasApiKey: (.primaryApiKey != null)}' ~/.claude.json
```

진단 결과를 표로 요약해 사용자에게 보여준다: `현재 CLI / npm 최신 / 충돌 여부 / 모델 핀 / 바이너리 최신 Opus`.

## 2) CLI 복구 — 자동 (안전 항목은 알아서)

> 자율성: **안전한 복구는 자동 실행**하고 결과만 보고한다. 파괴적이거나 애매하면 그때만 확인받는다.

### 2-a. 중복 설치 찌꺼기 제거 (가장 흔한 원인)

`claude update` 출력에 `Multiple installations found` / `Leftover npm global` 이 보이면 제거한다.

```bash
# 1차: 표준 명령 (volta가 가로채면 no-op 일 수 있음)
npm -g uninstall @anthropic-ai/claude-code 2>&1 | tail -3

# 2차: volta가 무시하면 — 실물 경로를 직접 확인 후 제거
#  (경고 메시지의 경로를 그대로 사용. 예: ~/.volta/tools/image/node/<ver>/...)
LEFT_BIN="$(claude update 2>&1 | grep -oE '/[^ ]*/bin/claude' | grep -v "$(readlink -f "$(which claude)")" | head -1)"
if [ -n "$LEFT_BIN" ] && [ "$LEFT_BIN" != "$(which claude)" ]; then
  LEFT_PKG="$(dirname "$LEFT_BIN")/../lib/node_modules/@anthropic-ai/claude-code"
  echo "제거 대상: $LEFT_BIN  +  $LEFT_PKG (버전: $(jq -r .version "$LEFT_PKG/package.json" 2>/dev/null))"
  rm -f "$LEFT_BIN"
  rm -rf "$LEFT_PKG"
fi
```

> **안전장치**: 현재 실행 중인 native 바이너리(`which claude` / `readlink -f`)는 **절대 건드리지 않는다.** 제거 대상은 그와 다른 경로의 찌꺼기뿐.

### 2-b. 강제 업데이트 + 검증

```bash
claude update 2>&1 | tail -8
```

- `Multiple installations` 경고가 **사라졌는지** 반드시 재확인한다 (복구 성공 판정 기준).
- `up to date` 면 CLI는 이미 최신. 새 버전을 못 받는 건 §3-c (릴리스 미존재) 문제.

## 3) 모델 복구 — 하이브리드

평소엔 `default`(자동 따라가기) 유지가 원칙이고, 그래도 새 모델이 CLI에 안 뜰 때만 강제 프로브를 **옵션으로** 시도한다.

### 3-a. 핀 점검 → default 보장 (기본)

```bash
jq -r '.model // "(핀 없음 = default, 정상)"' ~/.claude.json
```

- 최상위 `model`이 옛 버전으로 박혀 있으면 → 핀을 빼서 `default`로 되돌릴지 제안한다. (`/model`에서 "기본값" 선택 또는 settings에서 `model` 키 제거)
- `cachedGrowthBookFeatures...model` 같은 **피처플래그 캐시 값은 사용자 설정이 아니다** — 무시한다.

### 3-b. 강제 프로브 (앱엔 있는데 CLI 카탈로그엔 없을 때)

바이너리 최신 Opus가 `4-8`인데 앱에서 더 새 모델을 쓰고 있다면, 다음 ID를 **직접 꽂아 서버가 받아주는지 1회 테스트**한다.

```bash
# 예: 바이너리 최신이 4-8 이면 4-9 를 프로브
CAND="claude-opus-4-9"
claude --model "$CAND" -p "reply with exactly: OK" 2>&1 | tail -5
```

- **성공(OK 응답)** → picker에 없어도 사용 가능. 사용자에게 확인받고 `~/.claude/settings.json`의 `"model": "<ID>"`로 박아 영구 적용.
- **실패(거부/에러)** → 아직 이 경로로는 못 씀. §3-c로 안내.

> ⚠️ 이 단계는 **사용자 계정으로 실제 추론 호출이 1회 발생**한다. 하이브리드 정책상 자동으로 막 돌리지 말고, "강제로 당겨볼까요?"를 물은 뒤 실행한다.

### 3-c. 로컬로 못 고치는 경우 (정직하게 보고)

- npm `latest`/`next`에 **새 모델 포함 CLI가 아직 없고**, 강제 프로브도 실패하면 → **기다리는 수밖에 없다.**
- 이유를 명확히 전달: "계정 권한은 있으나(앱이 증거), 그 모델을 담은 **CLI 릴리스가 아직 안 나옴**. 나오면 native 자동 업데이트가 받아오고 `/model`에 자동 등장."

## 4) 결과 보고

복구 후 한 표로 정리한다.

```
CLI       : 2.1.162 → 2.1.162 (이미 최신)  | 중복설치 제거 ✅ | 충돌경고 사라짐 ✅
모델      : default 유지 (자동 따라가기)    | 강제프로브 4-9 → [성공/실패/생략]
남은 일   : (없음) / 4-9 포함 CLI 릴리스 대기
```

## 5) 자율성 경계 (확정된 정책)

- **자동 실행 OK**: 진단 명령 전부, 중복 npm-global 찌꺼기 제거, `claude update`. (안전 + 되돌리기 쉬움)
- **확인 후 실행**: 모델 강제 프로브(§3-b, 실제 호출 발생), 모델 핀 영구 변경, native 실행 바이너리에 영향 가는 모든 작업.
- **절대 금지**: 현재 실행 중인 native 바이너리/심링크 삭제, `autoUpdatesProtectedForNative` 강제 해제(native 자동 업데이트를 오히려 망칠 수 있음).

## 6) 하지 않는 것

- npm 에 없는 CLI 버전을 "만들어" 받지 않는다 — 릴리스 미존재는 대기 사안.
- 모델 가용성(entitlement)은 로컬에서 못 바꾼다 — 계정/플랜 영역.
- 멀쩡한 자동 경로를 "혹시 몰라" 건드리지 않는다.
