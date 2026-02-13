# IO Contract - Scene Understanding

## 1. 输入样本契约
每条样本最小字段：
- `session_id: str`
- `videos: list[str]`（长度 >= 1）
- `conversations: list[message]`（ShareGPT 格式）

数据来源字段（用于离线清洗）：
- `dynamic_metadata: dict`
- `static_metadata: dict`
- `behavior_metadata: list[str]`

## 2. 输出 JSON 契约
必须满足：
- 顶级 key 固定为：`动态标签`、`静态标签`、`行为标签`
- 禁止输出额外解释文本

JSON 结构：
```json
{
  "动态标签": [{"标签": "路口直行", "时间范围": [1.25, 4.5]}],
  "静态标签": {
    "天气": "晴天",
    "光照": "正常光线",
    "道路区域": "城区干道",
    "道路类型": ["十字路口"],
    "特殊静态要素": ["双车道线"],
    "特殊障碍物": []
  },
  "行为标签": ["合规驾驶"]
}
```

## 3. 时间范围规则
- 原始区间先裁剪到 `[0,600]` 且满足 `start < end`
- 映射步骤：
  - `start_idx = floor(start / 10)`
  - `end_idx = ceil(end / 10)`
  - 再裁剪到 `[0,60]`
  - 秒级：`start_sec = start_idx / 4`，`end_sec = end_idx / 4`

## 4. 校验建议（运行前）
- schema 校验：字段齐全、类型正确。
- 标签校验：行为标签必须属于闭集。
- 时间校验：动态标签时间范围满足 `0 <= start < end <= 15`。
