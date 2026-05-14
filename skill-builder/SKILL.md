---
name: skill-builder
description: "技能构建器 - 帮助用户从零开始创建高质量的 Agent Skills。支持多种技能类型、分步骤引导、完整文档生成和结构验证。"
---

# Skill Builder — 技能构建器

## 概述

专业技能创建助手，帮助用户从零开始创建高质量的 Agent Skills。支持多种模板类型、分步骤引导、完整文档生成，是构建自定义技能的一站式解决方案。

**核心功能：**
- 技能发现与需求分析
- 技能类型选择（Archetype Selection）
- 目录结构初始化
- SKILL.md 模板生成
- 技能验证与质量检查

## 工作流程

```
阶段1: Discovery → 阶段2: Archetype Selection → 阶段3: Initialization → 阶段4: Customization → 阶段5: Validation
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

### 阶段5：Validation（验证）

验证技能结构的完整性和正确性：

- ✅ SKILL.md 文件存在
- ✅ Frontmatter 包含 name 和 description
- ✅ name 符合命名规范（kebab-case）
- ✅ 目录名称与 name 一致
- ✅ description 包含足够信息
- ✅ 文件编码为 UTF-8

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

### 步骤7：验证技能

运行验证检查：

- 检查 SKILL.md 存在
- 验证 frontmatter 格式
- 检查目录结构
- 验证编码格式

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
skill-builder → vibe-coding → 需求分析 → 任务拆解 → 代码执行 → 测试验证 → 需求归档
     ↑                                                                 ↓
     └───────────────────── 技能开发完成 ────────────────────────────────┘
```

## 参考资源

- [Agent Skills Specification](https://agentskills.io/specification)
- [GitHub Copilot Skills Documentation](https://github.github.io/awesome-copilot/learning-hub/creating-effective-skills/)
- [outfitter-dev/skillcraft](https://github.com/outfitter-dev/outfitter/tree/main/plugins/fieldguides/skills/skillcraft)
- [muranustb/skills-creator](https://github.com/muranustb/skills-create_skills/tree/main/skills/skills-creator)