# PROJECT_ARCH

## 1. 当前状态（2026-02-13）
- 项目基座：`LlamaFactory`，主代码在 `src/llamafactory/`。
- 可复用核心：`src/llamafactory/v1/` 已具备较清晰分层（`config` / `core` / `plugins` / `trainers` / `samplers`）。
- 业务目标（当前阶段）：仅做 **VLM 场景理解**（Scene Understanding），不扩展到 RL、Agent、工具调用编排等复杂链路。
- 数据现状：驾驶行为数据已完成 v1 清洗并生成 SFT 数据，见 `data/processed_data/` 与 `DATA_STATE.md`。

## 2. 架构目标
在不破坏上游框架的前提下，建立一层“场景理解业务域”架构：
- 对外保持与 `v1` 训练/推理入口兼容。
- 对内将“数据定义、任务模板、评估协议、运行配置”分离，避免脚本化耦合。
- 先支持单任务闭环：`视频 + 结构化先验 -> 三类标签联合输出（动态/静态/行为）`。

## 3. 模块边界（必须遵守）

### 3.1 分层边界
- `Core Layer`（框架层）
  - 路径：`src/llamafactory/v1/core`, `src/llamafactory/v1/config`, `src/llamafactory/v1/plugins`
  - 职责：模型装载、训练循环、渲染器、插件机制、分布式能力。
  - 约束：不包含业务任务语义。

- `Domain Layer`（业务域层，新增）
  - 路径（规划）：`src/llamafactory/v1/domain/scene_understanding/`
  - 职责：场景理解任务定义、标签空间、输入输出协议、指标协议。
  - 约束：不直接依赖具体训练器实现细节（如 deepspeed 对象），通过 `core/plugins` 暴露能力。

- `Application Layer`（编排层，新增）
  - 路径（规划）：`src/llamafactory/v1/apps/scene_understanding/`
  - 职责：组装 Domain + Core，形成可执行入口（train/infer/eval 的工作流编排）。
  - 约束：只做流程编排，不承载清洗逻辑或模型底层 patch。

### 3.2 依赖方向
仅允许：
1. `apps -> domain -> core/plugins`
2. `apps -> core/config`
3. `domain -> 协议/常量/模板`

禁止：
1. `core -> domain`（核心层反向依赖业务域）
2. `domain -> trainers具体实现`（跨层耦合）
3. `scripts` 直接作为长期主入口（脚本仅用于临时或一次性任务）

## 4. 目录结构规划（目标形态）

```text
src/llamafactory/v1/
  domain/
    scene_understanding/
      task_spec.py          # 任务定义：输入模态、输出空间、约束
      label_schema.py       # 标签与映射规则（唯一可信来源）
      prompt_spec.py        # 模板协议（不是具体数据清洗）
      metric_spec.py        # 指标协议（准确率/F1/混淆矩阵接口）
      io_contract.py        # 样本字段契约与校验契约
  apps/
    scene_understanding/
      train_workflow.py     # 训练编排入口
      infer_workflow.py     # 推理编排入口
      eval_workflow.py      # 评估编排入口
      wiring.py             # 依赖装配（ModelEngine/DataEngine/Plugins）
  plugins/
    data_plugins/
      converters/
        scene_understanding.py   # 任务专用 converter（可选扩展）
```

补充说明：
- 若短期不新增 Python 包目录，可先在 `architecture/contracts/` 放置契约文档，再逐步代码化。
- `scripts/data_engineering/` 保留为离线数据生产，不承担在线推理/训练编排职责。

## 5. 与当前仓库的映射
- 训练主链路复用：`src/llamafactory/v1/trainers/sft_trainer.py`
- 数据加载复用：`src/llamafactory/v1/core/data_engine.py`
- 模型与渲染复用：`src/llamafactory/v1/core/model_engine.py`
- 插件扩展点：`src/llamafactory/v1/plugins/data_plugins/`

结论：当前最小改动路径是“在 `v1` 上加 domain/apps 薄层”，而不是改造 legacy `src/llamafactory/train/`。

## 6. 里程碑（只含架构动作）

### M0：冻结边界（现在）
- 确认仅支持“VLM 场景理解”单任务。
- 冻结标签集合与输出契约（严格 JSON：动态/静态/行为）。
- 在评审中强制检查依赖方向。

### M1：文档化契约
- 固化 `Task Spec / Label Schema / IO Contract / Metric Spec`。
- 将数据字段与 prompt 约束从脚本注释迁移到架构文档。

### M2：目录落位
- 创建 `domain/scene_understanding` 与 `apps/scene_understanding` 空骨架。
- 明确 train/infer/eval 三入口的参数面，避免后续 CLI 漫涨。

### M3：插件收口
- 将场景理解数据转换能力收敛到 data plugin 扩展点。
- 脚本与插件职责分离：脚本负责离线产物，插件负责运行时对接。

## 7. 非目标（当前阶段不做）
- 不做多任务统一调度。
- 不做 RLHF/PPO 链路并入。
- 不做在线服务网关与多租户隔离。
- 不改造底层分布式引擎抽象。

## 8. 架构决策记录（ADR）

### ADR-001：以 `v1` 为唯一演进主线
- 决策：新能力优先放在 `src/llamafactory/v1/`，不在 legacy `train/` 增量堆功能。
- 原因：`v1` 已具备 core/plugin 分层，迁移成本低且边界更清晰。

### ADR-002：场景理解采用“单任务单输出契约”
- 决策：固定单任务，但输出为三类标签联合 JSON（动态/静态/行为），不引入解释生成。
- 原因：与现有数据清洗与标注目标一致，同时保持可评估和可解析。

### ADR-003：脚本不作为长期系统边界
- 决策：`scripts/` 仅用于离线处理与实验，正式流程通过 apps + domain 组织。
- 原因：避免流程碎片化和隐式依赖。

## 9. 维护规则
- 本文件是架构唯一基线文档，任何模块新增/迁移前先更新本文件。
- 变更必须包含：
  - 影响边界
  - 依赖方向变化
  - 回滚策略
- 若与 `DATA_STATE.md` 冲突：
  - 数据事实以 `DATA_STATE.md` 为准
  - 模块边界与目录归属以 `PROJECT_ARCH.md` 为准

## 10. 契约文档索引
- `architecture/contracts/task_spec.md`
- `architecture/contracts/label_schema.md`
- `architecture/contracts/io_contract.md`
- `architecture/contracts/metric_spec.md`
