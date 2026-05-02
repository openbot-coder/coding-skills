---
version: 1.0.0
name: initialize
description: "项目初始化子技能。首次启动时判断是绿地项目（全新）还是棕地项目（已有），创建对应的 docs/vibe-coding/ 目录结构和文件。"
---

# Initialize — 项目初始化

## 概述

首次使用 vibe-coding 时，判断项目类型并创建对应的目录结构和文件。

## 首次启动检查

```bash
# 1. 检查工具是否完整
python scripts/tools_check.py

# 2. 检查 docs/vibe-coding/ 是否存在
if [ -d "docs/vibe-coding/" ]; then
    # 棕地项目（已有）
    → 执行棕地初始化
else
    # 绿地项目（全新）
    → 执行绿地初始化
fi
```

### 工具检查说明

**必需工具**（缺失会导致 vibe-coding 无法正常工作）：

| 工具 | 用途 | 安装命令 |
|------|------|----------|
| `git` | 版本控制 | [下载](https://git-scm.com/downloads) |
| `ripgrep` | 代码搜索 | `winget install BurntSushi.ripgrep` |

**可选工具**（建议安装）：

| 工具 | 用途 | 安装命令 |
|------|------|----------|
| `graphify` | 代码库结构分析 | `npx graphify install` |

**项目开发工具**（根据项目语言自动检测）：

| 语言 | 工具 | 用途 |
|------|------|------|
| Python | `uv`, `pytest`, `ruff` | 包管理、测试、代码检查 |
| JavaScript | `npm`/`pnpm`, `eslint` | 包管理、代码检查 |
| TypeScript | `tsc`, `prettier` | 编译、格式化 |
| Rust | `cargo`, `rustfmt`, `clippy` | 包管理、格式化、代码检查 |
| Go | `go`, `gofmt` | 编译、格式化 |

## 目录结构

```
docs/vibe-coding/              ← 由本技能维护，供 AI 理解项目结构
├── {project-name}-design.md   ← 项目设计文档
├── changes/                   ← 在途变更（正在执行的变更）
│   ├── {name}-progress.md     ← 当前变更的阶段进度状态
│   └── archive/               ← 已完成变更的归档
└── graphify/                  ← graphify 生成的代码库分析文档
    ├── report.md              ← 代码库整体结构报告
    ├── modules.md             ← 模块/包依赖关系图
    ├── apis.md                ← API 接口列表
    ├── data-flows.md          ← 数据流分析
    └── tech-stack.md           ← 技术栈清单
```

### 目录用途说明

| 目录 | 用途 | AI 使用场景 |
|------|------|-------------|
| `changes/` | 存放当前正在执行的变更 | 了解项目当前的开发进度 |
| `graphify/` | graphify 扫描结果 | 帮助 AI 理解项目架构和代码组织 |

## 一、绿地项目（全新项目）

**触发条件：** `docs/vibe-coding/` 不存在

### 操作步骤

1. **创建目录结构**
   ```bash
   mkdir -p docs/vibe-coding/changes/archive
   ```

2. **创建项目设计文档**
   ```bash
   # 创建空白设计文档
   touch docs/vibe-coding/{project-name}-design.md
   ```

3. **创建项目结构模板**（根据语言选择）

   **Python 项目：**
   ```bash
   mkdir -p src tests docs
   touch src/__init__.py
   touch tests/__init__.py
   ```

   **JavaScript/TypeScript 项目：**
   ```bash
   mkdir -p src tests docs
   touch src/index.ts
   touch tests/index.test.ts
   ```

   **通用：**
   ```bash
   touch README.md .gitignore
   ```

4. **输出**
   ```
   ✅ 绿地项目初始化完成
   📁 docs/vibe-coding/
      └── {project-name}-design.md  ← 请编辑此文件
   ```

## 二、棕地项目（已有项目）

**触发条件：** `docs/vibe-coding/` 不存在，但项目已有代码

### 操作步骤

1. **创建目录结构**
   ```bash
   mkdir -p docs/vibe-coding/changes/archive docs/vibe-coding/graphify
   ```

2. **代码库扫描**（使用 graphify）

   > 参考 [graphify skill](https://skills.sh/akillness/oh-my-skills/graphify)

   ```bash
   # 安装 graphify（如需要）
   npx graphify install

   # 扫描代码库，生成多个分析文档
   npx graphify scan --output docs/vibe-coding/graphify/report.md
   npx graphify modules --output docs/vibe-coding/graphify/modules.md
   npx graphify apis --output docs/vibe-coding/graphify/apis.md
   npx graphify data-flows --output docs/vibe-coding/graphify/data-flows.md
   npx graphify tech-stack --output docs/vibe-coding/graphify/tech-stack.md
   ```

3. **生成项目设计文档**

   基于 `graphify/report.md` 生成 `{project-name}-design.md`：

   ```markdown
   # {项目名称} 设计文档

   ## 项目概述
   <!-- 根据 graphify/report.md 填写 -->

   ## 架构
   <!-- 根据 graphify/report.md 填写 -->

   ## 技术栈
   <!-- 根据 graphify/tech-stack.md 填写 -->

   ## 目录结构
   <!-- 根据 graphify/report.md 填写 -->

   ## 变更日志
   | 日期 | 变更 | 负责人 |
   |------|------|--------|
   ```

4. **输出**
   ```
   ✅ 棕地项目初始化完成
   📁 docs/vibe-coding/
      ├── {project-name}-design.md   ← 项目设计文档
      ├── graphify/
      │   ├── report.md             ← 代码库整体结构
      │   ├── modules.md            ← 模块依赖关系
      │   ├── apis.md               ← API 接口列表
      │   ├── data-flows.md         ← 数据流分析
      │   └── tech-stack.md         ← 技术栈清单
      └── changes/                   ← 在途变更目录
          └── archive/              ← 已完成变更归档
   ```

## 后续变更归档

每次变更归档时，更新 `{project-name}-design.md`：

```markdown
## 变更日志

| 日期 | 变更 | 负责人 | 归档文件 |
|------|------|--------|----------|
| 2026-05-02 | 初始项目 | - | - |
| 2026-05-03 | 添加用户认证 | - | add-auth/ |
```

## 项目名称确定

如果项目目录名称不符合项目含义，可使用以下方式确定：

1. 检查 `package.json` / `pyproject.toml` / `Cargo.toml` 中的项目名
2. 检查 `README.md` 中的项目名
3. 使用目录名作为默认值
