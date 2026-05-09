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
- **模块化**：多个独立技能，按需使用
- **AI 友好**：SKILL.md 作为路由器，AI 助手加载后自动引导

## 核心技能

| 技能 | 用途 | 说明 |
|------|------|------|
| `code-exploration` | 代码探索 | 修改代码前先理解代码库 |
| `vibe-coding` | AI编程工作流 | 五阶段开发流程 |
| `scripts-coding` | 脚本编程规范 | 规范脚本开发流程 |

## 项目结构

```
coding-skills/
├── SKILL.md                    # 主入口：技能路由器
├── README.md                   # 项目文档
├── LICENSE                     # 许可证
├── .gitignore                  # Git 忽略配置

├── code-exploration/           # 代码探索子技能
│   └── SKILL.md                # 代码探索指南

├── vibe-coding/                # AI编程工作流
│   ├── SKILL.md                # 主入口：五阶段工作流
│   ├── README.md               # vibe-coding 文档
│   ├── scripts/                # 核心脚本工具
│   │   ├── design.py           # 阶段1：需求分析
│   │   ├── plans.py            # 阶段2：任务拆解
│   │   ├── execute.py          # 阶段3：代码执行
│   │   ├── verify.py           # 阶段4：测试验证
│   │   └── archive.py          # 阶段5：需求归档
│   ├── initialize/             # 项目初始化子技能
│   ├── writing-design/         # 需求调研子技能
│   ├── review-design/          # 设计审查子技能
│   ├── task-breakdown/         # 任务拆解子技能
│   ├── test-driven-development/ # TDD子技能
│   └── debugging-and-verification/ # 验证调试子技能

└── scripts-coding/             # 脚本编程规范
    ├── SKILL.md                # 技能定义
    ├── templates/              # 脚本模板
    │   └── python_script_template.py
    └── references/             # 参考文档
        └── script-guidelines.md
```

## 快速开始

### vibe-coding 五阶段工作流

**阶段 1：需求分析**
```bash
cd vibe-coding
python scripts/design.py --name add-dark-mode --desc "添加暗色模式支持"
```
编辑生成的 `docs/vibe-coding/changes/add-dark-mode/add-dark-mode-design.md`。

**阶段 2：任务拆解**
```bash
python scripts/plans.py --name add-dark-mode
```
编辑 `{name}-progress.md`，填充任务清单。

**阶段 3：代码执行**
```bash
# 查看任务
python scripts/execute.py --name add-dark-mode --action list

# 开始任务
python scripts/execute.py --name add-dark-mode --task T1 --action start

# 完成任务
python scripts/execute.py --name add-dark-mode --task T1 --action done
```

**阶段 4：测试验证**
```bash
python scripts/verify.py --name add-dark-mode
```

**阶段 5：需求归档**
```bash
python scripts/archive.py --name add-dark-mode
```

### scripts-coding 脚本编程

使用 `scripts-coding/templates/python_script_template.py` 创建规范的脚本文件：

```bash
# 创建脚本
cp scripts-coding/templates/python_script_template.py scripts/my-script.py
```

命名规范：`{YYYYMMDD}-{代码用途}-{version}.py`

## 子技能详细说明

### code-exploration - 代码探索

**核心原则：** 修改代码前必须先理解代码库。

**功能：**
- 系统化探索项目结构、模块依赖、关键函数
- 使用 graphify 生成知识图谱
- 生成代码探索报告
- 支持多种编程语言（Python、JavaScript/TypeScript、Go、Rust 等）

**使用时机：**
- 开始新任务时
- 修改陌生模块或文件时
- 重构现有代码时
- 修复 bug 时

### vibe-coding - AI编程工作流

**五阶段流程：**

