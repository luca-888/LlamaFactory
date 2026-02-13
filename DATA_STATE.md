# 数据状态(原始数据,处理流程,pipeline,版本管理)

## 基础数据情况
- 原始数据切分在 `data/raw_data`：
  - `train_full_217735_v2.json`
  - `train_17216_v2.json`
  - `val_3738_v4.json`
- 视频路径规则：`/f900/APS/tag_system/{session_id}.mp4`

## 任务拆分（已重构）
已拆分为两条独立 pipeline：

- 行为任务（当前 focus）
  - 脚本：`scripts/data_engineering/build_behavior_dataset.py`
  - 输出：仅 `{"行为标签":"<标签>"}`
- 三标签任务（独立保留）
  - 脚本：`scripts/data_engineering/build_tri_dataset.py`
  - 输出：`动态标签 + 静态标签 + 行为标签`

公共清洗逻辑在：`scripts/data_engineering/common.py`

## Prompt 版本控制
Prompt 按任务独立版本化：

- 行为任务：`scripts/data_engineering/prompts/behavior/`
  - `v1.json`
  - `v2.json`（默认）
  - `v3.json`
- 三标签任务：`scripts/data_engineering/prompts/tri/`
  - `v1.json`（默认）

加载器：`scripts/data_engineering/prompt_loader.py`

## 当前建议流程（行为任务）
1. 清理旧产物：清空 `data/processed_data/`
2. 生成行为训练集（train/val）
3. 固定 prompt 版本（建议先 `v2`），做单任务收敛
4. 稳定后再切换到三标签联合训练

## 清洗规则（共享）
- `session_id` 校验：`^[A-Za-z0-9_-]+_\d{14}$`
- 映射规则（继承旧脚本逻辑）：
  - 静态：`雷雨->雨天`，`霾_雾霾->雾天`，`强光->逆光`，`内部道路->城区干道`，`事故车辆/三角警示牌->其他路面异物`
  - 动态：`自车换道_导航换道/自车换道_效率换道->自车换道`，`掉头(uturn）->掉头(uturn)`
  - 行为：`危险驾驶->高风险驾驶`，`不当驾驶->不合理驾驶`
- 时间映射：600 帧标注 -> 60 帧索引 -> 秒（4fps）

## 版本管理
- `v4`（2026-02-13）
  - 清理 processed data 后完成 pipeline 拆分
  - 行为任务与三标签任务独立脚本
  - 引入 prompt version control，并新增行为 prompt 示例版本（v1/v2/v3）
