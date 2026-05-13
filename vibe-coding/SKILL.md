***
---

version: 0.8.0
name: vibe-coding
description: "轻量级 AI 编程技能。产品设计文档驱动：design.md 作为唯一真相源，变更直接修改，changelog 独立追溯，git tag 同步版本。"
-------------------------------------------------------------------------------------------

# Vibe Coding — 产品设计驱动开发工作流

## 概述

所有开发任务首先进入这里。此技能识别当前开发阶段并路由到适当的操作。永远不要直接跳到编码 — 始终先确定阶段。

**核心原则：** 设计文档是项目的唯一真相源（SSOT），AI 凭此可重建整个项目。

## 两种模式

### 模式 A：中央 design.md 模式（推荐）

一个项目维护一份 `docs/design.md`，所有需求变更直接在其上修改。

```
docs/
  design.md          ← 产品设计（唯一真相源）
  changelog.md       ← 变更历史（独立追溯）
```

- 每次变更：直接修改 design.md + 版本号递增 + changelog.md 追加记录
- AI 重建项目只需读 `design.md` 一个文件
- git tag 与 design.md 版本号同步

### 模式 B：独立变更文档模式（旧模式，向后兼容）

每个需求一个独立的 `{name}-design.md`。

```
docs/vibe-coding/changes/
  add-dark-mode/
    add-dark-mode-design.md
    add-dark-mode-progress.md
```

## 整体流程结构

```
阶段0: 项目初始化（仅一次） → design.md 就绪 → 阶段1-5 变更循环（每需求一次）
```

## 阶段0：项目初始化

**目的：** 创建或领养项目，生成 `design.md` 作为后续变更的唯一真相源。**只在首次运行一次。**

| 项目类型 | 命令 | 自动完成 |
|---------|------|---------|
| **绿地**（全新空白目录） | `--init --name X --lang python --desc Y` | 骨架+design+changelog+git |
| **棕地**（已有代码） | `--adopt --name X` | 扫描+预填充design+changelog+git |

### 模式 A（推荐）

```bash
# 绿地：从零创建完整项目骨架 + design.md (v0.1.0)
#   --lang 支持: python | javascript | typescript | rust | go
python scripts/design.py --init --name "my-project" --lang python --desc "项目描述"

# 棕地：扫描已有代码，自动检测项目名/版本/语言/框架
python scripts/design.py --adopt

# 棕地：指定项目名和起始版本
python scripts/design.py --adopt --name "my-project" --version 1.0.0
```

### 模式 B（旧模式，向后兼容）

```bash
python scripts/design.py --name <变更名称> --desc "<简要描述>"
```

---

## 五阶段变更循环（每需求一次）

design.md 就绪后，每次需求变更都走以下循环：

```
阶段1: 需求分析 → 阶段2: 任务拆解 → 阶段3: 代码执行 → 阶段4: 测试验证 → 阶段5: 需求归档
```

| 阶段 | 模式A 命令 | 模式B 命令 | 输出 |
|------|-----------|-----------|------|
| 1. 需求分析 | `--change` | `--name <名称>` | design.md 更新 + changelog |
| 2. 任务拆解 | `plans.py --name <名称>` | `plans.py --name <名称>` | {name}-progress.md |
| 3. 代码执行 | `execute.py` | `execute.py` | 更新 progress.md |
| 4. 测试验证 | `verify.py` | `verify.py` | progress.md |
| 5. 需求归档 | `archive.py`（自动打tag） | `archive.py` | git tag + 归档 |

## 阶段路由

### 阶段1：需求分析

**前提：** `docs/design.md` 已存在（阶段0已完成）

```bash
# 记录需求变更：先编辑 design.md，然后运行
python scripts/design.py --change --desc "新增XX需求" --bump minor

# 版本回退（不算是变更，但在此功能内）
python scripts/design.py --rollback --version 1.0.0
```

**子流程：** `writing-design → review-design → [用户批准] → 阶段2`

### 阶段2：任务拆解

**操作：**
1. 运行 `python scripts/plans.py --name <变更名称>`
2. 在 `{name}-progress.md` 中填充计划概述和任务清单
3. 确认完整后进入阶段3

### 阶段3：代码执行

**TDD 模式：** [详细规则](./test-driven-development/SKILL.md)

### 阶段4：测试验证

**操作：**
1. 开始验证：`python scripts/verify.py --name <名称> --action start`
2. 进行系统集成测试
3. 验证通过后请求用户批准

### 阶段5：需求归档

**操作：**
1. 运行 `python scripts/archive.py --name <变更名称>`
2. 脚本自动将 design.md 版本号用于 git tag
3. 创建 PR 将 develop 合并到 main

## 版本管理（模式 A 核心机制）

### 版本号规则（semver）

```
major.minor.patch
  │    │    │
  │    │    └─ bug fix / 微调（不改设计）
  │    └────── 新增需求 / 修改设计
  └─────────── 架构重构 / 不兼容变更
```

### 变更流程

1. 修改 `design.md` 对应章节
2. 运行 `python scripts/design.py --change --desc "描述" --bump minor`
3. 自动更新：版本号、最后更新日期、changelog.md
4. 自动 git commit

### 版本回退