| 阶段 | 脚本 | 输入 | 输出 |
|------|------|------|------|
| 1. 需求分析 | `design.py` | 变更名称、描述 | `{name}-design.md` |
| 2. 任务拆解 | `plans.py` | `{name}-design.md` | `{name}-progress.md` |
| 3. 代码执行 | `execute.py` | `{name}-progress.md` | 更新任务状态 |
| 4. 测试验证 | `verify.py` | `{name}-progress.md` | 验证结果 |
| 5. 需求归档 | `archive.py` | 用户已批准 | 归档到 `archive/` |

**子技能：**
- `initialize` - 项目初始化
- `writing-design` - 需求调研
- `review-design` - 设计审查
- `task-breakdown` - 任务拆解
- `test-driven-development` - TDD开发
- `debugging-and-verification` - 验证调试

### scripts-coding - 脚本编程规范

**核心功能：**
- 脚本存放目录规范（`scripts/` 长期，`tmp/` 临时）
- 文件命名规范：`{YYYYMMDD}-{代码用途}-{version}.py`
- Python 脚本模板，包含完整日志配置
- 日志格式：`YYYY-MM-DD HH:MM:SS - LEVEL - filename:line - Message`
- ERROR 级别日志自动包含执行信息和堆栈跟踪
- 日志目录自动检测，支持 Agent 记忆系统集成

## 开发原则

1. **先思考再编码** — 明确假设，暴露困惑，不确定就提问
2. **简洁优先** — 用最少的代码解决问题
3. **精准修改** — 只动必须动的，匹配现有风格
4. **目标驱动执行** — 定义可验证的成功标准

### 工程原则

5. **Hyrum's Law** — 行为的每个细节都是公共 API
6. **Chesterton's Fence** — 不要删除你不理解的东西
7. **测试金字塔** — 70% 单元测试 + 20% 集成测试 + 10% E2E 测试
8. **Beyoncé 规则** — 喜欢一个工具就该为它贡献
9. **左移原则** — 越早发现问题，修复成本越低
10. **二八定律** — 80% 的问题来自 20% 的代码区域

## AI 集成

将 `SKILL.md` 的内容添加到 AI 编程助手的系统提示中，AI 将自动按阶段引导开发过程。

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

### v0.6.0 (2026-05-09)

**新功能：**
- 新增 `scripts-coding` 脚本编程规范技能
- 提供 Python 脚本模板，包含完整日志配置
- 实现文件命名规范：`{YYYYMMDD}-{代码用途}-{version}.py`
- 日志格式增强：包含文件名和行号
- ERROR 级别日志自动包含 exec info 和 stack info
- 日志目录自动检测，支持 Agent 记忆系统集成

**改进：**
- 更新项目结构文档
- 更新 README.md，添加 scripts-coding 子技能说明

### v0.5.0 (2026-05-03)

**新功能：**
- 新增 `code-exploration` 代码探索子技能
- code-exploration 支持使用 graphify 生成交互式知识图谱
- 代码探索报告输出到 `docs/{项目名}-{version}-exploration/` 目录

**改进：**
- 完善 README.md，添加各子技能详细说明
- Git 分支规则：所有提交到 develop 分支，通过 PR 合并到 main

**Bug 修复：**
- 修复 `plans.py` 中 `extract_design_summary` 函数的变量名错误

### v0.4.0 (2026-05-02)

**新功能：**
- 重构为单一 vibe-coding 轻量级 5 阶段工作流
- 参考 OpenSpec 设计理念
- 包含 6 个子技能

**特点：**
- 零依赖、跨平台
- 强制用户批准门槛
- 内置防跑偏检查机制

### v0.3.0 (2026-04-28)

**新功能：**
- 新增阶段：PRD 与详细设计
- 新增技能 `writing-prd-and-design`

### v0.2.0 (2026-04-27)

**新功能：**
- 添加版本号到 SKILL.md
- 添加 6 条工程原则
- 添加平台集成指南

### v0.1.0 (2026-04-26)

- 初始版本发布
- 完成开发生命周期 7 阶段技能体系

## License

MIT