#!/usr/bin/env python3
"""Build behavior-only SFT dataset with prompt version control."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from common import normalize_behavior_label, valid_session_id
from prompt_loader import list_prompt_versions, load_prompt_config


def build_record(raw: dict[str, Any], stats: Counter[str], prompt: dict[str, Any]) -> dict[str, Any] | None:
    session_id = raw.get("session_id")
    if not valid_session_id(session_id):
        stats["invalid_session_id"] += 1
        return None

    behavior_label = normalize_behavior_label(raw.get("behavior_metadata"), stats)
    if behavior_label is None:
        stats["invalid_behavior"] += 1
        return None

    return {
        "session_id": session_id,
        "prompt_version": prompt.get("name", "unknown"),
        "system": prompt["system"],
        "messages": [
            {"role": "user", "content": prompt["user"]},
            {"role": "assistant", "content": json.dumps({"行为标签": behavior_label}, ensure_ascii=False)},
        ],
        "videos": [f"/f900/APS/tag_system/{session_id}.mp4"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build behavior-only dataset")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--prompt-version", type=str, default="v2")
    parser.add_argument("--list-prompt-versions", action="store_true")
    args = parser.parse_args()

    if args.list_prompt_versions:
        for v in list_prompt_versions("behavior"):
            print(v)
        return

    if args.input is None or args.output is None:
        parser.error("--input and --output are required unless --list-prompt-versions is used")

    prompt = load_prompt_config("behavior", args.prompt_version)

    raw_data = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(raw_data, list):
        raise ValueError(f"Input must be a list, got: {type(raw_data).__name__}")

    stats: Counter[str] = Counter()
    cleaned: list[dict[str, Any]] = []
    for item in raw_data:
        if not isinstance(item, dict):
            stats["non_dict_row"] += 1
            continue
        rec = build_record(item, stats, prompt)
        if rec is None:
            stats["dropped"] += 1
            continue
        cleaned.append(rec)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")

    report = {
        "task": "behavior",
        "prompt_version": args.prompt_version,
        "input_file": str(args.input),
        "output_file": str(args.output),
        "input_rows": len(raw_data),
        "output_rows": len(cleaned),
        "drop_ratio": round((len(raw_data) - len(cleaned)) / max(1, len(raw_data)), 6),
        "stats": dict(stats),
    }

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
