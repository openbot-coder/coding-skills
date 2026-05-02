---
name: code-exploration
description: "代码探索技能 - 在修改代码前必须先理解代码库结构、依赖关系和现有实现。通过系统化的探索方法和知识图谱分析，生成代码探索报告，快速建立对陌生代码的认知。"
---

# Code Exploration — 代码探索

## 概述

在修改任何代码之前，必须先理解代码库。这是避免破坏现有功能、做出不合理修改的关键步骤。

**核心原则：** 不要删除你不理解的东西。先探索，再动手。

参考 [graphify](https://github.com/safishamsi/graphify) 的设计理念，本技能支持将代码库转换为知识图谱，并生成代码探索报告。

## 探索前检查

在开始代码探索之前，先检查 graphify 是否已安装：

```bash
# 检查 graphify 是否已安装
if ! command -v graphify &> /dev/null; then
    echo "错误: graphify 未安装"
    echo "请运行以下命令之一安装 graphify:"
    echo "1. uv tool install graphifyy && graphify install"
    echo "2. pipx install graphifyy && graphify install"
    echo "3. pip install graphifyy && graphify install"
    exit 1
fi
```

**PowerShell 检查命令:**
```powershell
if (-not (Get-Command "graphify" -ErrorAction SilentlyContinue)) {
    Write-Host "错误: graphify 未安装" -ForegroundColor Red
    Write-Host "请运行以下命令之一安装 graphify:"
    Write-Host "1. uv tool install graphifyy; graphify install"
    Write-Host "2. pipx install graphifyy; graphify install"
    Write-Host "3. pip install graphifyy; graphify install"
    exit 1
}
```

## 探索时机

以下情况必须执行代码探索：

- 开始一个新任务时
- 修改陌生的模块或文件时
- 重构现有代码时
- 修复 bug 时（需要先理解相关代码）
- 进入 review-design 之前

## 报告输出目录

```
docs/
└── {项目名称}-{version}-exploration/    ← 代码探索报告目录
    ├── {项目名称}-exploration.md        ← 代码探索报告（主文档）
    ├── graphify-out/                    ← graphify 知识图谱输出
    │   ├── graph.html                  ← 交互式图谱
    │   ├── graph.json                  ← 持久化图数据
    │   └── GRAPH_REPORT.md             ← 图谱分析报告
    └── modules/                         ← 模块详细分析
        ├── {module-name}-analysis.md   ← 各模块分析文档
        └── data-flows.md               ← 数据流分析
```

**命令：**
```bash
# 创建报告目录
mkdir -p docs/{项目名}-{version}-exploration

# 运行 graphify 生成知识图谱
graphify .
```

## 探索维度

### 1. 项目结构

```
项目结构分析
├── 目录结构          ← 主要目录和用途
├── 根目录文件        ← package.json, Cargo.toml 等
├── 入口文件          ← main.py, index.js 等
└── 配置文件          ← .env, config 等
```

**探索命令：**
```bash
# 目录结构
ls -la
find . -type d -maxdepth 3 | head -30

# 项目类型判断
rg -l "package\.json" .              # Node.js
rg -l "Cargo\.toml" .                # Rust
rg -l "go\.mod" .                     # Go
rg -l "requirements\.txt" .           # Python
```

### 2. 模块依赖

```
模块依赖分析
├── 核心模块           ← 主要业务逻辑
├── 公共工具           ← 共享函数/类
├── 外部依赖           ← 第三方库
└── 数据流             ← 模块间调用关系
```

**探索命令：**
```bash
# 依赖关系
rg -n "^import |^from .* import" --type py | head -50
rg -n "^const |^import |^require\(" --type js | head -50

# 查找模块定义
rg -n "^module.exports" .
rg -n "^export (class|function|const)" .
```

### 3. 关键函数/类

```
关键代码定位
├── 核心函数           ← 业务逻辑入口
├── 工具函数           ← 辅助功能
├── 数据结构           ← 重要的类型/类
└── 边界处理           ← 错误处理逻辑
```

**探索命令：**
```bash
# 搜索函数定义
rg -n "^def \w+\(" --type py
rg -n "^function \w+\(" --type js
rg -n "func \w+\(" --type go

# 搜索类定义
rg -n "^class \w+" --type py
rg -n "^class \w+" --type js
```

### 4. 数据流

```
数据流分析
├── 输入处理           ← API/CLI/文件
├── 数据转换           ← 业务逻辑处理
├── 输出/副作用         ← 数据库/网络/文件
└── 状态管理           ← 全局状态/缓存
```

**探索命令：**
```bash
# 搜索 API 路由/端点
rg -n "router\.|@app\.|@router\." --type py
rg -n "router\.|routes\.|GET\(|POST\(" --type js

# 搜索数据库操作
rg -n "\.query\(|\.execute\(|SELECT |INSERT " --type py
rg -n "db\.|mongo\.|redis\." --type js
```

### 5. 现有测试

```
测试覆盖分析
├── 测试文件位置
├── 测试用例数量
├── 覆盖范围
└── 测试模式
```

**探索命令：**
```bash
# 查找测试文件
find . -name "*test*" -o -name "*spec*" | head -20
find . -name "test_*.py" -o -name "*_test.py"

# 查看测试覆盖
rg -n "def test_|it\(|describe\(" --type py | head -30
```

### 6. 知识图谱分析

参考 graphify 的实现，构建代码知识图谱：

```
知识图谱分析
├── 节点类型           ← 文件、类、函数、变量、接口
├── 关系类型           ← imports, calls, extends, implements, uses
├── 社区聚类           ← 模块分组
└── 关键节点           ← 核心模块、频繁调用的函数
```

**关系类型定义：**

| 关系类型 | 含义 | 标记 |
|----------|------|------|
| `EXTRACTED` | 从源代码直接提取 | ✅ 确定 |
| `INFERRED` | 合理推断，带置信度 | ⚠️ 需验证 |
| `AMBIGUOUS` | 含义模糊，需审查 | ❓ 待确认 |

**生成知识图谱：**

```bash
# 使用 graphify 生成知识图谱
graphify .

# 输出文件
# graphify-out/
# ├── graph.html       ← 交互式图 - 点击节点、搜索、过滤社区
# ├── GRAPH_REPORT.md  ← 关键节点、意外连接、建议问题
# └── graph.json       ← 持久化图 - 后续查询无需重新读取
```

**自定义忽略规则：**

创建 `.graphifyignore` 文件（语法同 `.gitignore`）：
```
# .graphifyignore
vendor/
node_modules/
dist/
*.generated.py
```

## 探索流程

```
┌─────────────────────────────────────────────────────────────┐
│ 步骤1：初始化报告目录                                        │
│ - 创建 docs/{项目名}-{version}-exploration/                 │
│ - 运行 graphify . 生成知识图谱                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 步骤2：探索项目结构                                         │
│ - 查看目录结构、主要文件                                      │
│ - 判断项目类型和架构模式                                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 步骤3：模块依赖分析                                         │
│ - 分析核心模块和公共工具                                      │
│ - 绘制模块间调用关系                                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 步骤4：关键代码定位                                         │
│ - 找到核心函数和类                                          │
│ - 理解数据流和边界处理                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 步骤5：生成探索报告                                         │
│ - 编写 {项目名}-exploration.md                               │
│ - 保存模块详细分析到 modules/                                 │
│ - 更新 graphify 输出到 graphify-out/                         │
└─────────────────────────────────────────────────────────────┘
```

## 代码探索报告模板

创建 `docs/{项目名}-{version}-exploration/{项目名}-exploration.md`：

```markdown
# {项目名} 代码探索报告

> 版本：{version}
> 探索时间：{date}
> 探索者：{explorer}

## 项目概况

| 属性 | 值 |
|------|-----|
| 项目类型 | [Node.js/Python/Rust/其他] |
| 架构模式 | [MVC/微服务/分层/其他] |
| 主要语言 | [Python/TypeScript/Go/其他] |
| 依赖管理器 | [npm/cargo/pip/其他] |

## 目录结构

```
{项目根目录}/
├── src/                   ← 源代码目录
├── tests/                 ← 测试目录
├── docs/                  ← 文档目录
└── [其他主要目录]
```

## 核心模块

| 模块 | 路径 | 职责 |
|------|------|------|
| {模块1} | {path} | {description} |
| {模块2} | {path} | {description} |

## 模块依赖图

```
{PlantUML 或 Mermaid 依赖图}
```

## 关键代码

### 入口点

- **主入口**: `{file}:{line}`
- **CLI 入口**: `{file}:{line}`
- **API 入口**: `{file}:{line}`

### 核心函数

| 函数 | 路径 | 用途 |
|------|------|------|
| {func1} | {path}:{line} | {description} |

### 关键数据结构

| 结构 | 路径 | 用途 |
|------|------|------|
| {struct1} | {path}:{line} | {description} |

## 数据流

```
{输入} → {处理模块} → {输出}
```

## API 端点

| 端点 | 方法 | 处理函数 |
|------|------|----------|
| /api/users | GET | {func} |

## 测试覆盖

- 测试文件位置：`{path}`
- 测试用例数量：{count}
- 覆盖率：{percentage}%

## 知识图谱

知识图谱已生成，详见 `graphify-out/` 目录：

- `graph.html` — 交互式图谱
- `graph.json` — 持久化图数据
- `GRAPH_REPORT.md` — 图谱分析报告

## 关键发现

1. **{发现1}**: {描述}
2. **{发现2}**: {描述}

## 架构决策记录

| ADR | 决策 | 原因 |
|-----|------|------|
| ADR-001 | {决策} | {原因} |

## 潜在风险

- {风险1}: {描述}
- {风险2}: {描述}

## 附录

### 关键文件索引

| 文件 | 行数 | 说明 |
|------|------|------|
| {file} | {lines} | {desc} |

### 参考文档

- {doc1}
- {doc2}
```

## 快速参考

| 目标 | 命令 |
|------|------|
| 创建报告目录 | `mkdir -p docs/{项目名}-{version}-exploration` |
| 生成知识图谱 | `graphify .` |
| 项目结构 | `ls -la && find . -type d -maxdepth 3` |
| 搜索函数 | `rg -n "^def \w+\(" --type py` |
| 搜索类 | `rg -n "^class \w+" --type py` |
| 搜索导入 | `rg -n "^import \|^from .* import"` |
| 查找测试 | `find . -name "*test*" -o -name "*spec*"` |
| 查找 API | `rg -n "router\.\|@app\.\|routes\."` |
| 查看调用 | `rg -n "函数名"` |

## Chesterton's Fence

> "在拆除栅栏之前，首先理解为什么它被建造。"

如果探索中发现：
- 看起来"愚蠢"的代码 → 可能有你不知道的原因
- "不必要"的抽象 → 可能是为了可扩展性
- 重复代码 → 可能是有意为之避免耦合

**原则：** 不理解之前，不要修改。提问或记录疑问。

## graphify 安装与使用

```bash
# 使用 uv 安装（推荐）
uv tool install graphifyy && graphify install

# 或使用 pipx
pipx install graphifyy && graphify install

# 或使用 pip
pip install graphifyy && graphify install
```

**注意：** PyPI 上官方包名为 `graphifyy`，其他名为 `graphify*` 的包与此项目无关。

## 与其他技能的衔接

```
code-exploration → writing-design → review-design → 任务拆解 → 代码执行
     ↑                                          ↓
     └────────────── 遇到问题时 ←────────────────┘
```

**使用场景：**
- writing-design 前：探索项目上下文，生成代码探索报告
- review-design 前：确认理解目标代码，分析影响范围
- 代码执行前：了解要修改的代码，制定安全的修改方案
