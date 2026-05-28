#!/usr/bin/env python3
"""Skill 호출 통계를 기록하는 훅 스크립트.

Claude Code 의 PreToolUse / PostToolUse 훅에서 호출된다. matcher 가 `Skill`
로 걸려 있으므로 이 스크립트는 Skill 도구 호출에 대해서만 실행된다.

동작
----
- `--event pre`  : 호출 시작 시각을 `.claude/logs/.skill_stat_pending.json` 에
                   `(session_id, skill)` 키로 저장한다.
- `--event post` : pending 에서 시작 시각을 꺼내 소요 시간을 계산하고,
                   `.claude/logs/skill-stats.jsonl` 에 한 줄을 append 한다.

훅 입력
-------
표준 입력으로 JSON 페이로드가 들어온다. 최소한 다음 필드를 사용한다::

    {
      "session_id": "...",
      "tool_name":  "Skill",
      "tool_input": {"skill": "<skill-name>", ...}
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
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
LOG_DIR = PROJECT_DIR / ".claude" / "logs"
STATS_PATH = LOG_DIR / "skill-stats.jsonl"
PENDING_PATH = LOG_DIR / ".skill_stat_pending.json"


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
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", choices=["pre", "post"], required=True)
    args = parser.parse_args()
    try:
        payload = _read_payload()
        if args.event == "pre":
            handle_pre(payload)
        else:
            handle_post(payload)
    except Exception as e:
        print(f"[skill_stat] non-blocking error: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
