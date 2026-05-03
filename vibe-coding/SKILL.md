---
version: 0.6.0
name: vibe-coding
description: "轻量级 AI 编程技能。五阶段工作流：需求分析 → 任务拆解 → 代码执行 → 测试验证 → 需求归档。"
---

# Vibe Coding

## 概述

**所有开发任务首先进入这里。** 识别当前阶段并路由到适当的操作。

> **参考文档**：
> - [开发原则](../references/PRINCIPLES.md) — 核心原则和工程原则
> - [反模式](../references/ANTI-PATTERNS.md) — 反模式、借口反驳、警告信号
> - [Git规则](../references/GIT-RULES.md) — 分支策略和提交规范
> - [架构设计原则](../references/ARCHITECTURE-PRINCIPLES.md) — 术语、原则、检查点

## 防跑偏检查

编码过程中，必须在以下时机检查是否跑偏：

- 开始每个任务前
- 每完成一个子功能后
- 遇到问题时

```
[ ] 我当前在做什么任务？
[ ] 我的改动是否符合原始设计？
[ ] 我是否在解决原始问题，而不是发现新问题就去做？
```

## 五阶段工作流

```
需求分析 → 任务拆解 → 代码执行 → 测试验证 → 需求归档
```

| 阶段 | 脚本/技能 | 时机 | 输出 |
|------|-----------|------|------|
| 1. 需求分析 | writing-design + review-design | 需求出现 | `{name}-design.md` |
| 2. 任务拆解 | `python scripts/plans.py` | 设计已批准 | `{name}-progress.md` |
| 3. 代码执行 | `python scripts/execute.py` | 计划已定 | 更新任务状态 |
| 4. 测试验证 | `python scripts/verify.py` | 编码完成 | 验证结果 |
| 5. 需求归档 | `python scripts/archive.py` | 用户批准 | 归档到 `archive/` |

## 阶段详解

### 阶段1：需求分析

**子流程：** `writing-design → review-design` 循环直到通过

**writing-design：**
- 探索项目上下文，理解真正的问题
- 通过提问澄清需求、约束和成功标准
- 提出 2-3 种方案并分析权衡
- 记录到 `{name}-design.md` 和 `{name}-survey-records.md`

**review-design：**
- 审查设计完整性（目标、背景、成功标准、范围）
- 审查架构质量（模块划分、接口设计、深度评估）
- 与调研记录一致性检查
- 循环修改直到通过 → 请求用户批准

### 阶段2：任务拆解

**脚本：** `python scripts/plans.py --name <名称>`

- 将设计文档拆解为可执行的任务清单
- 每个任务 10~20 个功能点
- 明确依赖关系和验证方式

### 阶段3：代码执行

**脚本：** `python scripts/execute.py --name <名称> --task <编号> --action <操作>`

**TDD 铁律：** 没有失败的测试就不能写生产代码

**红-绿-重构循环：**
```
红（写失败测试）→ 绿（最少代码通过）→ 重构（清理）→ 下一个
```

**覆盖率要求：** 单元测试覆盖率目标 **100%**

### 阶段4：测试验证

**脚本：** `python scripts/verify.py --name <名称>`

- 系统集成测试
- 验证通过后请求用户批准

**验证通过标准：**
- 单元测试覆盖率 100%
- 集成测试通过
- 测试用例充分完整

### 阶段5：需求归档

**脚本：** `python scripts/archive.py --name <名称>`

- 提交 Git 到 `develop`
- 移动变更目录到 `archive/`
- 创建 PR 合并到 `main`

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

通过检查文件存在性和状态判断当前阶段：

| 文件状态 | 当前阶段 | 下一步 |
|----------|----------|--------|
| `{name}-design.md` 不存在 | 阶段1：writing-design | 开始需求调研 |
| `{name}-design.md` 存在，`Agent审查`为 ⏳ | 阶段1：review-design | 审查设计 |
| 设计审查通过，`用户批准`为 ⏳ | 阶段1：等待批准 | 请求用户批准 |
| 设计已批准 | 阶段2：任务拆解 | 运行 plans.py |
| 阶段2完成，有未完成任务 | 阶段3：代码执行 | 运行 execute.py |
| 所有任务完成 | 阶段4：测试验证 | 运行 verify.py |
| 验证通过，`用户批准`为 ⏳ | 阶段4：等待批准 | 请求用户批准 |
| 用户已批准 | 阶段5：需求归档 | 运行 archive.py |

## 快速决策表

| 你听到... | 阶段 | 操作 |
|-----------|------|------|
| "我想做 X" / "添加功能" | 1 | writing-design |
| "设计写好了，帮我看看" | 1（子流程） | review-design |
| "设计审查通过了" | 1（子流程） | 请求用户批准 |
| "设计批准了" | 2 | 任务拆解 |
| "计划做好了，开始做" | 3 | 代码执行 |
| "做完了" | 4 | 测试验证 |
| "批准了" | 5 | 需求归档 |

## 文件结构

```
vibe-coding/                           ← 技能目录
├── SKILL.md                           ← 主入口路由器
├── README.md
├── initialize/
├── writing-design/
├── review-design/
├── test-driven-development/
├── debugging-and-verification/
├── references/                        ← 参考文档
│   ├── PRINCIPLES.md                 ← 开发原则
│   ├── ANTI-PATTERNS.md             ← 反模式和借口反驳
│   ├── GIT-RULES.md                 ← Git 分支规则
│   ├── ARCHITECTURE-*.md            ← 架构设计文档
│   ├── CONTEXT-FORMAT.md            ← 领域术语格式
│   └── SURVEY-RECORDS.md            ← 调研记录格式
└── scripts/

# 项目目录
{项目根目录}/
└── docs/
    └── vibe-coding/
        ├── .initialized               ← 初始化标记
        ├── CONTEXT.md                 ← 【项目级】领域术语
        ├── {project-name}-design.md  ← 【项目级】项目设计
        ├── graphify-out/              ← graphify 输出（由 graphify 命令生成）
        │   ├── graph.html            ← 交互式图谱
        │   ├── GRAPH_REPORT.md      ← 分析报告
        │   ├── graph.json           ← 持久化图数据
        │   └── cache/               ← SHA256 缓存
        └── changes/
            ├── {name}/              ← 变更目录
            │   ├── {name}-design.md
            │   ├── {name}-survey-records.md
            │   └── {name}-progress.md
            └── archive/              ← 已归档变更
```

## 归档规则

归档时移动**整个变更目录**到 `archive/`，项目级文件保留：

```
归档前                              归档后
changes/add-dark-mode/            changes/add-dark-mode/  ← 移动整个目录
├── design.md                     ├── design.md
├── survey-records.md             ├── survey-records.md
└── progress.md                   └── progress.md

# 保留在原位：
docs/vibe-coding/CONTEXT.md        ← 项目级，不归档
```
