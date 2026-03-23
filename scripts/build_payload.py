#!/usr/bin/env python3
"""Build a poster payload JSON from a simplified list structure.

Input (JSON):
{
  "date": "YYYY-MM-DD",
  "items": [{"rank":1,"text":"...","sources":["...",...]}, ...],
  "meta": {"lunar": "...", "signature": "@...", "sources": ["...", ...], "updated_at": "..."}
}

Output (JSON):
{
  "date": "YYYY-MM-DD",
  "date_cn": "YYYY年M月D日",
  "weekday_cn": "星期一",
  "lunar": "农历 · ..." (or ""),
  "items": [{"rank":1,"text":"..."}, ...],
  "sources_line": "新闻联播 / 人民日报 / ...",
  "updated_at": "更新于：YYYY/MM/DD HH:mm",
  "signature": "@..."
}
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


WEEKDAY_CN = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


def _date_cn(d: datetime) -> str:
    return f"{d.year}年{d.month}月{d.day}日"


def _weekday_cn(d: datetime) -> str:
    return WEEKDAY_CN[d.weekday()]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--out", dest="out", required=True)
    args = p.parse_args()

    raw = json.loads(Path(args.inp).read_text(encoding="utf-8"))
    date_str = raw.get("date") or datetime.now().strftime("%Y-%m-%d")
    d = datetime.strptime(date_str, "%Y-%m-%d")

    items = raw.get("items", [])
    meta = raw.get("meta", {})

    lunar = meta.get("lunar", "")
    if lunar and not lunar.startswith("农历"):
        lunar = "农历 · " + str(lunar)

    sources_list = meta.get("sources", [])
    if isinstance(sources_list, str):
        sources_line = sources_list
    else:
        sources_line = " / ".join([str(x) for x in sources_list if str(x).strip()])
    if sources_line:
        sources_line = "来源：" + sources_line
    else:
        sources_line = "来源：综合多家权威媒体"

    updated_at = meta.get("updated_at", "")
    if updated_at:
        # allow either already formatted or ISO-ish
        if updated_at.startswith("更新于"):
            upd = updated_at
        else:
            upd = "更新于：" + str(updated_at)
    else:
        upd = ""

    payload = {
        "date": date_str,
        "date_cn": _date_cn(d),
        "weekday_cn": _weekday_cn(d),
        "lunar": lunar,
        "items": [{"rank": int(it.get("rank", i + 1)), "text": str(it.get("text", "")).strip()} for i, it in enumerate(items)][:15],
        "sources_line": sources_line,
        "updated_at": upd,
        "signature": meta.get("signature", ""),
    }

    Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
