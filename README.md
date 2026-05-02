# coding-skills
开发全生命周期管理

一套面向 AI 编程助手的开发生命周期技能体系。

## 概述

`coding-skills` 是一套结构化的 AI Agent 技能（Skill）集合，旨在让 AI 编程助手遵循严谨的软件开发生命周期，从构思、计划到执行、调试、审查和交付，每个阶段都有对应的技能和明确的工作流。

**核心理念：** 在正确的时间使用正确的技能，绝不跳过阶段。

## 开发原则

所有技能贯穿以下四条不可妥协的原则：

1. **先思考再编码** — 明确假设，暴露困惑，呈现多种理解，不确定就提问
2. **简洁优先** — 用最少的代码解决问题，不做投机性编码，不添加未要求的功能
3. **精准修改** — 只动必须动的，只清理自己弄乱的，匹配现有风格
4. **目标驱动执行** — 定义可验证的成功标准，循环直到验证通过

### 工程原则

5. **Hyrum's Law** — 行为的每个细节都是公共 API，即使"未记录的行为"也会被依赖
6. **Chesterton's Fence** — 不要删除你不理解的东西，先问"为什么这是这样？"
7. **测试金字塔** — 70% 单元测试 + 20% 集成测试 + 10% E2E 测试
8. **Beyoncé 规则** — 如果你喜欢一个工具，就该贡献保护它（文档、测试、bug修复）
9. **左移原则** — 越早发现问题，修复成本越低
10. **二八定律** — 80% 的问题来自 20% 的代码区域，重点审查复杂逻辑

## 开发生命周期

```
构思 → PRD与设计 → 计划 → 执行 → 调试 → 审查 → 验证 → 收尾
 1        2        3      4      5      6      7      8
```

| 阶段 | 技能 | 时机 |
|------|------|------|
| 1. 构思 | `brainstorming` | 尚无设计，需求不明确 |
| 2. PRD与设计 | `writing-prd-and-design` | 构思完成，需要 PRD 和详细设计 |
| 3. 实施计划 | `writing-plans` | 设计已批准，尚无实施计划 |
| 4. 执行 | `subagent-driven-development` / `executing-plans` / `dispatching-parallel-agents` | 计划已存在，需要实施 |
| 5. 调试 | `systematic-debugging` | 遇到 bug、错误或意外行为 |
| 6. 审查 | `requesting-code-review` / `receiving-code-review` | 代码已写，需要审查 |
| 7. 验证 | `verification-before-completion` | 即将声称完成 |
| 8. 收尾 | `finishing-a-development-branch` | 已验证，准备合并/关闭 |

**执行阶段辅助技能：**

| 技能 | 用途 |
|------|------|
| `test-driven-development` | TDD 纪律：先写测试，看它失败，写最少代码通过 |
| `using-git-worktrees` | 在 Git Worktree 中隔离开发 |
| `using-uv` | 使用 uv 管理 Python 包 |

## 快速决策

| 你听到... | 阶段 | 技能 |
|-----------|------|------|
| "构建 X" / "添加功能" / "创建" | 1 | brainstorming |
| "构思完成，写 PRD 和设计" | 2 | writing-prd-and-design |
| "设计已批准，做实施计划" | 3 | writing-plans |
| "按这个计划做" / "执行任务 N" | 4 | subagent-driven-development |
| "修复这个 bug" / "错误：..." | 5 | systematic-debugging |
| "审查这段代码" / "PR 反馈" | 6 | requesting/receiving-code-review |
| "完成了吗？" / "应该没问题了" | 7 | verification-before-completion |
| "合并这个" / "结束分支" | 8 | finishing-a-development-branch |

## 多工作流支持

本仓库提供两套互补的 AI 编程工作流：

### 1. 完整生命周期（8 阶段）

适用于需要严格流程管理的复杂项目：

```
构思 → PRD与设计 → 计划 → 执行 → 调试 → 审查 → 验证 → 收尾
  1        2        3      4      5      6      7      8
```

