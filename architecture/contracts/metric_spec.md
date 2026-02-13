# Metric Spec - Scene Understanding

## 1. 评估目标
评估三类输出的可用性与一致性：
- 行为标签正确性
- 静态标签字段级一致性
- 动态标签及时间范围一致性

## 2. 指标定义

### 2.1 行为标签
- `Behavior-Acc`：主行为标签准确率
- `Behavior-F1-macro`：宏平均 F1（用于类别不均衡）

### 2.2 静态标签
- `Static-Field-Acc`：逐字段准确率（天气/光照/道路区域）
- `Static-Set-F1`：集合字段 F1（道路类型/特殊静态要素/特殊障碍物）
- `Static-Exact-Match`：6 字段全匹配率

### 2.3 动态标签
- `Dynamic-Label-F1`：仅标签集合 F1（忽略时间）
- `Dynamic-Time-IoU@label`：同标签时间段 IoU
- `Dynamic-Event-EM`：标签+时间范围完全匹配率

### 2.4 结构合法性
- `JSON-Valid-Rate`：可解析 JSON 比例
- `Schema-Valid-Rate`：满足 IO 契约比例

## 3. 汇总口径
建议主指标（用于版本比较）：
- `Primary = 0.4 * Behavior-Acc + 0.3 * Static-Exact-Match + 0.3 * Dynamic-Event-EM`

## 4. 评估输出
每次评估至少输出：
- 总体指标表
- 分类别混淆矩阵（行为标签）
- 动态标签常见错误样例 Top-K

## 5. 版本
- `v1`（2026-02-13）：面向三类标签联合输出的评估口径。
