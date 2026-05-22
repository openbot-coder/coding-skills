---
version: 0.7.0
name: vibe-coding
design-pattern: pipeline
description: "轻量级 AI 编程技能，管理完整的开发全生命周期。当开始任何开发任务、功能实现或 Bug 修复时使用，或用户说「开始开发」「加功能」「修 bug」「写代码」时触发。五阶段工作流：需求分析 → 任务拆解 → 代码执行 → 测试验证 → 需求归档。"
---

# Vibe Coding

## 概述

**所有开发任务首先进入这里。** 识别当前阶段并路由到适当的操作。

> **参考文档**：
> - [开发原则](./references/PRINCIPLES.md)
> - [反模式](./references/ANTI-PATTERNS.md)
> - [Git规则](./references/GIT-RULES.md)
> - [分支策略](./references/branching-strategy.md)
> - [工作流指南](./references/workflow-guide.md)
> - [自我升级指南](./evolution/EVOLUTION-GUIDE.md) ← 基于 AHE 论文实现

## 🔴 硬性约束（绝对禁止违反）

| 约束 | 说明 |
|------|------|
| ❌ **禁止绕过 review-design** | 阶段1 必须完成 design 审查，禁止跳过审核直接给用户确认 |
| ❌ **禁止跳过覆盖率检查** | 提交代码前必须确认覆盖率 100% |
| ❌ **禁止跳过测试用例检查** | 提交前必须确认正例 + 反例 + 边界值 完整 |
| ❌ **禁止跳过规范编写** | SDD 模式：必须先写规范再写代码 |

## 防跑偏检查

**每次响应前必须自检：**

```
[ ] 我当前在做什么任务？任务目标是什么？
[ ] 我的输出是否在解决这个任务？
[ ] 是否违反了硬性约束？
[ ] 是否发现新问题？→ 记录到 TODO，不在本任务处理
```

---

## 五阶段工作流

```
需求分析 → 任务拆解 → 代码执行 → 测试验证 → 需求归档
```

| 阶段 | 脚本/技能 | 时机 | 输出 |
|------|-----------|------|------|
| 1. 需求分析 | writing-design + **review-design** | 需求出现 | `{name}-design.md` |
| 2. 任务拆解 | `python scripts/plans.py` | 设计已批准 | `{name}-progress.md` |
| 3. 代码执行 | `python scripts/execute.py` | 计划已定 | 更新任务状态 |
| 4. 测试验证 | `python scripts/verify.py` | 编码完成 | 验证结果 |
| 5. 需求归档 | `python scripts/archive.py` | 用户批准 | 归档到 `archive/` |

---

## 阶段详解

### 阶段1：需求分析

```
writing-design → review-design → 用户批准
```

> ⚠️ **强制规则：禁止绕过 review-design**
>
> ❌ 错误做法：写完 design.md 直接给用户确认
> ✅ 正确做法：必须经过 review-design 审查 → 修改 → 再审查 → 通过后才能用户确认

**writing-design：**
- 探索项目上下文，理解真正的问题
- 通过提问澄清需求、约束和成功标准
- 提出 2-3 种方案并分析权衡
- 记录到 `{name}-design.md`

**review-design：**
- 审查设计完整性（目标、背景、成功标准、范围）
- 审查架构质量（模块划分、接口设计、深度评估）
- **审查通过后**才能请求用户批准

### 阶段2：任务拆解

**脚本：** `python scripts/plans.py --name <名称>`

- 将设计文档拆解为可执行的任务清单
- 每个任务约 10 个功能点
- 明确依赖关系和验证方式

### 阶段3：代码执行（SDD 规范驱动开发）

**脚本：** `python scripts/execute.py --name <名称> --task <编号> --action <操作>`

#### SDD 流程

```
规范（Spec） → 实现 → 测试 → 重构
```

**❌ 禁止行为：**
- 直接写代码，不写规范
- 先写实现，后补规范

**✅ 正确流程：**
1. **写规范**：定义接口签名、行为约定、边界条件
2. **实现**：按规范编写代码
3. **测试**：正例 + 反例 + 边界值
4. **重构**：如有需要

### 阶段3.5：单元测试

> ⚠️ **强制规则：覆盖率 100%，测试用例三维度完整**

所有任务完成后，进入**单元测试阶段**：

| 检查项 | 要求 | 状态 |
|--------|------|------|
| 正例测试 | 正常输入 → 正常输出 | ❌ 未覆盖 |
| 反例测试 | 无效输入 → 正确错误响应 | ❌ 未覆盖 |
| 边界值测试 | 最小值、零值、空值、最大值 | ❌ 未覆盖 |
| 覆盖率 | **100%** | ❌ 未达标 |