详见上方 [开发生命周期](#开发生命周期) 部分。

### 2. 轻量级工作流（5 阶段）

`vibe-coding/` 是一套轻量级开发工作流，参考 OpenSpec 设计理念：

```
需求分析 → 任务拆解 → 代码执行 → 测试验证 → 需求归档
```

**特点：**
- **零依赖**：仅使用 Python 标准库
- **跨平台**：Windows、macOS、Linux
- **AI 友好**：SKILL.md 作为路由器，自动按阶段引导

| 阶段 | 脚本 | 输出 |
|------|------|------|
| 1. 需求分析 | `design.py` | `{name}-design.md` |
| 2. 任务拆解 | `plans.py` | `{name}-progress.md` |
| 3. 代码执行 | `execute.py` | 更新任务状态 |
| 4. 测试验证 | `verify.py` | 验证结果 |
| 5. 需求归档 | `archive.py` | 归档到 archive/ |

详细文档见 [vibe-coding/README.md](vibe-coding/README.md)

## 项目结构

```
coding-skills/
├── SKILL.md                              ← 主入口：生命周期路由器
├── workflows/                            ← 子技能工作流文档
│   ├── brainstorming.md                   ← 阶段1：构思
│   ├── writing-prd-and-design.md         ← 阶段2：PRD与详细设计
│   ├── writing-plans.md                   ← 阶段3：实施计划
│   ├── subagent-driven-development.md     ← 阶段4：子代理驱动开发
│   ├── executing-plans.md                 ← 阶段4：批量执行计划
│   ├── dispatching-parallel-agents.md     ← 阶段4：并行代理调度
│   ├── test-driven-development.md         ← 阶段4：测试驱动开发
│   ├── using-git-worktrees.md             ← 阶段4：Git Worktree 隔离开发
│   ├── using-uv.md                        ← 阶段4：Python uv 包管理
│   ├── systematic-debugging.md            ← 阶段5：系统化调试
│   ├── requesting-code-review.md          ← 阶段6：请求代码审查
│   ├── receiving-code-review.md           ← 阶段6：处理审查反馈
│   ├── verification-before-completion.md  ← 阶段7：完成前验证
│   └── finishing-a-development-branch.md   ← 阶段8：分支收尾
└── references/                           ← 辅助参考文件
    ├── python-async-patterns.md           ← Python 异步开发实战模式
    ├── requesting-code-review-code-reviewer.md          ← 代码审查者角色定义
    ├── subagent-driven-development-*.md                 ← 子代理角色提示词
    ├── systematic-debugging-*.md/.ts/.sh                ← 调试辅助工具与示例
    └── test-driven-development-testing-anti-patterns.md ← 测试反模式参考
```

## 反模式

- ❌ 不经设计直接编码
- ❌ 没有计划就实施
- ❌ 执行时跳过 TDD
- ❌ 不运行验证就声称"完成"
- ❌ 不经代码审查就合并
- ❌ "这太简单了不需要设计"

## 支持的工具平台

`coding-skills` 可在以下 AI 编程工具中使用：

| 工具 | 集成方式 | 状态 |
|------|----------|------|
| **Claude Code** | 通过 CLAUDE.md 加载系统提示 | ✅ |
| **Cursor** | 通过 .cursorrules 或 Custom Instructions | ✅ |
| **Windsurf** | 通过 Cascade Rules | ✅ |
| **GitHub Copilot** | 通过 Workspace Instructions | ✅ |
| **VS Code (Continue)** | 通过 instructions 配置 | ✅ |
| **Kiro IDE/CLI** | 通过系统提示 | ✅ |

### 通用集成方法

将主 SKILL.md 的内容添加到工具的系统提示或指令配置中：

1. 读取 `coding-skills/SKILL.md` 的完整内容
2. 添加到工具的系统提示开头
3. 确保工具在每次对话开始时加载此技能

### Claude Code 集成

在项目根目录创建 `CLAUDE.md`：

```markdown
# Claude Code 配置

你是一个遵循 structured coding-skills 的 AI 编程助手。

在开始任何编码任务前，先加载并遵循 coding-skills 技能体系：
- 阶段1：构思与设计 → brainstorming
- 阶段2：编写计划 → writing-plans
- ...（其他阶段）

详见 `.skills/coding-skills/SKILL.md`
```

## 参考项目

- [andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) — Andrej Karpathy 风格的 AI 编程技能
- [superpowers](https://github.com/obra/superpowers) — AI Agent 超能力技能集合
- [agent-skills](https://github.com/addyosmani/agent-skills) — Addy Osmani 的 AI Agent 技能集合（斜杠命令、专家角色定义）

## Changelog

### v0.3.0 (2026-04-28)

**新功能：**
- 新增阶段：PRD 与详细设计（阶段2）
- 新增技能 `writing-prd-and-design`：将需求转化为 PRD 文档和详细设计文档
- 优化工作流程：brainstorming → PRD与设计 → 实施计划 → 执行

**流程改进：**
- 阶段数从 7 扩展到 8
- PRD 回答"做什么"，详细设计回答"怎么做"，实施计划回答"先做什么"

### v0.2.0 (2026-04-27)

**新功能：**
- 添加版本号 `version: 0.2.0` 到 SKILL.md
- 添加 6 条工程原则（Hyrum's Law、Chesterton's Fence、测试金字塔、Beyoncé 规则、左移原则、二八定律）
- 添加 8 条借口反驳表
- 添加平台集成指南（Claude Code、Cursor、Windsurf、GitHub Copilot 等）

**参考项目：**
- 添加 agent-skills 到参考项目列表

### v0.1.0 (2026-04-26)

- 初始版本发布
- 完成开发生命周期 7 阶段技能体系
- 包含 13 个工作流技能和 15 个辅助参考文件
- 完善 README.md 项目文档

## License

[MIT](LICENSE)
