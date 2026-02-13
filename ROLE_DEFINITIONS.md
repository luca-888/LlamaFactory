# ROLE DEFINITIONS

## 总则
- 本文件定义角色边界与交接规则，避免职责重叠。
- 角色变更先更新本文件，再执行实际改动。

## ARCHITECT
工作文档：
- `PROJECT_ARCH.md`

Scope：
- 模块边界设计
- 目录结构规划
- 依赖方向约束
- 架构 ADR 维护

Output：
- 架构基线与变更记录（`PROJECT_ARCH.md`）
- 目录规划与分层约束

Definition of Done：
- 边界、依赖方向、非目标写清楚
- 与 `DATA_STATE.md` 无事实冲突

Forbidden：
- 写业务实现代码
- 修改训练超参数
- 修改数据内容

## DATA_ENGINEER
工作文档：
- `DATA_STATE.md`
- `data/raw_data/PROMPT_TEMPLATE.md`

Scope：
- 数据清洗流程
- 标签映射与样本校验
- Prompt 模板维护
- 产物版本管理

Output：
- 可训练数据产物（`data/processed_data/`）
- 数据版本与规则说明（`DATA_STATE.md`）

Definition of Done：
- 清洗规则可复现
- 输入输出字段与契约一致
- 新版本含变更说明与产物清单

Forbidden：
- 修改训练参数与训练策略
- 改动架构边界定义

## TRAIN_ENGINEER
工作文档：
- 训练配置文件（如 yaml / deepspeed config）

Scope：
- 训练参数配置
- batch / lr / 资源配置
- 训练稳定性与吞吐优化

Output：
- 可复现训练配置
- 训练日志与核心指标摘要

Definition of Done：
- 可复现跑通
- 参数修改有理由和记录
- 不破坏数据与标签契约

Forbidden：
- 修改数据样本与清洗逻辑
- 改写任务标签定义

## AUDITOR
工作文档：
- 审查报告（可附在 MR/PR 描述或独立 md）

Scope：
- 结构审查
- 依赖越界检查
- 风险识别（回归、数据泄漏、评估口径偏差）

Output：
- 按严重级别排序的问题清单
- 修复建议与阻断项

Definition of Done：
- 关键风险有证据与定位
- 结论可执行（明确到文件/模块）

Forbidden：
- 直接实现新功能
- 以“建议”替代证据

## 交接规则
- `ARCHITECT -> DATA_ENGINEER`：提供任务边界与 IO/标签契约。
- `DATA_ENGINEER -> TRAIN_ENGINEER`：提供稳定数据版本与字段说明。
- `TRAIN_ENGINEER -> AUDITOR`：提供配置、日志、评估结果。
- `AUDITOR -> 全角色`：返回阻断项与修复优先级。
