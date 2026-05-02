# Vibe Coding

轻量级 AI 编程技能系统。五阶段工作流：需求分析 → 任务拆解 → 代码执行 → 测试验证 → 需求归档。

## 概述

`vibe-coding` 是一套面向 AI 编程助手的轻量级开发工作流，参考 [OpenSpec](https://github.com/Fission-AI/OpenSpec) 的轻量级设计理念，将工作流扩展为五个阶段：

```
需求分析 → 任务拆解 → 代码执行 → 测试验证 → 需求归档
```

相比 OpenSpec 的 `propose → apply → archive`，我们将 `apply` 拆分为 `任务拆解`（计划）和 `代码执行`（执行），并新增了 `测试验证`（验证）环节，确保每个变更都有据可查。

## 特点

- **零依赖**：仅使用 Python 标准库，无需 `pip install`
- **跨平台**：Windows、macOS、Linux 均可用
- **轻量级**：5 个脚本 + 1 个 SKILL.md，上手即会
- **AI 友好**：SKILL.md 作为路由器，AI 助手加载后自动按阶段引导

## 安装

无需安装。将本目录复制到项目中即可使用：

```bash
# 方式1：直接复制
cp -r vibe-coding/ your-project/.vibe-coding/

# 方式2：子目录
cp -r vibe-coding/ your-project/vibe-coding/
```

## 快速开始

### 1. 需求分析

```bash
python scripts/design.py --name add-dark-mode --desc "添加暗色模式支持"
```

编辑生成的 `docs/vibe-coding/changes/add-dark-mode/add-dark-mode-design.md`，填充目标、背景和成功标准。

### 2. 任务拆解

```bash
python scripts/plans.py --name add-dark-mode
```

编辑 `{name}-progress.md`，填充架构方案和任务清单。

### 3. 代码执行

```bash
# 查看任务
python scripts/execute.py --name add-dark-mode --action list

# 开始任务
python scripts/execute.py --name add-dark-mode --task T1 --action start

# 完成任务
python scripts/execute.py --name add-dark-mode --task T1 --action done
```

### 4. 测试验证

```bash
python scripts/verify.py --name add-dark-mode
```

编辑生成的 `verification.md`，填充测试结果和结论。

### 5. 需求归档

```bash
python scripts/archive.py --name add-dark-mode
```

变更目录将移动到 `docs/vibe-coding/changes/archive/add-dark-mode/`。

## 五阶段详解

| 阶段 | 命令 | 输入 | 输出 | 说明 |
|------|------|------|------|------|
| 1. 需求分析 | `design.py --name <名称>` | 变更名称、描述 | `{name}-design.md` | 创建变更设计 |
| 2. 任务拆解 | `plans.py --name <名称>` | `{name}-design.md` | `{name}-progress.md` | 制定实施计划 |
| 3. 代码执行 | `execute.py --name <名称>` | `{name}-progress.md` | 更新任务状态 | 执行开发任务 |
| 4. 测试验证 | `verify.py --name <名称>` | `{name}-progress.md` | 验证结果 | 验证执行结果 |
| 4.5 用户批准 | - | 验证通过 | 更新状态 | **用户批准后归档** |
| 5. 需求归档 | `archive.py --name <名称>` | 用户已批准 | 移动目录 | 归档已完成工作 |

## 目录结构

```
vibe-coding/
├── SKILL.md                    # 主入口：生命周期路由器
├── README.md                   # 项目文档
├── scripts/
│   ├── design.py              # 阶段1：创建设计文档
│   ├── plans.py                # 阶段2：任务拆解
│   ├── execute.py              # 阶段3：代码执行
│   ├── verify.py               # 阶段4：测试验证
│   └── archive.py              # 阶段5：需求归档
└── docs/vibe-coding/         # 项目 vibe-coding 目录（运行 initialize 后创建）
    ├── {project-name}-design.md  # 项目设计文档
    ├── graphify/              # graphify 扫描文档
    │   ├── report.md         # 代码库结构
    │   ├── modules.md        # 模块依赖
    │   ├── apis.md           # API 接口
    │   ├── data-flows.md     # 数据流
    │   └── tech-stack.md     # 技术栈
    └── changes/              # 在途变更目录
        ├── archive/          # 已归档变更
        └── {name}/           # 单个变更
            ├── {name}-design.md   # 变更设计文档
            └── {name}-progress.md  # 进度跟踪
```

## 状态判断

通过检查文件存在性判断当前阶段：

| 文件状态 | 当前阶段 | 下一步 |
|----------|----------|--------|
| `{name}-design.md` 不存在 | 需要需求分析 | 运行 design.py |
| `{name}-design.md` 存在，阶段2未完成 | 需要任务拆解 | 运行 plans.py |
| 阶段2已完成，有未完成任务 | 需要代码执行 | 运行 execute.py |
| 任务全部 done，`verification.md` 不存在 | 需要测试验证 | 运行 verify.py |
| 验证通过，"用户批准"为 ⏳ | 需要用户批准 | 向用户请求批准 |
| 用户已批准 | 需要需求归档 | 运行 archive.py |

## 脚本参数

所有脚本都支持 `--dir` 参数自定义 changes 目录位置：

```bash
python scripts/design.py --name my-feature --dir /path/to/changes
```

各脚本的详细参数：

### design.py

| 参数 | 必填 | 说明 |
|------|------|------|
| `--name` | 是 | 变更名称（小写字母、数字、连字符） |
| `--desc` | 否 | 简要描述 |
| `--dir` | 否 | 自定义 changes 目录 |

### plans.py

| 参数 | 必填 | 说明 |
|------|------|------|
| `--name` | 是 | 变更名称 |
| `--dir` | 否 | 自定义 changes 目录 |

### execute.py

| 参数 | 必填 | 说明 |
|------|------|------|
| `--name` | 是 | 变更名称 |
| `--action` | 否 | 操作：list/start/done/skip（默认 list） |
| `--task` | 条件 | 任务编号（action 非 list 时必填） |
| `--dir` | 否 | 自定义 changes 目录 |

### verify.py

| 参数 | 必填 | 说明 |
|------|------|------|
| `--name` | 是 | 变更名称 |
| `--dir` | 否 | 自定义 changes 目录 |

### archive.py

| 参数 | 必填 | 说明 |
|------|------|------|
| `--name` | 条件 | 变更名称（与 --list 二选一） |
| `--list` | 否 | 列出已归档变更 |
| `--dir` | 否 | 自定义 changes 目录 |

## 开发原则

1. **先思考再编码** — 明确假设，暴露困惑
2. **简洁优先** — 用最少的代码解决问题
3. **精准修改** — 只动必须动的
4. **目标驱动执行** — 定义可验证的成功标准

## 反模式

- ❌ 不经设计直接编码
- ❌ 没有计划就实施
- ❌ 跳过验证声称"完成"
- ❌ 一次处理多个任务

## AI 集成

将 `SKILL.md` 的内容添加到 AI 编程助手的系统提示中，AI 将自动按五阶段工作流引导开发过程。

支持的 AI 编程工具：

| 工具 | 集成方式 |
|------|----------|
| Claude Code | 通过 CLAUDE.md 加载 |
| Cursor | 通过 .cursorrules 或 Custom Instructions |
| Windsurf | 通过 Cascade Rules |
| GitHub Copilot | 通过 Workspace Instructions |
| CodeBuddy | 通过系统提示 |

## 参考项目

- [OpenSpec](https://github.com/Fission-AI/OpenSpec) — 轻量级 AI 规格文档框架
- [coding-skills](https://github.com/RefoundAI/coding-skills) — 完整的 8 阶段开发技能体系
- [lenny-skills](https://github.com/RefoundAI/lenny-skills) — 产品管理技能集合

## License

MIT
