# coding-skills

轻量级 AI 编程技能系统。

## 概述

`coding-skills` 是一套轻量级 AI 编程工作流，核心理念：**先想清楚再动手，每一步都有据可查**。

```
需求分析 → 任务拆解 → 代码执行 → 测试验证 → 需求归档
```

## 特点

- **零依赖**：仅使用 Python 标准库
- **跨平台**：Windows、macOS、Linux
- **轻量级**：5 个脚本 + 1 个 SKILL.md，上手即会
- **AI 友好**：SKILL.md 作为路由器，AI 助手加载后自动按阶段引导

## 安装

将 `vibe-coding/` 目录复制到项目中即可使用：

```bash
cp -r vibe-coding/ your-project/.vibe-coding/
```

## 快速开始

### 阶段 1：需求分析

```bash
python scripts/design.py --name add-dark-mode --desc "添加暗色模式支持"
```

编辑生成的 `docs/vibe-coding/changes/add-dark-mode/add-dark-mode-design.md`，填充目标、背景和成功标准。

### 阶段 2：任务拆解

```bash
python scripts/plans.py --name add-dark-mode
```

编辑 `{name}-progress.md`，填充架构方案和任务清单。

### 阶段 3：代码执行

```bash
# 查看任务
python scripts/execute.py --name add-dark-mode --action list

# 开始任务
python scripts/execute.py --name add-dark-mode --task T1 --action start

# 完成任务
python scripts/execute.py --name add-dark-mode --task T1 --action done
```

### 阶段 4：测试验证

```bash
python scripts/verify.py --name add-dark-mode
```

### 阶段 5：需求归档

```bash
python scripts/archive.py --name add-dark-mode
```

变更目录将移动到 `docs/vibe-coding/changes/archive/add-dark-mode/`。

## 五阶段详解

| 阶段 | 命令 | 输入 | 输出 |
|------|------|------|------|
| 1. 需求分析 | `design.py --name <名称>` | 变更名称、描述 | `{name}-design.md` |
| 2. 任务拆解 | `plans.py --name <名称>` | `{name}-design.md` | `{name}-progress.md` |
| 3. 代码执行 | `execute.py --name <名称>` | `{name}-progress.md` | 更新任务状态 |
| 4. 测试验证 | `verify.py --name <名称>` | `{name}-progress.md` | 验证结果 |
| 5. 需求归档 | `archive.py --name <名称>` | 用户已批准 | 归档到 `archive/` |

## 开发原则

1. **先思考再编码** — 明确假设，暴露困惑，不确定就提问
2. **简洁优先** — 用最少的代码解决问题，不做投机性编码
3. **精准修改** — 只动必须动的，匹配现有风格
4. **目标驱动执行** — 定义可验证的成功标准

### 工程原则

5. **Hyrum's Law** — 行为的每个细节都是公共 API
6. **Chesterton's Fence** — 不要删除你不理解的东西
7. **测试金字塔** — 70% 单元测试 + 20% 集成测试 + 10% E2E 测试
8. **Beyoncé 规则** — 喜欢一个工具就该为它贡献
9. **左移原则** — 越早发现问题，修复成本越低
10. **二八定律** — 80% 的问题来自 20% 的代码区域

## 项目结构

```
coding-skills/
├── SKILL.md                    # 主入口：生命周期路由器
├── README.md                   # 项目文档
├── code-exploration/           # 代码探索子技能：修改前必须先理解代码
├── initialize/                 # 项目初始化子技能
├── writing-design/             # 需求调研子技能
├── review-design/              # 设计审查子技能
├── test-driven-development/    # TDD 子技能
└── debugging-and-verification/  # 验证调试子技能
```

## AI 集成

将 `SKILL.md` 的内容添加到 AI 编程助手的系统提示中，AI 将自动按五阶段工作流引导开发过程。

支持的 AI 编程工具：

| 工具 | 集成方式 |
|------|----------|
| Claude Code | 通过 CLAUDE.md 加载 |
| Cursor | 通过 .cursorrules 或 Custom Instructions |
| Windsurf | 通过 Cascade Rules |
| GitHub Copilot | 通过 Workspace Instructions |
| Trae IDE | 通过 Skill 加载 |

## 参考项目

- [OpenSpec](https://github.com/Fission-AI/OpenSpec) — 轻量级 AI 规格文档框架

## Changelog

### v0.4.0 (2026-05-02)

**新功能：**
- 重构为单一 vibe-coding 轻量级 5 阶段工作流
- 参考 OpenSpec 设计理念：`需求分析 → 任务拆解 → 代码执行 → 测试验证 → 需求归档`
- 提供 5 个 Python 脚本（design.py、plans.py、execute.py、verify.py、archive.py）
- 包含 5 个子技能：initialize、writing-design、review-design、test-driven-development、debugging-and-verification

**特点：**
- **零依赖**：仅使用 Python 标准库
- **跨平台**：Windows、macOS、Linux
- 强制用户批准门槛
- 内置防跑偏检查机制

### v0.3.0 (2026-04-28)

**新功能：**
- 新增阶段：PRD 与详细设计（阶段2）
- 新增技能 `writing-prd-and-design`：将需求转化为 PRD 文档和详细设计文档
- 优化工作流程：brainstorming → PRD与设计 → 实施计划 → 执行

### v0.2.0 (2026-04-27)

**新功能：**
- 添加版本号 `version: 0.2.0` 到 SKILL.md
- 添加 6 条工程原则（Hyrum's Law、Chesterton's Fence、测试金字塔、Beyoncé 规则、左移原则、二八定律）
- 添加 8 条借口反驳表
- 添加平台集成指南（Claude Code、Cursor、Windsurf、GitHub Copilot 等）

### v0.1.0 (2026-04-26)

- 初始版本发布
- 完成开发生命周期 7 阶段技能体系
- 包含 13 个工作流技能和 15 个辅助参考文件
- 完善 README.md 项目文档

## License

MIT
