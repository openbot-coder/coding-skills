***

version: 0.6.0
name: vibe-coding
description: "轻量级 AI 编程技能。代码探索 → 需求分析 → 任务拆解 → 代码执行 → 测试验证 → 需求归档。"
-------------------------------------------------------------------------------------------

# Vibe Coding — 轻量级开发工作流

## 概述

所有开发任务首先进入这里。此技能识别当前开发阶段并路由到适当的操作。永远不要直接跳到编码 — 始终先确定阶段。

**核心原则：** 先想清楚再动手，每一步都有据可查。

## 五阶段工作流

```
阶段1: 需求分析 → 阶段2: 任务拆解 → 阶段3: 代码执行 → 阶段4: 测试验证 → 阶段5: 需求归档
```

| 阶段 | 脚本/技能 | 时机 | 输出 |
|------|----------|------|------|
| 1. 需求分析 | writing-design + review-design | 需求出现，需要设计 | `{name}-design.md`（已批准） |
| 2. 任务拆解 | `python scripts/plans.py --name <名称>` | 设计已批准，需要计划 | `{name}-progress.md`（计划 + 任务清单） |
| 3. 代码执行 | `python scripts/execute.py --name <名称> --task <编号>` | 计划已定，开始编码 | 更新 `{name}-progress.md` 任务状态 |
| 4. 测试验证 | `python scripts/verify.py --name <名称>` | 编码完成，需要验证 | `{name}-progress.md` |
| 5. 需求归档 | `python scripts/archive.py --name <名称>` | 用户批准，归档收尾 | 移动到 `archive/` |

## 阶段路由

### 阶段1：需求分析

**子流程：** `writing-design → review-design → [用户批准] → 阶段2`

- **writing-design**：[详细规则](./writing-design/SKILL.md)
- **review-design**：[详细规则](./review-design/SKILL.md)

**操作：**
1. 运行 `python scripts/design.py --name <变更名称> --desc "<简要描述>"`
2. 完成需求调研，记录到 `{name}-design.md`
3. 进入 review-design 审查
4. 审查通过后请求用户批准
5. 批准后进入阶段2

### 阶段2：任务拆解

**操作：**
1. 运行 `python scripts/plans.py --name <变更名称>`
2. 在 `{name}-progress.md` 中填充计划概述和任务清单
3. 确认完整后进入阶段3

**规则：** 每个任务 10~20 个功能点，必须可独立验证

### 阶段3：代码执行

**TDD 模式：** [详细规则](./test-driven-development/SKILL.md)

**操作：**
1. 查看任务：`python scripts/execute.py --name <名称> --action list`
2. 开始任务：`python scripts/execute.py --name <名称> --task <编号> --action start`
3. 遵循 TDD 循环：红 → 绿 → 重构
4. 完成任务：`python scripts/execute.py --name <名称> --task <编号> --action done`
5. 所有任务完成后进入阶段4

### 阶段4：测试验证

**操作：**
1. 开始验证：`python scripts/verify.py --name <名称> --action start`
2. 进行系统集成测试
3. 验证通过后请求用户批准
4. 批准后进入阶段5

**验证标准：** 单元测试覆盖率 100%，集成测试通过

### 阶段5：需求归档

**前提条件：** 阶段4验证通过 + 用户批准

**操作：**
1. 运行 `python scripts/archive.py --name <变更名称>`
2. 脚本将提交 Git、推送远程、创建版本标签、归档变更
3. 创建 PR 将 `develop` 合并到 `main`

## 状态判断

| 文件状态 | 当前阶段 | 下一步 |
|----------|----------|--------|
| `{name}-design.md` 不存在 | 阶段1：writing-design | 开始需求调研 |
| `{name}-design.md` 存在，"Agent审查"为 ⏳ | 阶段1：review-design | 审查设计 |
| `{name}-design.md` 审查通过，"用户批准"为 ⏳ | 阶段1：等待批准 | 请求用户批准 |
| `{name}-design.md` 已批准 | 阶段2：任务拆解 | 运行 plans.py |
| 阶段2完成，有未完成任务 | 阶段3：代码执行 | 运行 execute.py |
| 所有任务完成 | 阶段4：测试验证 | 运行 verify.py |
| 验证通过，"用户批准"为 ⏳ | 阶段4：等待批准 | 请求用户批准 |
| 用户已批准 | 阶段5：需求归档 | 运行 archive.py |

## 快速决策表

| 你听到... | 阶段 | 操作 |
|-----------|------|------|
| "我想做 X" / "添加功能" | 阶段1 | writing-design |
| "设计写好了，帮我看看" | 阶段1 | review-design |
| "设计审查通过了" | 阶段1 | 请求用户批准 |
| "设计批准了" | 阶段2 | 任务拆解 |
| "计划做好了，开始做" | 阶段3 | 代码执行 |
| "做完了" | 阶段4 | 测试验证 |
| "验证通过了" | 阶段4 | 请求用户批准 |
| "批准了" | 阶段5 | 需求归档 |

## 核心规则

1. **任何开发任务始终先通过此技能路由**
2. **绝不跳过阶段**，即使任务"看起来很简单"
3. **阶段可以回退**：执行中发现问题可以回到计划阶段
4. **验证是强制性的**：没有验证证据就不能声称完成
5. **宣布阶段**："阶段 [N]：[名称]"

## 防跑偏检查

**检查时机：**
- 开始每个任务前
- 每完成一个子功能后
- 遇到问题时

**检查清单：**
- [ ] 我当前在做什么任务？
- [ ] 这个任务的目标是什么？
- [ ] 我的改动是否符合原始设计？
- [ ] 我是否在解决原始问题？

## Git 分支规则

| 操作 | 目标分支 |
|------|----------|
| 日常开发提交 | `develop` |
| 归档完成 | `develop` |
| 合并到 main | PR |

**分支策略详情：** [参考文档](./references/branching-strategy.md)

## 文件结构

```
vibe-coding/
├── SKILL.md                    ← 本文件（主入口路由器）
├── README.md                   ← 项目文档
├── scripts/
│   ├── design.py               ← 阶段1：需求分析
│   ├── plans.py                ← 阶段2：任务拆解
│   ├── execute.py              ← 阶段3：代码执行
│   ├── verify.py               ← 阶段4：测试验证
│   └── archive.py              ← 阶段5：需求归档
├── initialize/                 ← 首次启动子技能
├── writing-design/             ← 阶段1子技能
├── review-design/              ← 阶段1子技能
├── task-breakdown/             ← 阶段2子技能
├── test-driven-development/    ← 阶段3子技能
├── debugging-and-verification/ ← 阶段4子技能
├── references/                 ← 参考文档
└── assets/                     ← 资源文件
```

## 参考资源

- [`references/principles.md`](references/principles.md) - 开发原则详解（10条核心原则）
- [`references/workflow-guide.md`](references/workflow-guide.md) - 五阶段工作流详细指南
- [`references/branching-strategy.md`](references/branching-strategy.md) - Git 分支策略
- [`writing-design/SKILL.md`](writing-design/SKILL.md) - 需求调研子技能
- [`review-design/SKILL.md`](review-design/SKILL.md) - 设计审查子技能
- [`test-driven-development/SKILL.md`](test-driven-development/SKILL.md) - TDD 子技能
- [`debugging-and-verification/SKILL.md`](debugging-and-verification/SKILL.md) - 验证调试子技能