| 场景 | 命令 | 效果 |
|------|------|------|
| 回退设计+代码 | `--rollback --version 1.0.0` | 从 git tag 恢复 design.md + src/ |
| 仅回退设计 | `--rollback --version 1.0.0 --design-only` | 只恢复 docs/ |
| 仅回退代码 | `--rollback --version 1.0.0 --code-only` | 只恢复 src/ |

### Changelog 管理

```bash
# 列出所有版本
python scripts/changelog.py --list

# 显示当前版本
python scripts/changelog.py --current

# 标记版本状态
python scripts/changelog.py --mark 1.1.0 --state done
```

## 状态判断

| 文件状态 | 当前阶段 | 下一步 |
|----------|----------|--------|
| `design.md` 不存在，项目为空 | **阶段0**：绿地初始化 | `--init` |
| `design.md` 不存在，有代码 | **阶段0**：棕地领养 | `--adopt` |
| `design.md` 存在，有新变更 | **阶段1**：设计更新 | `--change` |
| `design.md` 已批准 | **阶段2**：任务拆解 | `plans.py` |
| 阶段2完成，有未完成任务 | **阶段3**：代码执行 | `execute.py` |
| 所有任务完成 | **阶段4**：测试验证 | `verify.py` |
| 验证通过 | **阶段5**：需求归档 | `archive.py` |

## 快速决策表

| 你听到... | 阶段 | 操作 |
|-----------|------|------|
| "新项目" / "从零开始" | **阶段0** 初始化 | `--init` |
| "已有项目" / "接手"/"棕地" | **阶段0** 初始化 | `--adopt` |
| "新增功能" / "修改需求" | **阶段1** 需求分析 | `--change` |
| "回退到上个版本" | 版本管理 | `--rollback` |
| "设计写好了，帮我看看" | **阶段1** 需求分析 | review-design |
| "设计批准了" | **阶段2** 任务拆解 | 任务拆解 |
| "计划做好了，开始做" | **阶段3** 代码执行 | 代码执行 |
| "做完了" | **阶段4** 测试验证 | 测试验证 |
| "验证通过了" | **阶段4** 测试验证 | 请求用户批准 |
| "批准了" | **阶段5** 需求归档 | 需求归档 |

## 核心规则

1. **任何开发任务始终先通过此技能路由**
2. **绝不跳过阶段**，即使任务"看起来很简单"
3. **阶段可以回退**：执行中发现问题可以回到计划阶段
4. **验证是强制性的**：没有验证证据就不能声称完成
5. **宣布阶段**："阶段 [N]：[名称]"
6. **design.md 是唯一真相源**：变更直接在其上修改，不是创建新文件

## 防跑偏检查

**检查时机：**
- 开始每个任务前
- 每完成一个子功能后
- 遇到问题时

**检查清单：**
- [ ] 我当前在做什么任务？
- [ ] 这个任务的目标是什么？
- [ ] 我的改动是否符合 design.md 的设计？
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
│   ├── common.py               ← 公共工具模块（项目根目录查找、Git 操作、版本管理等）
│   ├── design.py               ← 阶段0+1：初始化(--init/--adopt) + 需求分析(--change/--rollback)；模式B：--name
│   ├── changelog.py            ← Changelog 管理工具（模式A专用）
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

### 项目文件结构（模式 A 推荐布局）

```
project-root/
├── docs/
│   ├── design.md               ← 产品设计文档（唯一真相源）
│   └── changelog.md            ← 变更历史
├── src/                        ← 源代码
├── tests/                      ← 测试代码
└── ...
```

### scripts/common.py 公共模块

提供所有脚本共享的工具函数：

| 函数 | 说明 |
|------|------|
| `setup_unicode_output()` | 解决 Windows 控制台 Unicode 输出问题 |
| `find_project_root()` | 从当前目录向上查找项目根目录 |
| `get_changes_dir()` | 获取 changes 目录路径 |
| `get_docs_dir()` | 获取 docs 目录路径（模式 A） |
| `run_git_command()` | 执行 git 命令 |
| `ensure_on_develop_branch()` | 确保当前在 develop 分支 |
| `git_add_and_commit()` | 执行 git add . 和 git commit |
| `is_git_repo()` | 检查目录是否为 Git 仓库 |
| `has_pending_changes()` | 检查是否有未提交的更改 |
| `read_version()` | 读取 design.md 版本号 |
| `bump_version()` | 递增 semver 版本号 |
| `update_version_in_design()` | 更新 design.md 版本号 |
| `update_last_updated()` | 更新 design.md 最后更新日期 |
| `get_git_tags()` | 获取所有 git tag |
| `find_tag_for_version()` | 查找版本对应的 git tag |
| `rollback_files_from_tag()` | 从 git tag 恢复文件 |

## 参考资源

- [`references/principles.md`](references/principles.md) - 开发原则详解（10条核心原则）
- [`references/workflow-guide.md`](references/workflow-guide.md) - 五阶段工作流详细指南
- [`references/branching-strategy.md`](references/branching-strategy.md) - Git 分支策略
- [`writing-design/SKILL.md`](writing-design/SKILL.md) - 需求调研子技能
- [`review-design/SKILL.md`](review-design/SKILL.md) - 设计审查子技能
- [`test-driven-development/SKILL.md`](test-driven-development/SKILL.md) - TDD 子技能
- [`debugging-and-verification/SKILL.md`](debugging-and-verification/SKILL.md) - 验证调试子技能