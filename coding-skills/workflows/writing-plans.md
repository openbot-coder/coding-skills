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

> **致 Claude：** 必需子技能：使用 workflows:executing-plans 逐任务实现此计划。

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

**步骤 1：编写测试用例文档，提交审核**

coder 编写测试用例需求文档，包含：
- 测试用例编号
- 测试前置条件
- 测试输入
- 预期输出
- 覆盖场景（正例/反例/边界值）

提交给 reviewer 审核：
- 测试用例与任务描述是否一致？
- 测试用例是否完整（覆盖所有场景）？
- 验收标准是否可测试？

**审核结论：**
| 结论 | 操作 |
|------|------|
| 通过 | 进入步骤 2 |
| 需修改 | 返回 coder 重新编写测试用例文档，重新提交审核 |

---

**步骤 2：编写测试用例，验证执行失败**

根据审核通过的测试用例文档编写测试代码：

```python
def test_specific_behavior():
    """测试用例编号：TC-XXX
    覆盖场景：正例/反例/边界值
    """
    result = function(input)
    assert result == expected
```

运行测试验证失败：

运行：`pytest tests/path/test.py::test_name -v`
期望：失败，提示 "function not defined"

---

**步骤 3：coder 编写最小实现**

**执行者：** coder

```python
def function(input):
    return expected
```

---

**步骤 4：reviewer 执行测试验证**

**执行者：** reviewer agent

运行：`pytest tests/path/test.py::test_name -v --cov=src --cov-report=term-missing`

验证：
- 测试全部通过
- 覆盖率 100%

**覆盖率说明：**
- 如有无法测试的代码，标注原因（如：第三方库调用、ORM 自动生成方法等）

**验证结论：**
| 结论 | 操作 |
|------|------|
| 通过 | 进入步骤 5 |
| 失败 | 返回 coder 修复，进入新一轮验证 |

---

**步骤 5：提交**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## 注意事项
- 总是使用精确的文件路径
- 计划中包含完整代码（而非"添加验证"）
- 精确命令及期望输出
- 使用 @ 语法引用相关技能
- DRY、YAGNI、TDD、频繁提交

## 执行交接

保存计划后，提供执行选择：

**"计划已完成并保存到 `docs/plans/<filename>.md`。两种执行选项：**

**1. 子代理驱动（当前会话）** - 我为每个任务派发新子代理，任务间审查，快速迭代

**2. 并行会话（单独）** - 在新会话中打开执行计划，批量执行带检查点

**选择哪种方式？"**

**如果选择子代理驱动：**
- **必需子技能：** 使用 workflows:subagent-driven-development
- 留在当前会话
- 每个任务新子代理 + 代码审查

**如果选择并行会话：**
- 引导他们在工作树中打开新会话
- **必需子技能：** 新会话使用 workflows:executing-plans
