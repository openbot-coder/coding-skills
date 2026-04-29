---
name: writing-plans
description: 当你有多步骤任务的规格或需求时使用，在触碰代码之前
---

# 编写计划

## 概述

编写全面的实现计划，假设工程师对代码库零上下文且品味存疑。记录他们需要知道的一切：每个任务要触及哪些文件、代码、测试、可能需要查看的文档、如何测试。以小步骤任务的形式给出整个计划。DRY。YAGNI。TDD。频繁提交。

假设他们是熟练的开发者，但几乎不了解我们的工具集或问题领域。假设他们不太了解好的测试设计。

**开始时宣布：** "我正在使用编写计划技能来创建实现计划。"

**上下文：** 
- 此阶段在 `writing-prd-and-design` 之后执行
- PRD 和详细设计文档应已获得批准
- 这应该在专用工作树中运行

**保存计划到：** `docs/plans/YYYY-MM-DD-<feature-name>.md`

## 小步骤任务粒度

**每个步骤是一个动作（2-5 分钟）：**
- "编写失败的测试" - 步骤
- "运行以确保它失败" - 步骤
- "实现让测试通过的最少代码" - 步骤
- "运行测试确保通过" - 步骤
- "提交" - 步骤

## 计划文档头部

**每个计划必须以此头部开始：**

```markdown
# [功能名称] 实现计划

> **致 Claude：** 必需子技能：使用 workflows:subagent-driven-development 逐任务实现此计划。

**目标：** [一句话描述这构建了什么]

**架构：** [2-3 句关于方法]

**技术栈：** [关键技术/库]

---
```

## 任务结构

````markdown
### 任务 N：[组件名称]

**文件：**
- 创建：`exact/path/to/file.py`
- 修改：`exact/path/to/existing.py:123-145`
- 测试：`tests/exact/path/to/test.py`

---

> **TDD 执行：** 此任务使用 workflows:subagent-driven-development 的 TDD 流程执行：
> 1. implementer 编写测试用例文档 → reviewer 审核
> 2. implementer 编写测试用例（验证失败）
> 3. implementer 编写最小实现
> 4. reviewer 验证测试通过 + 覆盖率 100%
> 5. implementer 提交代码

````

## 子代理角色（执行时）

执行过程中使用两个独立的子代理：

| 子代理 | 职责 |
|--------|------|
| **implementer** | 编写代码和测试，实现 TDD 流程 |
| **reviewer** | 审核测试用例文档、验证测试结果 |

**重要：implementer 和 reviewer 是两个不同的子代理，不能由同一个代理执行。**

详细 TDD 流程见 [workflows:subagent-driven-development](#tdd-执行步骤每个任务)。

## 注意事项
- 总是使用精确的文件路径
- 计划中包含完整代码（而非"添加验证"）
- 精确命令及期望输出
- 使用 @ 语法引用相关技能
- DRY、YAGNI、TDD、频繁提交

## 执行交接

保存计划后：

**"计划已完成并保存到 `docs/plans/<filename>.md`。**

**必需子技能：** 使用 workflows:subagent-driven-development 执行此计划。

**TDD 流程：**
1. implementer 编写测试用例文档，reviewer 审核
2. implementer 编写测试用例（验证失败）
3. implementer 编写最小实现
4. reviewer 验证测试通过 + 覆盖率 100%
5. implementer 提交代码

**每个任务完成后两阶段审查：**
1. 规格合规审查
2. 代码质量审查
