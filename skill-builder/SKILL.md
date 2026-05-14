---
name: skill-builder
description: "技能构建器 v2.0 - 从零创建高质量的 Agent Skills。支持 SKILL 审核机制（可用性 + 安全性）、审计日志系统、自我进化能力。"
---

# Skill Builder — 技能构建器 v2.0

## 概述

专业技能创建助手，帮助用户从零开始创建高质量的 Agent Skills。支持多种模板类型、分步骤引导、完整审核机制、审计日志和自我进化。

**核心功能：**
- 技能发现与需求分析
- 技能类型选择（Archetype Selection）
- 目录结构初始化
- SKILL.md 模板生成
- **可用性审核**（格式、描述清晰度、流程连贯性、可执行性）
- **安全性审核**（注入、凭证泄露、路径穿越等 12 项检查）
- **审计日志**（统一记录 + 统计 + 失败案例复盘）
- **自我进化**（失败模式分析 + 自动优化审核规则）

## 工作流程

```
阶段1: Discovery → 阶段2: Archetype Selection → 阶段3: Initialization
    → 阶段4: Customization → 阶段5: Review       ← v2.0 新增审核阶段
    → 阶段6: Publish（日志记录）
    ↓
持续: Self-Evolution（失败分析 → 规则更新 → 模板优化）
```

### 阶段1：Discovery（发现）

询问用户关于技能的关键问题：

- 这个技能解决什么问题？
- 主要功能是什么？
- 触发词是什么？（用户会说什么来调用这个技能）
- 存放位置？（个人、项目或插件）
- 是否用于 Claude 插件？如果是，加载相关技能

### 阶段2：Archetype Selection（类型选择）

| Archetype | 使用场景 | 示例 | 参考文档 |
|---|---|---|---|
| **simple** | 无脚本的基础技能 | 快速参考、风格指南 | - |
| **api-wrapper** | 包装外部 API | GitHub API、Stripe API | [`references/api-wrapper-guide.md`](references/api-wrapper-guide.md) |
| **document-processor** | 处理文件格式 | PDF 提取器、Excel 分析器 | [`references/document-processor-guide.md`](references/document-processor-guide.md) |
| **dev-workflow** | 自动化开发任务 | Git 工作流、项目脚手架 | [`references/dev-workflow-guide.md`](references/dev-workflow-guide.md) |
| **research-synthesizer** | 收集和综合信息 | 竞争分析、文献综述 | [`references/research-synthesizer-guide.md`](references/research-synthesizer-guide.md) |

### 阶段3：目录结构

创建标准的技能目录结构：

```
skill-name/
├── SKILL.md          # 必需：指令 + 元数据
├── scripts/          # 可选：可执行代码
├── references/       # 可选：文档参考
└── assets/           # 可选：模板、资源
```

### 阶段4：Frontmatter Schema（元数据模板）

生成标准的 SKILL.md frontmatter：

```yaml
---
name: skill-name
description: "What it does and when to use it. Include trigger keywords."
version: 1.0.0
license: MIT
compatibility: Requires git and jq
metadata:
  author: your-org
  category: development
  tags: [testing, automation]
---
```

| 字段 | 是否必需 | 约束 |
|---|---|---|
| `name` | 是 | 2-64 字符，小写/数字/连字符，必须匹配目录名 |
| `description` | 是 | 10-1024 字符，包含引号，描述 what + when |
| `version` | 否 | 语义版本（MAJOR.MINOR.PATCH） |
| `license` | 否 | 许可证名称或引用 |
| `compatibility` | 否 | 1-500 字符，环境要求 |
| `metadata` | 否 | 自定义字段对象 |

### 阶段5：Review（审核）— v2.0 新增

创建完成后，**必须**进行可用性和安全性双重审核。

#### 5.1 可用性审核（Quality Review）

确保生成的 SKILL 在日常使用中可用、易用：

| 检查项 | 内容 | 命令 |
|--------|------|------|
| **格式正确性** | front matter 完整性、YAML 语法、分隔符闭合 | `--quality` |
| **描述清晰度** | description 是否包含 `WHAT + WHEN`、触发词是否明确 | `--quality` |
| **业务流程连贯性** | 流程是否完整、无死循环、条件覆盖全面 | `--quality` |
| **可执行性** | 引用的脚本/文档是否存在、路径是否正确 | `--quality` |

