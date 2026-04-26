# coding-skills
教AI Agent 编写代码的skills

教 AI Agent 编写代码的 Skills — 一套面向 AI 编程助手的开发生命周期技能体系。

## 概述

`coding-skills` 是一套结构化的 AI Agent 技能（Skill）集合，旨在让 AI 编程助手遵循严谨的软件开发生命周期，从构思、计划到执行、调试、审查和交付，每个阶段都有对应的技能和明确的工作流。

**核心理念：** 在正确的时间使用正确的技能，绝不跳过阶段。

## 开发原则

所有技能贯穿以下四条不可妥协的原则：

1. **先思考再编码** — 明确假设，暴露困惑，呈现多种理解，不确定就提问
2. **简洁优先** — 用最少的代码解决问题，不做投机性编码，不添加未要求的功能
3. **精准修改** — 只动必须动的，只清理自己弄乱的，匹配现有风格
4. **目标驱动执行** — 定义可验证的成功标准，循环直到验证通过

## 开发生命周期

```
构思 → 计划 → 执行 → 调试 → 审查 → 验证 → 收尾
 1      2      3      4      5      6      7
```

| 阶段 | 技能 | 时机 |
|------|------|------|
| 1. 构思 | `brainstorming` | 尚无设计，需求不明确 |
| 2. 计划 | `writing-plans` | 设计已批准，尚无实施计划 |
| 3. 执行 | `subagent-driven-development` / `executing-plans` / `dispatching-parallel-agents` | 计划已存在，需要实施 |
| 4. 调试 | `systematic-debugging` | 遇到 bug、错误或意外行为 |
| 5. 审查 | `requesting-code-review` / `receiving-code-review` | 代码已写，需要审查 |
| 6. 验证 | `verification-before-completion` | 即将声称完成 |
| 7. 收尾 | `finishing-a-development-branch` | 已验证，准备合并/关闭 |

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
| "这是设计，实现它" | 2 | writing-plans |
| "按这个计划做" / "执行任务 N" | 3 | subagent-driven-development |
| "修复这个 bug" / "错误：..." | 4 | systematic-debugging |
| "审查这段代码" / "PR 反馈" | 5 | requesting/receiving-code-review |
| "完成了吗？" / "应该没问题了" | 6 | verification-before-completion |
| "合并这个" / "结束分支" | 7 | finishing-a-development-branch |

## 项目结构

```
coding-skills/
├── SKILL.md                              ← 主入口：生命周期路由器
├── workflows/                            ← 子技能工作流文档
│   ├── brainstorming.md                   ← 阶段1：构思与设计
│   ├── writing-plans.md                   ← 阶段2：编写计划
│   ├── subagent-driven-development.md     ← 阶段3：子代理驱动开发
│   ├── executing-plans.md                 ← 阶段3：批量执行计划
│   ├── dispatching-parallel-agents.md     ← 阶段3：并行代理调度
│   ├── test-driven-development.md         ← 阶段3：测试驱动开发
│   ├── using-git-worktrees.md             ← 阶段3：Git Worktree 隔离开发
│   ├── using-uv.md                        ← 阶段3：Python uv 包管理
│   ├── systematic-debugging.md            ← 阶段4：系统化调试
│   ├── requesting-code-review.md          ← 阶段5：请求代码审查
│   ├── receiving-code-review.md           ← 阶段5：处理审查反馈
│   ├── verification-before-completion.md  ← 阶段6：完成前验证
│   └── finishing-a-development-branch.md  ← 阶段7：分支收尾
└── references/                           ← 辅助参考文件
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

## 参考项目

- [andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) — Andrej Karpathy 风格的 AI 编程技能
- [superpowers](https://github.com/obra/superpowers) — AI Agent 超能力技能集合

## Changelog

### v0.1.0 (2026-04-26)

- 初始版本发布
- 完成开发生命周期 7 阶段技能体系
- 包含 13 个工作流技能和 15 个辅助参考文件
- 完善 README.md 项目文档

## License

[MIT](LICENSE)
