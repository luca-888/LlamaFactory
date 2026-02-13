#!/usr/bin/env python3
"""Prompt version registry and loader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROMPT_ROOT = Path(__file__).resolve().parent / "prompts"


def load_prompt_config(task: str, version: str) -> dict[str, Any]:
    path = PROMPT_ROOT / task / f"{version}.json"
    if not path.exists():
        raise FileNotFoundError(f"Prompt version not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if "system" not in data or "user" not in data:
        raise ValueError(f"Invalid prompt file (need system/user): {path}")
    return data


def list_prompt_versions(task: str) -> list[str]:
    task_dir = PROMPT_ROOT / task
    if not task_dir.exists():
        return []
    return sorted([p.stem for p in task_dir.glob("*.json")])
