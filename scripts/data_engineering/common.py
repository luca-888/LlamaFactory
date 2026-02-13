#!/usr/bin/env python3
"""Common data cleaning utilities for driving label dataset builders."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import Any

SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+_\d{14}$")

STATIC_VALUE_MAP = {
    "雷雨": "雨天",
    "霾_雾霾": "雾天",
    "强光": "逆光",
    "事故车辆": "其他路面异物",
    "三角警示牌": "其他路面异物",
    "内部道路": "城区干道",
}

DYNAMIC_LABEL_MAP = {
    "自车换道_导航换道": "自车换道",
    "自车换道_效率换道": "自车换道",
    "掉头(uturn）": "掉头(uturn)",
}

BEHAVIOR_LABEL_MAP = {
    "危险驾驶": "高风险驾驶",
    "不当驾驶": "不合理驾驶",
}

ALLOWED_BEHAVIOR_LABELS = {"合规驾驶", "高风险驾驶", "特殊驾驶", "不合理驾驶", "违规驾驶"}
BEHAVIOR_PRIORITY = {"违规驾驶": 5, "高风险驾驶": 4, "不合理驾驶": 3, "特殊驾驶": 2, "合规驾驶": 1}

SINGLE_STATIC_CHOICES = {
    "天气": ["晴天", "雨天", "雨后", "大雨", "雪天", "雾天", "阴天"],
    "光照": ["正常光线", "顺光", "弱光", "逆光", "对向远光灯"],
    "道路区域": ["高速", "高架", "城区干道", "城区支路", "郊区", "乡间", "山区"],
}

MULTI_STATIC_CHOICES = {
    "道路类型": ["分流", "合流", "环岛", "桥梁", "隧道", "弯道", "涵洞", "匝道", "异型路口", "十字路口", "T型路口"],
    "特殊静态要素": ["掉头红绿灯", "待转区", "鱼骨线", "双黄隔离线", "双车道线", "减速带", "模糊车道线"],
    "特殊障碍物": ["异型车", "道路封闭标示", "单只锥桶水马", "动物", "其他路面异物", "施工路段"],
}

ALLOWED_DYNAMIC_LABELS = {
    "道路合流", "道路分流", "因前车造成自车减速", "前车加塞(cut_in)", "前车换道(cutout)", "自车换道",
    "减速/停车避让", "临道运动大车", "车道内vru避让", "绕障场景", "路口直行", "左转_有左转红绿灯",
    "左转_无左转红绿灯", "右转", "掉头(uturn)", "转盘绕行", "车道合并", "车道分叉", "驶入分叉道",
    "红绿灯头车启停", "障碍物头车启停", "非头车启停", "进入/驶离待转区", "特殊行车数据", "堵车",
    "自主巡航", "跟车巡航", "限速巡航", "前方行人非机动车", "绕障场景_无违规",
}

ORIGINAL_FRAMES = 600
MP4_FRAMES = 60
MP4_FPS = 4.0
FRAME_INTERVAL = ORIGINAL_FRAMES / MP4_FRAMES


def valid_session_id(session_id: Any) -> bool:
    return isinstance(session_id, str) and bool(SESSION_ID_PATTERN.match(session_id))


def normalize_behavior_label(labels: Any, stats: Counter[str]) -> str | None:
    if not isinstance(labels, list) or not labels:
        return None

    mapped = [BEHAVIOR_LABEL_MAP.get(str(x), str(x)) for x in labels]
    valid = [x for x in mapped if x in ALLOWED_BEHAVIOR_LABELS]
    if not valid:
        return None

    deduped = sorted(set(valid), key=lambda x: -BEHAVIOR_PRIORITY[x])
    if len(deduped) > 1:
        stats["multi_behavior"] += 1
    return deduped[0]


def _split_mixed_value(value: str) -> list[str]:
    text = value.strip()
    if not text:
        return []
    return [x for x in text.split("_") if x]


def _map_static_value(v: str) -> str:
    return STATIC_VALUE_MAP.get(v, v)


def _normalize_single_static(category: str, value: Any, stats: Counter[str]) -> str:
    allowed = set(SINGLE_STATIC_CHOICES[category])

    candidates: list[str] = []
    if isinstance(value, list):
        for x in value:
            candidates.extend(_split_mixed_value(str(x)))
    elif value is not None:
        candidates.extend(_split_mixed_value(str(value)))

    mapped = [_map_static_value(x) for x in candidates]
    valid = [x for x in mapped if x in allowed]
    if valid:
        return valid[0]

    stats[f"invalid_single_static_{category}"] += 1
    return SINGLE_STATIC_CHOICES[category][0]


def _normalize_multi_static(category: str, value: Any, stats: Counter[str]) -> list[str]:
    allowed = set(MULTI_STATIC_CHOICES[category])

    raw_items: list[str] = []
    if isinstance(value, list):
        raw_items = [str(x).strip() for x in value if str(x).strip()]
    elif value is not None:
        text = str(value).strip()
        if text:
            raw_items = [text]

    mapped = [_map_static_value(x) for x in raw_items]
    valid = sorted({x for x in mapped if x in allowed})

    dropped = [x for x in mapped if x not in allowed]
    if dropped:
        stats[f"invalid_multi_static_{category}"] += len(dropped)
    return valid


def normalize_static_labels(static_metadata: Any, stats: Counter[str]) -> dict[str, Any] | None:
    if not isinstance(static_metadata, dict):
        return None
    return {
        "天气": _normalize_single_static("天气", static_metadata.get("天气", ""), stats),
        "光照": _normalize_single_static("光照", static_metadata.get("光照", ""), stats),
        "道路区域": _normalize_single_static("道路区域", static_metadata.get("道路区域", ""), stats),
        "道路类型": _normalize_multi_static("道路类型", static_metadata.get("道路类型", []), stats),
        "特殊静态要素": _normalize_multi_static("特殊静态要素", static_metadata.get("特殊静态要素", []), stats),
        "特殊障碍物": _normalize_multi_static("特殊障碍物", static_metadata.get("特殊障碍物", []), stats),
    }


def _normalize_segments_to_frames(value: Any, stats: Counter[str]) -> list[tuple[int, int]]:
    if not isinstance(value, list):
        return []

    cleaned: list[tuple[int, int]] = []
    for seg in value:
        if not (isinstance(seg, list) and len(seg) == 2):
            stats["invalid_segment_shape"] += 1
            continue
        s, e = seg
        if not (isinstance(s, int) and isinstance(e, int)):
            stats["invalid_segment_type"] += 1
            continue

        s = max(0, min(ORIGINAL_FRAMES, s))
        e = max(0, min(ORIGINAL_FRAMES, e))
        if s >= e:
            stats["invalid_segment_order"] += 1
            continue
        cleaned.append((s, e))

    cleaned.sort(key=lambda x: (x[0], x[1]))
    merged: list[tuple[int, int]] = []
    for s, e in cleaned:
        if not merged or s > merged[-1][1]:
            merged.append((s, e))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
    return merged


def _frames_to_seconds(seg: tuple[int, int]) -> tuple[float, float]:
    s, e = seg
    start_idx = max(0, min(MP4_FRAMES, int(math.floor(s / FRAME_INTERVAL))))
    end_idx = max(0, min(MP4_FRAMES, int(math.ceil(e / FRAME_INTERVAL))))
    if end_idx <= start_idx:
        end_idx = min(MP4_FRAMES, start_idx + 1)
    return (round(start_idx / MP4_FPS, 3), round(end_idx / MP4_FPS, 3))


def normalize_dynamic_events(dynamic_metadata: Any, stats: Counter[str]) -> list[dict[str, Any]] | None:
    if not isinstance(dynamic_metadata, dict):
        return None

    buckets: dict[str, list[tuple[int, int]]] = defaultdict(list)

    for raw_tag, value in dynamic_metadata.items():
        mapped_tag = DYNAMIC_LABEL_MAP.get(raw_tag, raw_tag)
        if not mapped_tag:
            stats["empty_dynamic_tag"] += 1
            continue
        if mapped_tag not in ALLOWED_DYNAMIC_LABELS:
            stats["unknown_dynamic_tag"] += 1
            continue

        buckets[mapped_tag].extend(_normalize_segments_to_frames(value, stats))

    events: list[dict[str, Any]] = []
    for tag in sorted(buckets):
        merged = _normalize_segments_to_frames([[s, e] for s, e in buckets[tag]], stats)
        for seg in merged:
            start_sec, end_sec = _frames_to_seconds(seg)
            events.append({"标签": tag, "时间范围": [start_sec, end_sec]})

    return events