**未覆盖行必须以 `# UNCOVERED: [原因]` 标注**

> 详细 SDD 开发说明见 [sdd-unit-development 子技能](./sdd-unit-development/SKILL.md)

### 阶段4：测试验证

**脚本：** `python scripts/verify.py --name <名称>`

**验证通过标准：**
- ✅ 单元测试覆盖率 **100%**
- ✅ 正例 + 反例 + 边界值 **三维度完整**
- ✅ 所有单元测试通过
- ✅ 集成测试全部通过

**提交前检查清单：**
```
[ ] 覆盖率报告已生成
[ ] 正例测试用例：N 个
[ ] 反例测试用例：N 个
[ ] 边界值测试用例：N 个
[ ] 未覆盖行已标注 # UNCOVERED
```

### 阶段5：需求归档

**脚本：** `python scripts/archive.py --name <名称>`

- 提交 Git 到 `develop`
- 移动变更目录到 `archive/`
- 创建 PR 合并到 `main`

---

## 首次启动

> 详细规则见 [initialize 子技能](./initialize/SKILL.md)

```bash
# 检查工具
python scripts/tools_check.py

# 检查 docs/vibe-coding/ 是否存在
# 不存在 → 绿地项目初始化
# 存在 → 棕地项目初始化
```

## 状态判断

| 文件状态 | 当前阶段 | 下一步 |
|----------|----------|--------|
| `{name}-design.md` 不存在 | 阶段1：writing-design | 开始需求调研 |
| `{name}-design.md` 存在，`Agent审查`为 ⏳ | 阶段1：review-design | **审查设计（禁止跳过）** |
| 设计审查通过，`用户批准`为 ⏳ | 阶段1：等待批准 | 请求用户批准 |
| 设计已批准 | 阶段2：任务拆解 | 运行 plans.py |
| 阶段2完成，有未完成任务 | 阶段3：SDD 代码执行 | 运行 execute.py |
| 所有任务完成 | 阶段3.5：单元测试 | **覆盖率100% + 三维度检查** |
| 测试通过 | 阶段4：集成测试 | 运行 verify.py |
| 验证通过，`用户批准`为 ⏳ | 阶段4：等待批准 | 请求用户批准 |
| 用户已批准 | 阶段5：需求归档 | 运行 archive.py |

## 快速决策表

| 你听到... | 阶段 | 操作 |
|-----------|------|------|
| "我想做 X" / "添加功能" | 1 | writing-design |
| "设计写好了" | 1 | **review-design（禁止跳过）** |
| "设计审查通过了" | 1 | 请求用户批准 |
| "设计批准了" | 2 | 任务拆解 |
| "计划做好了，开始做" | 3 | SDD 代码执行 |
| "实现完了" | 3.5 | **单元测试（覆盖率100%）** |
| "单元测试写完了" | 4 | 集成测试验证 |
| "批准了" | 5 | 需求归档 |

## 文件结构

```
vibe-coding/                           ← 技能目录
├── SKILL.md                           ← 主入口路由器
├── README.md
├── initialize/
├── writing-design/
├── review-design/
├── sdd-unit-development/
├── debugging-and-verification/
├── evolution/                         ← 自我升级模块
│   ├── evolve.py                     ← 进化主脚本
│   ├── collect-evidence.py           ← 证据收集
│   ├── analyze-trajectories.py       ← 轨迹分析
│   ├── change-manifest-template.md   ← 变更清单模板
│   └── EVOLUTION-GUIDE.md           ← 进化指南
├── references/                        ← 参考文档
└── scripts/

# 项目目录
{项目根目录}/
└── docs/
    └── vibe-coding/
        ├── .initialized               ← 初始化标记
        ├── CONTEXT.md                 ← 【项目级】领域术语
        ├── {project-name}-design.md  ← 【项目级】项目设计
        └── changes/
            ├── {name}/              ← 变更目录
            │   ├── {name}-design.md
            │   ├── {name}-survey-records.md
            │   └── {name}-progress.md
            └── archive/              ← 已归档变更
```

## 🔄 自我升级（基于 AHE 论文）

vibe-coding 通过三个可观测性支柱实现自我升级，详见 [EVOLUTION-GUIDE.md](./evolution/EVOLUTION-GUIDE.md)。

### 进化循环

```
收集证据 → 分析轨迹 → 变更决策 → 验证结果
```

### 触发条件

| 类型 | 触发条件 |
|------|----------|
| **手动触发** | `python evolution/evolve.py --project-dir . --action init` |
| **自动触发** | 连续 3 次相同类型错误时自动触发 |

### 证据收集时机

- ✅ 每次任务开始/完成时
- ✅ 每次阶段切换时
- ✅ 每次遇到问题时
- ✅ 每次规则修改时