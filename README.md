# VLM 场景理解工作区

这是一个面向自动驾驶视频场景理解的精简工程。

## 当前范围
- 任务：基于视频 + 结构化先验做场景理解
- 输出：严格 JSON，包含 3 类结果
  - `动态标签`
  - `静态标签`
  - `行为标签`
- 不包含：RLHF/PPO、Agent 流程、工具调用编排

## 当前目录
- `src/`：模型与训练运行时（LlamaFactory 基座）
- `data/raw_data/`：原始数据与 prompt 模板
- `data/processed_data/`：清洗后的训练/验证产物
- `scripts/data_engineering/`：离线数据处理脚本
- `PROJECT_ARCH.md`：架构基线
- `DATA_STATE.md`：数据事实与版本
- `ROLE_DEFINITIONS.md`：角色边界
- `architecture/contracts/`：任务/标签/IO/评估契约

## 核心文档
- `PROJECT_ARCH.md`
- `architecture/contracts/task_spec.md`
- `architecture/contracts/label_schema.md`
- `architecture/contracts/io_contract.md`
- `architecture/contracts/metric_spec.md`
- `DATA_STATE.md`

## 说明
- 本仓库已按当前目标做精简清理。
- 若需要历史上游资料，可查看本地归档目录：`_archive_unused/`。
