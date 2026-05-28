#!/usr/bin/env python3
"""Skill 호출 통계를 기록하는 훅 스크립트.

Claude Code 의 PreToolUse / PostToolUse / UserPromptSubmit 훅에서 호출된다.

동작
----
- `--event pre`         : (matcher="Skill") 어시스턴트가 Skill tool 을 호출한
                          시작 시각을 `.claude/logs/.skill_stat_pending.json` 에
                          저장한다.
- `--event post`        : (matcher="Skill") pending 에서 시작 시각을 꺼내
                          소요 시간을 계산하고 jsonl 에 한 줄 append 한다.
                          `source: "skill_tool"` 로 표시.
- `--event user-prompt` : 사용자가 직접 입력한 프롬프트에서 `/<skill-name>`
                          패턴을 감지해 invocation 만 기록한다. duration 은
                          측정할 수 없으므로 `duration_ms: null`,
                          `source: "user_prompt"` 로 남긴다. 로컬
                          `.claude/skills/<name>/SKILL.md` 가 실제로 존재할
                          때만 기록 (built-in `/help`, `/clear`, 플러그인
                          네임스페이스 등은 통계 대상에서 제외).

훅 입력
-------
표준 입력으로 JSON 페이로드가 들어온다.

- Skill tool 경로::
    {
      "session_id": "...",
      "tool_name":  "Skill",
      "tool_input": {"skill": "<skill-name>", ...}
    }
- 사용자 프롬프트 경로::
    {
      "session_id": "...",
      "prompt": "<raw user input>"
    }

원칙
----
훅은 사용자 작업을 절대 막지 않는다. 어떤 예외가 발생해도 stderr 로 한 줄만
남기고 exit code 0 으로 끝낸다.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
LOG_DIR = PROJECT_DIR / ".claude" / "logs"
SKILLS_DIR = PROJECT_DIR / ".claude" / "skills"
STATS_PATH = LOG_DIR / "skill-stats.jsonl"
PENDING_PATH = LOG_DIR / ".skill_stat_pending.json"

SLASH_PATTERN = re.compile(r"^\s*/([A-Za-z][\w-]*)\b")


def _now_ms() -> int:
    return time.time_ns() // 1_000_000


def _read_payload() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def _skill_name(payload: dict) -> str | None:
    tool_input = payload.get("tool_input") or {}
    return tool_input.get("skill") or tool_input.get("name")


def _pending_key(payload: dict, skill: str) -> str:
    return f"{payload.get('session_id', 'unknown')}::{skill}"


def _load_pending() -> dict:
    if not PENDING_PATH.exists():
        return {}
    try:
        return json.loads(PENDING_PATH.read_text("utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_pending(pending: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    PENDING_PATH.write_text(json.dumps(pending), encoding="utf-8")


def _append_jsonl(record: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False) + "\n"
    with STATS_PATH.open("a", encoding="utf-8") as f:
        f.write(line)


def handle_pre(payload: dict) -> None:
    skill = _skill_name(payload)
    if not skill:
        return
    pending = _load_pending()
    pending[_pending_key(payload, skill)] = _now_ms()
    _save_pending(pending)


def handle_post(payload: dict) -> None:
    skill = _skill_name(payload)
    if not skill:
        return
    pending = _load_pending()
    key = _pending_key(payload, skill)
    start_ms = pending.pop(key, None)
    duration_ms = (_now_ms() - start_ms) if start_ms is not None else None
    _save_pending(pending)
    _append_jsonl({
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "skill": skill,
        "duration_ms": duration_ms,
        "session_id": payload.get("session_id"),
        "source": "skill_tool",
    })


def _detect_local_skill(prompt: str) -> str | None:
    """프롬프트 첫 토큰이 `/<name>` 이고 로컬 스킬 디렉터리에 존재하면 이름 반환."""
    if not prompt:
        return None
    m = SLASH_PATTERN.match(prompt)
    if not m:
        return None
    name = m.group(1)
    if (SKILLS_DIR / name / "SKILL.md").is_file():
        return name
    return None


def handle_user_prompt(payload: dict) -> None:
    prompt = payload.get("prompt") or ""
    skill = _detect_local_skill(prompt)
    if not skill:
        return
    _append_jsonl({
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "skill": skill,
        "duration_ms": None,
        "session_id": payload.get("session_id"),
        "source": "user_prompt",
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--event",
        choices=["pre", "post", "user-prompt"],
        required=True,
    )
    args = parser.parse_args()
    try:
        payload = _read_payload()
        if args.event == "pre":
            handle_pre(payload)
        elif args.event == "post":
            handle_post(payload)
        else:
            handle_user_prompt(payload)
    except Exception as e:
        print(f"[skill_stat] non-blocking error: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
