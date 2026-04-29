---
name: using-uv
description: 使用 uv Python 包管理器的指南。在处理 Python 依赖、创建虚拟环境或使用 uv 管理 Python 项目时调用。
---

# 使用 uv - Python 包管理器

uv 是一个用 Rust 编写的极速 Python 包安装器和解析器。本技能提供使用 uv 进行 Python 依赖管理的指导。

## 何时使用本技能

- 创建或管理 Python 虚拟环境
- 安装 Python 包
- 管理项目依赖
- 运行带有依赖隔离的 Python 脚本
- 处理 pyproject.toml

## 常用命令

### 项目初始化

```bash
# 使用包结构初始化新的 Python 项目
uv init --package [项目名称]

# 初始化新的 Python 项目（简单）
uv init [项目名称]

# 在当前目录创建新项目
uv init
```

### 虚拟环境管理

```bash
# 创建虚拟环境
uv venv

# 使用特定 Python 版本创建虚拟环境
uv venv --python 3.11

# 使用自定义名称创建虚拟环境
uv venv .venv-name

# 激活虚拟环境（Windows）
.venv\Scripts\activate

# 激活虚拟环境（Unix/macOS）
source .venv/bin/activate
```

### 包管理

```bash
# 添加包到依赖
uv add <包名>

# 添加开发依赖
uv add --dev <包名>

# 添加带版本约束的包
uv add "package>=1.0.0"

# 移除包
uv remove <包名>

# 从 pyproject.toml 安装所有依赖
uv sync

# 仅安装生产依赖
uv sync --no-dev
```

### 运行命令

```bash
# 运行 Python 脚本
uv run python script.py

# 在虚拟环境中运行命令
uv run <命令>

# 运行 pytest
uv run pytest

# 使用特定 Python 版本运行
uv run --python 3.11 python script.py
```

### 包安装（类 pip）

```bash
# 安装包（一次性）
uv pip install <包名>

# 从 requirements.txt 安装
uv pip install -r requirements.txt

# 从 pyproject.toml 安装
uv pip install -e .

# 列出已安装的包
uv pip list

# 显示包信息
uv pip show <包名>

# 卸载包
uv pip uninstall <包名>
```

### Python 版本管理

```bash
# 列出可用的 Python 版本
uv python list

# 安装 Python 版本
uv python install 3.11

# 为项目固定 Python 版本
uv python pin 3.11
```

### 工具安装

```bash
# 全局安装工具
uv tool install <工具名>

# 不安装直接运行工具
uvx <工具名>

# 示例：不安装直接运行 ruff
uvx ruff check .
```

### 锁文件管理

```bash
# 生成/更新锁文件
uv lock

# 升级所有依赖
uv lock --upgrade

# 升级特定包
uv lock --upgrade-package <包名>
```

## 完整的项目初始化工作流

按此工作流从头设置新的 Python 项目：

### 第 1 步：初始化项目目录

```bash
# 使用包结构创建项目（推荐）
uv init --package my-project

# 或在现有目录中初始化
cd my-project
uv init --package .
```

这会创建：
- `pyproject.toml` - 项目配置
- `src/my_project/__init__.py` - 包入口点
- `.python-version` - 固定的 Python 版本
- `README.md` - 项目说明

### 第 2 步：创建虚拟环境

```bash
# 使用特定 Python 版本创建虚拟环境
uv venv --python 3.13

# 虚拟环境创建在 .venv/
# 激活：.venv\Scripts\activate（Windows）
# 激活：source .venv/bin/activate（Unix/macOS）
```

### 第 3 步：安装开发依赖

```bash
# 安装常用开发工具
uv add --dev ruff black pytest pytest-cov mypy

# 或安装特定版本
uv add --dev "ruff>=0.15.0" "pytest>=9.0.0"
```

推荐的开发包：

| 包 | 用途 |
|------|------|
| ruff | 代码检查和格式化 |
| black | 代码格式化 |
| pytest | 测试框架 |
| pytest-cov | 测试覆盖率 |
| mypy | 类型检查 |

### 第 4 步：创建项目目录

```bash
# 创建标准项目目录
mkdir docs tests examples

# 或在 Windows PowerShell 中
New-Item -ItemType Directory -Force -Path docs, tests, examples
```

目录用途：

| 目录 | 用途 |
|------|------|
| docs/ | 文档文件 |
| tests/ | 测试文件 |
| examples/ | 示例代码和用法 |

### 第 5 步：配置 .gitignore

确保 `.gitignore` 包含以下条目：

```gitignore
# 分发
dist/

# 环境
.env
.venv

# 日志
logs/

# IDE/工具
.idea/
```

### 第 6 步：初始化 Git 仓库

```bash
# 初始化 git
git init

# 添加所有文件
git add .

# 初始提交
git commit -m "Initial commit"
```

### 完整示例

```bash
# 完整初始化工作流
uv init --package myproject
cd myproject
uv venv --python 3.13
uv add --dev ruff black pytest pytest-cov mypy
mkdir docs tests examples
git init
git add .
git commit -m "Initial commit"
```

### 生成的项目结构

```
myproject/
├── .git/              # Git 仓库
├── .gitignore         # Git 忽略规则
├── .python-version    # Python 版本（3.13）
├── pyproject.toml     # 项目配置和依赖
├── uv.lock            # 锁文件
├── README.md
├── LICENSE
├── docs/              # 文档
├── tests/             # 测试文件
├── examples/          # 示例代码
└── src/
    └── myproject/
        └── __init__.py
```

## 最佳实践

1. **使用 pyproject.toml**：项目依赖优先使用 `uv add` 而非 `uv pip install` 以维护正确的依赖跟踪。

2. **锁文件**：总是将 `uv.lock` 提交到版本控制以确保可重现的构建。

3. **虚拟环境**：让 uv 使用 `uv venv` 或 `uv run` 自动管理虚拟环境。

4. **开发依赖**：对仅在开发期间需要的工具使用 `--dev` 标志（pytest、ruff、mypy 等）。

5. **Python 版本**：使用 `uv python pin` 在项目中固定 Python 版本以保持一致性。

## 项目结构示例

```
my-project/
├── .python-version    # 固定的 Python 版本
├── pyproject.toml     # 项目配置和依赖
├── uv.lock            # 锁文件用于可重现安装
├── .venv/             # 虚拟环境（自动创建）
├── docs/              # 文档
├── tests/             # 测试文件
├── examples/          # 示例代码
└── src/
    └── my_package/
        └── __init__.py
```

## pyproject.toml 示例

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "我的 Python 项目"
requires-python = ">=3.10"
dependencies = [
    "requests>=2.28.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
```

## 从 pip/poetry 迁移

```bash
# 从 requirements.txt
uv add $(cat requirements.txt)

# 从 poetry - 直接使用现有 pyproject.toml
uv sync
```

## 故障排除

- **安装缓慢**：uv 应该非常快。如果慢，检查网络或尝试 `--no-cache`
- **版本冲突**：使用 `uv lock --upgrade` 解决
- **找不到 Python**：使用 `uv python install <版本>` 安装 Python