```bash
# 全量审核
python scripts/review.py <skill-dir>

# 仅可用性审核
python scripts/review.py <skill-dir> --quality
```

#### 5.2 安全性审核（Security Review）

检查 SKILL 中的安全风险（共 12+ 个检查模式）：

| 检查项 | 危险信号 | 严重度 |
|--------|----------|--------|
| **代码注入** | `exec()`、`eval()`、`os.system()` | 🔴 严重 |
| **凭证泄露** | 硬编码密码、API Key、Token、Secret | 🔴 严重 |
| **路径穿越** | `../` 不受控的文件路径操作 | 🟡 高危 |
| **命令执行** | shell=True、反引号命令 | 🔴 严重 |
| **反序列化** | pickle.loads() | 🟡 高危 |
| **SSRF** | f-string 拼接 URL | 🟡 高危 |
| **权限问题** | sudo、chmod 777、rm -rf / | 🟡 高危 |

> 安全性审核逻辑复用 `security-audit` 技能的部分规则。

```bash
# 仅安全性审核
python scripts/review.py <skill-dir> --security

# JSON 格式输出（用于脚本集成）
python scripts/review.py <skill-dir> --json
```

**审核通过后方可发布。** 审核结果将被自动记录到审计日志系统。

## 审计日志系统（Audit Log）— v2.0 新增

每次 SKILL 的创建、审核、调用都会记录到统一的日志系统，供统计和复盘。

```
logs/skill-audit/
├── skill-builder-audit.log        ← 每次 SKILL 创建/审核记录（JSON Lines）
├── skill-call-stats.json          ← 每日统计（通过/失败次数）
└── failure-cases/                 ← 失败案例 Md 文档
    ├── YYYYMMDD-HHMMSS-技能名.md
    └── ...
```

每条日志包含：时间戳、SKILL 名称、审核结果、检查明细、失败原因、调用来源。

```bash
# 查看统计
python scripts/audit_log.py stats

# 查看最近审核记录
python scripts/audit_log.py list

# 查看失败案例
python scripts/audit_log.py failures

# 手动记录
python scripts/audit_log.py record <skill-dir> --result pass --checks '{"...":{...}}'
```

## 自我进化（Self-Evolution）— v2.0 新增

基于审计日志和历史数据，实现技能的自动迭代。

### 分析失败模式

| 模式 | 描述 | 自动处理 |
|------|------|----------|
| **frontmatter 错误** | 必填字段缺失、分隔符错误 | 模板预检 + 自动修复 |
| **命名不规范** | name 不符合 kebab-case | 自动规范化函数 |
| **描述质量不足** | 缺少 WHEN/WHAT 信息 | 增加占位符提示 |
| **硬编码凭证** | SKILL 中包含密码/Token | 自动扫描标记 |
| **注入风险** | exec/eval 等危险函数 | 提供安全替代方案 |
| **资源缺失** | 引用不存在的脚本/文档 | 引用前文件存在性检查 |

```bash
# 分析失败模式
python scripts/self_evolve.py analyze

# 获取优化建议
python scripts/self_evolve.py suggest

# 根据历史数据自动生成新审核规则
python scripts/self_evolve.py update-rules

# 生成完整进化报告
python scripts/self_evolve.py report
```

### 工作流

```
开发新 SKILL → 审核（可用性+安全性）→ 日志记录
                                           ↓
                                   持续监控失败模式
                                           ↓
                                   自动更新审核规则
                                           ↓
                                   模板自动优化迭代
                                           ↓
                                   降低失败率 → 质量提升
```

## 使用流程

### 步骤1：初始化技能

```bash
# 创建技能目录
mkdir -p skills/your-skill-name

# 初始化基本结构
touch skills/your-skill-name/SKILL.md
mkdir -p skills/your-skill-name/{scripts,references,assets}
```

### 步骤2：填写 Frontmatter

在 SKILL.md 顶部添加元数据：

```yaml
---
name: your-skill-name
description: "What this skill does and when to use it."
version: 1.0.0
license: MIT
metadata:
  author: your-name
  category: development
---
```

### 步骤3：编写技能内容

在 frontmatter 之后添加详细的技能说明：

```markdown
# Your Skill Name

## Overview

Describe what this skill does...

## When to Use

Explain when this skill should be triggered...

## Workflow

Step-by-step instructions...
```

### 步骤4：添加脚本（可选）

