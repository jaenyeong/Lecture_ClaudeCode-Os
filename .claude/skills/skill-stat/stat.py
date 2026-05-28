#!/usr/bin/env python3
"""skill-stat: 누적된 스킬 호출 통계를 CLI 표로 출력한다.

데이터 소스
-----------
``.claude/logs/skill-stats.jsonl`` — 한 줄이 한 번의 스킬 호출.
스키마: ``{"ts": ISO8601, "skill": str, "duration_ms": int|null, "session_id": str}``

집계 컬럼
---------
- ``COUNT``     : 호출 횟수
- ``AVG(ms)``   : 평균 소요 시간 (duration_ms 가 기록된 호출만 평균)
- ``TOTAL(ms)`` : 총 소요 시간
- ``LAST USED`` : 가장 최근 호출 시각 (UTC)
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
STATS_PATH = PROJECT_DIR / ".claude" / "logs" / "skill-stats.jsonl"


def load_records() -> list:
    if not STATS_PATH.exists():
        return []
    records = []
    for line in STATS_PATH.read_text("utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def aggregate(records: list) -> list:
    by_skill = defaultdict(lambda: {
        "count": 0,
        "total_ms": 0,
        "duration_count": 0,
        "last_used": "",
    })
    for r in records:
        skill = r.get("skill") or "(unknown)"
        bucket = by_skill[skill]
        bucket["count"] += 1
        d = r.get("duration_ms")
        if isinstance(d, (int, float)):
            bucket["total_ms"] += int(d)
            bucket["duration_count"] += 1
        ts = r.get("ts") or ""
        if ts > bucket["last_used"]:
            bucket["last_used"] = ts

    rows = []
    for skill, b in by_skill.items():
        avg = (b["total_ms"] // b["duration_count"]) if b["duration_count"] else 0
        rows.append({
            "skill": skill,
            "count": b["count"],
            "avg_ms": avg,
            "total_ms": b["total_ms"],
            "last_used": b["last_used"] or "-",
        })
    rows.sort(key=lambda r: r["count"], reverse=True)
    return rows


def render_table(rows: list) -> str:
    headers = ["SKILL", "COUNT", "AVG(ms)", "TOTAL(ms)", "LAST USED"]
    data = [
        [r["skill"], str(r["count"]), str(r["avg_ms"]), str(r["total_ms"]), r["last_used"]]
        for r in rows
    ]
    widths = []
    for i, h in enumerate(headers):
        col_widths = [len(h)] + [len(d[i]) for d in data]
        widths.append(max(col_widths))

    def fmt(cols):
        return "  ".join(c.ljust(w) for c, w in zip(cols, widths))

    sep = "  ".join("-" * w for w in widths)
    return "\n".join([fmt(headers), sep] + [fmt(d) for d in data])


def main() -> int:
    records = load_records()
    if not records:
        print("(아직 기록된 스킬 호출이 없습니다. 스킬을 한두 번 호출한 뒤 다시 실행해 주세요.)")
        print(f"source: {STATS_PATH}")
        return 0
    rows = aggregate(records)
    print(render_table(rows))
    print(f"\n총 {sum(r['count'] for r in rows)}건 기록 · source: {STATS_PATH.relative_to(PROJECT_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
