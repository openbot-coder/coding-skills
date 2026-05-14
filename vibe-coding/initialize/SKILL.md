---
version: 1.0.0
name: initialize
description: "项目初始化子技能。支持模式 A（中央 design.md）和模式 B（旧）。首次启动判断项目类型：绿地→--init，棕地→--adopt，然后创建对应目录结构和文件。"
---

# Initialize — 项目初始化

## 概述

首次使用 vibe-coding 时，判断项目类型并创建对应的目录结构和文件。

## 初始化模式选择

vibe-coding 支持两种模式，**推荐使用模式 A**：

| 模式 | 简介 | 适用场景 |
|------|------|----------|
| **模式 A（推荐）** | 中央 `docs/design.md` + `docs/changelog.md` | 新项目或接手已有项目 |
| 模式 B（旧） | 每变更一个 `docs/vibe-coding/changes/{name}/` | 向后兼容 |

## 首次启动检查

```bash
# 1. 检查工具是否完整
python scripts/tools_check.py

# 2. 检查项目类型
if [ -d "docs/vibe-coding/" ]; then
    # 已有旧模式 B 结构 → 保持向后兼容
    → 检查具体文件，按需操作
elif [ -f "docs/design.md" ]; then
    # 已有模式 A 设计文档 → 直接使用
    → 使用 --change 继续开发
elif [ -z "$(ls -A src/ 2>/dev/null)" ] && [ -z "$(ls -A app/ 2>/dev/null)" ]; then
    # 目录为空或几乎空 → 绿地项目
    → 执行模式 A 绿地初始化
else
    # 已有代码文件 → 棕地项目
    → 执行模式 A 棕地领养
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
| `graphify` | 代码库结构分析（知识图谱） | `pip install graphifyy && graphify install` |

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

**触发条件：** `docs/design.md` 和 `docs/vibe-coding/` 都不存在，且 src/ 目录为空

### 模式 A（推荐）：完整一键初始化

```bash
# 基本用法（自动检测语言类型，默认 unknown）
python scripts/design.py --init --name "项目名称" --desc "项目简要描述"

# 指定开发语言（推荐）
python scripts/design.py --init --name "my-app" --lang python --desc "一个Python Web应用"
python scripts/design.py --init --name "my-app" --lang typescript --desc "一个TS后端服务"
python scripts/design.py --init --name "my-app" --lang rust --desc "一个Rust CLI工具"
python scripts/design.py --init --name "my-app" --lang go --desc "一个Go微服务"
```

**支持的开发语言：** python | javascript | typescript | rust | go

**一键创建的内容：**

| 文件/目录 | 用途 |
|-----------|------|
| `docs/design.md` | 产品设计文档（v0.1.0，预填充项目信息）|
| `docs/changelog.md` | 变更历史（v0.1.0 条目）|
| `src/` | 源代码目录 + 入口文件 |
| `tests/` | 测试目录 |
| `README.md` | 项目说明文档 |
| `.gitignore` | 语言专属的忽略规则 |
| 配置文件 | pyproject.toml / package.json / Cargo.toml / go.mod |
| `.git/` | Git 仓库（自动初始化）|
| Git commit | 自动提交初始版本 |

**效果：**
```
✅ 绿地项目初始化完成（模式 A）
📁 project-root/
   ├── src/            # 源代码入口
   ├── tests/          # 测试
   ├── docs/
   │   ├── design.md   ← 请编辑此文件，填充各章节
   │   └── changelog.md
   ├── README.md
   ├── .gitignore
   └── pyproject.toml  # 语言配置文件
```

### 模式 B（旧，向后兼容）：独立变更文档

```bash
mkdir -p docs/vibe-coding/changes/archive
touch docs/vibe-coding/{project-name}-design.md
```

**额外：** 按语言创建项目结构模板

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

## 二、棕地项目（已有代码项目）

**触发条件：** 项目已有代码（src/、app/ 等目录非空），但无 `docs/design.md`

### 模式 A（推荐）：自动领养

使用 `--adopt` 命令自动扫描已有代码，生成预填充的 design.md：

```bash
# 基本用法：自动检测项目名称、版本、语言、技术栈
python scripts/design.py --adopt

# 指定项目名称（覆盖自动检测）
python scripts/design.py --adopt --name "my-project"

# 指定起始版本号（覆盖自动检测，默认 1.0.0）
python scripts/design.py --adopt --name "my-project" --version 1.0.0
```

**自动检测内容：**
| 配置文件 | 检测内容 |
|----------|----------|
| `pyproject.toml` | 项目名、版本、Python |
| `package.json` | 项目名、版本、框架（React/Vue/Angular）、TS |
| `Cargo.toml` | 项目名、版本、Rust |
| `go.mod` | 项目名、Go |

**生成的设计文档包含：**
- 项目名称、版本号、开发语言
- 检测到的框架信息
- 源代码目录结构
- 测试和文档目录检测

**效果：**
- 创建 `docs/design.md`（预填充基本信息，章节待补充）
- 创建 `docs/changelog.md`（标记为 ✅ 已实现）
- 自动 git commit

**输出：**
```
✅ 棕地项目领养完成（模式 A）
📁 docs/
   ├── design.md       ← 预填充了项目基本信息，请补充详细设计
   └── changelog.md    ← 标记为已实现

📋 下一步：
   1. 编辑 docs/design.md，补充各章节描述
   2. 验证无误后提交
   3. 建议创建初始 tag：git tag -a v1.0.0 -m "初始版本"
   4. 运行代码探索：python ../code-exploration/scripts/explore.py --full
   5. 后续变更使用：--change
```

**自动触发代码探索：**

棕地领养后建议立即执行首次 `code-exploration` 全量扫描，将 graphify 输出提交到 Git 作为后续感知基准：

```bash
# 首次全量扫描
python ../code-exploration/scripts/explore.py --full

# 为初始版本打 tag（包含 graphify 快照）
git tag -a v1.0.0 -m "初始版本 + graphify 探索快照"
git push origin v1.0.0
```

### 模式 B（旧，向后兼容）：手动使用 graphify

```bash
mkdir -p docs/vibe-coding/changes/archive docs/vibe-coding/graphify
```

**代码库扫描**（使用 graphify）：

```bash
# 安装 graphify（如需要）
pip install graphifyy

# 全量知识图谱构建（统一方式）
graphify .
```

基于扫描结果手动创建 `{project-name}-design.md`：

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