```bash
# 创建脚本目录
mkdir -p scripts/

# 添加脚本文件
touch scripts/helper.py
```

### 步骤5：添加参考文档（可选）

```bash
mkdir -p references/
touch references/api-docs.md
```

### 步骤6：添加资源文件（可选）

```bash
mkdir -p assets/
# 添加模板、图标等资源
```

### 步骤7：审核与发布 — v2.0 新流程

使用 review.py 进行全量审核：

```bash
# 全量审核（可用性 + 安全性）
python scripts/review.py skills/your-skill-name

# 审核通过后，记录日志
python scripts/audit_log.py record skills/your-skill-name --result pass --caller "skill-builder"
```

**审核不通过时** — 修复问题后重新审核，失败案例会自动记录到审计日志。定期运行 `self_evolve.py report` 可查看质量趋势。

## 最佳实践

### 命名规范

- **目录名**：使用 kebab-case，如 `pdf-processing`
- **文件名**：使用小写字母和连字符
- **避免**：大写字母、下划线、连续连字符

### 描述公式

**[WHAT] + [WHEN] + [TRIGGERS]**

```
description: "Extracts text and tables from PDF files, fills forms, merges documents. Use when working with PDF files or document extraction."
```

### 内容指南

1. **保持简洁**：上下文窗口是公共资源，只添加必要信息
2. **设置适当自由度**：根据任务脆弱性选择指导级别
3. **渐进式披露**：分层次加载信息（元数据 → SKILL.md → 资源文件）
4. **避免重复**：信息应存在于 SKILL.md 或 references 中，不要重复

### 文件大小建议

- **SKILL.md**：保持在 500 行以内
- **References**：大型文档放入 references 目录
- **Scripts**：可执行代码放入 scripts 目录

## 示例技能

### 简单技能示例

```markdown
---
name: code-style-guide
description: "Enforce code style guidelines for Python projects. Use when reviewing code or creating new Python files."
version: 1.0.0
license: MIT
---

# Code Style Guide

## Overview

This skill provides Python code style guidelines based on PEP 8.

## Guidelines

1. Use 4 spaces for indentation
2. Maximum line length: 79 characters
3. Use snake_case for functions and variables
4. Use PascalCase for classes
```

### API 包装技能示例

```markdown
---
name: github-api-wrapper
description: "Interact with GitHub API for repository management. Use when working with GitHub repositories, issues, or pull requests."
version: 1.0.0
license: MIT
metadata:
  author: dev-team
  tags: [github, api, automation]
---

# GitHub API Wrapper

## Overview

This skill provides functions to interact with GitHub API.

## Available Functions

- list_repositories()
- create_issue()
- get_pull_request()

## Usage

```python
from scripts.github_api import GitHubAPI
api = GitHubAPI(token="your-token")
repos = api.list_repositories()
```
```

## 与其他技能的衔接

```
skill-builder → 审核（quality + security）→ 审计日志记录 → 发布 skill
     │                ↑
     │                └─ security-audit（可复用检查规则）
     │
     ├──→ scripts-coding（日志规范参考）
     │
     └──→ self-evolution（持续迭代优化）
                ↓
         vibe-coding → 需求分析 → ... → 归档
```

## 命令速查

| 操作 | 命令 |
|------|------|
| 全量审核 | `python scripts/review.py <skill-dir>` |
| 仅可用性审核 | `python scripts/review.py <skill-dir> --quality` |
| 仅安全性审核 | `python scripts/review.py <skill-dir> --security` |
| JSON 审核输出 | `python scripts/review.py <skill-dir> --json` |
| 查看审核统计 | `python scripts/audit_log.py stats` |
| 查看失败案例 | `python scripts/audit_log.py failures` |
| 分析失败模式 | `python scripts/self_evolve.py analyze` |
| 生成进化报告 | `python scripts/self_evolve.py report` |
| 更新审核规则 | `python scripts/self_evolve.py update-rules` |

## 参考资源

- [Agent Skills Specification](https://agentskills.io/specification)
- [GitHub Copilot Skills Documentation](https://github.github.io/awesome-copilot/learning-hub/creating-effective-skills/)
- [outfitter-dev/skillcraft](https://github.com/outfitter-dev/outfitter/tree/main/plugins/fieldguides/skills/skillcraft)
- [muranustb/skills-creator](https://github.com/muranustb/skills-create_skills/tree/main/skills/skills-creator)