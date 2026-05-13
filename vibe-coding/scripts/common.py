#!/usr/bin/env python3
"""vibe-coding 公共工具模块

提供项目根目录查找、changes 目录管理、Git 操作、版本管理、项目扫描、任务表格模板等公共功能。
"""

import json
import os
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def setup_unicode_output():
    """解决 Windows 控制台 Unicode 输出问题"""
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def find_project_root(start_dir: Optional[Path] = None) -> Path:
    """从给定目录向上查找项目根目录

    检测以下项目标记（按优先级）：
    - .git（Git 仓库）
    - pyproject.toml（Python）
    - package.json（Node.js）
    - Cargo.toml（Rust）
    - go.mod（Go）

    Args:
        start_dir: 起始查找目录，默认为当前工作目录

    Returns:
        项目根目录路径
    """
    start = start_dir or Path.cwd()
    markers = [
        ".git", "pyproject.toml", "package.json",
        "Cargo.toml", "go.mod",
    ]
    for parent in [start] + list(start.parents):
        for marker in markers:
            if (parent / marker).exists():
                return parent
    return start


def get_changes_dir(script_dir: Path, custom_dir: Optional[str] = None) -> Path:
    """获取 changes 目录路径（默认：项目根目录/docs/vibe-coding/changes）"""
    if custom_dir:
        return Path(custom_dir)
    project_root = find_project_root()
    return project_root / "docs" / "vibe-coding" / "changes"


def run_git_command(args: list, cwd: Optional[Path] = None) -> tuple:
    """运行 git 命令

    Args:
        args: git 命令参数列表
        cwd: 执行目录

    Returns:
        (success, stdout, stderr) 元组
    """
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def ensure_on_develop_branch(project_root: Path) -> bool:
    """确保当前在 develop 分支"""
    success, current_branch, _ = run_git_command(["git", "branch", "--show-current"], project_root)
    if current_branch != "develop":
        print(f"⚠️  当前不在 develop 分支（当前：{current_branch}）")
        return False
    return True


def git_add_and_commit(project_root: Path, message: str) -> bool:
    """执行 git add . 和 git commit

    Args:
        project_root: 项目根目录
        message: 提交消息

    Returns:
        是否成功
    """
    success, _, stderr = run_git_command(["git", "add", "."], project_root)
    if not success:
        print(f"⚠️  git add 失败：{stderr}")
        return False

    success, _, stderr = run_git_command(["git", "commit", "-m", message], project_root)
    if not success:
        print(f"⚠️  git commit 失败：{stderr}")
        return False

    return True


def is_git_repo(project_root: Path) -> bool:
    """检查目录是否为 Git 仓库"""
    success, _, _ = run_git_command(["git", "rev-parse", "--git-dir"], project_root)
    return success


def has_pending_changes(project_root: Path) -> bool:
    """检查是否有未提交的更改"""
    success, stdout, _ = run_git_command(["git", "status", "--porcelain"], project_root)
    return success and bool(stdout)


def ensure_directory(path: Path, name: str = "目录") -> bool:
    """确保目录存在，不存在则创建"""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"✅ {name} 已创建：{path}")
        return True
    return False


TASK_TABLE_HEADER = "| # | 任务名称 | 状态 | 优先级 | 预计工时 | 功能点数 | 完成时间 |"
TASK_TABLE_SEPARATOR = "|---|----------|------|--------|----------|----------|----------|"

PROGRESS_TEMPLATE_TASK_SECTION = """### 任务清单

| # | 任务名称 | 状态 | 优先级 | 预计工时 | 功能点数 | 完成时间 |
|---|----------|------|--------|----------|----------|----------|
| - | - | - | - | - | - | - |"""


def parse_tasks_from_status(status_content: str) -> List[dict]:
    """从 progress.md 解析任务列表（统一格式）

    解析 阶段2/3 中的任务清单表格，提取任务信息。

    Returns:
        任务列表，每项包含 id, name, status
    """
    tasks = []
    in_task_table = False
    for line in status_content.split("\n"):
        if "| # | 任务名称 |" in line and "| 状态 |" in line:
            in_task_table = True
            continue
        if in_task_table:
            if line.startswith("---") or line.startswith("|---"):
                continue
            if not line.startswith("|"):
                break
            match = re.match(r"\|\s*(\d+)\s*\|\s*([^\|]+)\s*\|\s*([^\|]+)\s*\|", line)
            if match:
                task_id = match.group(1)
                task_name = match.group(2).strip()
                status = match.group(3).strip()
                tasks.append({
                    "id": task_id,
                    "name": task_name,
                    "status": status,
                })
    return tasks


def update_task_status(status_file: Path, task_id: str, new_status: str) -> bool:
    """更新任务状态

    Args:
        status_file: progress.md 文件路径
        task_id: 任务编号
        new_status: 新状态（✅ / ⏳ / ⏭️）

    Returns:
        是否更新成功
    """
    if not status_file.exists():
        return False

    content = status_file.read_text(encoding="utf-8")
    lines = content.split("\n")
    new_lines = []
    updated = False

    for i, line in enumerate(lines):
        if not line.startswith("|"):
            new_lines.append(line)
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 4 and parts[1] == task_id:
            if new_status == "done":
                new_lines.append(f"| {task_id} | {parts[2]} | ✅ | {parts[4]} | {parts[5]} | {parts[6]} | {parts[7]} |")
                updated = True
                continue
            elif new_status == "skip":
                new_lines.append(f"| {task_id} | {parts[2]} | ⏭️ | {parts[4]} | {parts[5]} | {parts[6]} | {parts[7]} |")
                updated = True
                continue
        new_lines.append(line)

    if updated:
        status_file.write_text("\n".join(new_lines), encoding="utf-8")

    return updated


# =============================================================================
# 版本管理（方案 B：中央 design.md + 独立 changelog.md）
# =============================================================================


def get_docs_dir(script_dir: Optional[Path] = None, custom_dir: Optional[str] = None) -> Path:
    """获取 docs 目录路径（design.md 和 changelog.md 所在目录）

    默认：项目根目录/docs/
    """
    if custom_dir:
        return Path(custom_dir)
    project_root = find_project_root()
    return project_root / "docs"


def read_version(design_file: Path) -> Optional[str]:
    """从 design.md 读取当前版本号

    匹配格式：> 版本：1.2.0 或 > 版本: 1.2.0
    """
    if not design_file.exists():
        return None

    content = design_file.read_text(encoding="utf-8")
    match = re.search(r">\s*版本[：:]\s*(\d+\.\d+(?:\.\d+)?)", content)
    if match:
        return match.group(1)
    return None


def bump_version(version: str, bump_type: str = "minor") -> str:
    """递增 semver 版本号

    Args:
        version: 当前版本号，如 "1.0.0"
        bump_type: "major" | "minor" | "patch"

    Returns:
        递增后的版本号
    """
    parts = version.split(".")
    while len(parts) < 3:
        parts.append("0")

    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump_type: {bump_type}")


def update_version_in_design(design_file: Path, new_version: str) -> bool:
    """更新 design.md 中的版本号和最后更新日期"""
    if not design_file.exists():
        return False

    content = design_file.read_text(encoding="utf-8")

    # 更新版本号
    content = re.sub(
        r"(>\s*版本[：:]\s*)\d+\.\d+(?:\.\d+)?",
        rf"\g<1>{new_version}",
        content,
    )

    # 更新最后更新日期
    today = date.today().isoformat()
    content = re.sub(
        r"(>\s*最后更新[：:]\s*)\S+",
        rf"\g<1>{today}",
        content,
    )

    design_file.write_text(content, encoding="utf-8")
    return True


def update_last_updated(design_file: Path) -> bool:
    """仅更新 design.md 中的最后更新日期（不改版本号）"""
    if not design_file.exists():
        return False

    content = design_file.read_text(encoding="utf-8")
    today = date.today().isoformat()
    content = re.sub(
        r"(>\s*最后更新[：:]\s*)\S+",
        rf"\g<1>{today}",
        content,
    )
    design_file.write_text(content, encoding="utf-8")
    return True


def get_git_tags(project_root: Path) -> List[str]:
    """获取所有 git tag（按版本排序）"""
    if not is_git_repo(project_root):
        return []

    success, stdout, _ = run_git_command(
        ["git", "tag", "-l", "--sort=-v:refname"],
        project_root,
    )
    if not success or not stdout:
        return []

    return [t.strip() for t in stdout.strip().split("\n") if t.strip()]


def find_tag_for_version(version: str, project_root: Path) -> Optional[str]:
    """查找指定版本号对应的 git tag"""
    tags = get_git_tags(project_root)
    # 精确匹配 v{version} 格式
    target = f"v{version}"
    for tag in tags:
        if tag == target:
            return tag
    return None


def rollback_files_from_tag(
    tag: str, project_root: Path, file_paths: List[str]
) -> Tuple[bool, str]:
    """从指定 git tag 恢复文件

    Args:
        tag: git tag 名称
        project_root: 项目根目录
        file_paths: 要恢复的文件路径列表（相对于项目根目录）

    Returns:
        (success, message)
    """
    if not is_git_repo(project_root):
        return False, "不是 Git 仓库"

    # 检查 tag 是否存在
    success, _, _ = run_git_command(
        ["git", "rev-parse", "--verify", tag],
        project_root,
    )
    if not success:
        return False, f"Tag '{tag}' 不存在"

    # 逐个恢复文件
    restored = []
    failed = []
    for fp in file_paths:
        success, _, stderr = run_git_command(
            ["git", "checkout", tag, "--", fp],
            project_root,
        )
        if success:
            restored.append(fp)
        else:
            failed.append((fp, stderr))

    if failed:
        msg = f"恢复了 {len(restored)} 个文件，{len(failed)} 个失败"
        for fp, err in failed:
            msg += f"\n  失败: {fp} - {err}"
        return False, msg

    return True, f"已从 tag '{tag}' 恢复 {len(restored)} 个文件"


# =============================================================================
# 项目扫描（棕地项目检测）
# =============================================================================


def detect_project_info(project_root: Path) -> Dict:
    """扫描现有项目，检测项目名称、版本、技术栈、源代码目录等信息

    Args:
        project_root: 项目根目录

    Returns:
        包含项目信息的字典：
        {
            "name": str,
            "version": str,
            "language": str,
            "frameworks": list,
            "src_dirs": list,
            "has_tests": bool,
            "has_docs": bool,
        }
    """
    info = {
        "name": project_root.name,
        "version": "1.0.0",
        "language": "unknown",
        "frameworks": [],
        "src_dirs": [],
        "has_tests": False,
        "has_docs": False,
    }

    # 语言优先级检测：第一个匹配的配置文件决定语言（pyproject > package.json > Cargo > go.mod）
    pyproject = project_root / "pyproject.toml"
    package_json = project_root / "package.json"
    cargo = project_root / "Cargo.toml"
    go_mod = project_root / "go.mod"

    if pyproject.exists():
        info["language"] = "python"
        try:
            content = pyproject.read_text(encoding="utf-8")
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if name_match:
                info["name"] = name_match.group(1)
            ver_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if ver_match:
                info["version"] = ver_match.group(1)
        except Exception:
            pass

    elif package_json.exists():
        info["language"] = "javascript"
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
            if "name" in data:
                info["name"] = data["name"]
            if "version" in data:
                info["version"] = data["version"]
            if "dependencies" in data:
                deps = list(data["dependencies"].keys())
                if any("typescript" in d.lower() for d in deps):
                    info["language"] = "typescript"
                if any("react" in d.lower() for d in deps):
                    info["frameworks"].append("React")
                if any("vue" in d.lower() for d in deps):
                    info["frameworks"].append("Vue")
                if any("angular" in d.lower() for d in deps):
                    info["frameworks"].append("Angular")
        except Exception:
            pass

    elif cargo.exists():
        info["language"] = "rust"
        try:
            content = cargo.read_text(encoding="utf-8")
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if name_match:
                info["name"] = name_match.group(1)
            ver_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if ver_match:
                info["version"] = ver_match.group(1)
        except Exception:
            pass

    elif go_mod.exists():
        info["language"] = "go"
        try:
            content = go_mod.read_text(encoding="utf-8")
            name_match = re.search(r"^module\s+(\S+)", content, re.MULTILINE)
            if name_match:
                info["name"] = name_match.group(1).split("/")[-1]
        except Exception:
            pass

    # 检测源代码目录
    for dir_name in ["src", "app", "lib", "source", "cmd", "pkg"]:
        d = project_root / dir_name
        if d.exists() and d.is_dir():
            info["src_dirs"].append(dir_name)

    # 检测测试目录
    for dir_name in ["tests", "test", "__tests__", "spec"]:
        if (project_root / dir_name).exists():
            info["has_tests"] = True
            break

    # 检测 docs 目录
    if (project_root / "docs").exists():
        info["has_docs"] = True

    # 如果都没检测到 src 目录，用当前目录
    if not info["src_dirs"]:
        info["src_dirs"].append(".")

    return info


def generate_adopt_design(project_root: Path, info: Dict) -> str:
    """根据扫描结果生成预填充的设计文档

    Args:
        project_root: 项目根目录
        info: detect_project_info() 返回的项目信息

    Returns:
        填充好的 design.md 内容
    """
    today = date.today().isoformat()
    name = info["name"]
    language = info["language"]
    frameworks = ", ".join(info["frameworks"]) if info["frameworks"] else "无"
    src_dirs = ", ".join(info["src_dirs"])
    has_tests = "有" if info["has_tests"] else "无"
    version = info["version"]

    # 扫描目录结构
    dir_structure = _scan_directory(project_root, max_depth=2, max_entries=30)

    return f"""# 产品设计文档

> 版本：{version}
> 创建日期：{today}
> 最后更新：{today}

## 1. 项目概述

**项目名称：** {name}
**开发语言：** {language}
**框架：** {frameworks}

> 此文档通过 `--adopt` 从现有项目自动生成。
> 请补充项目整体描述、目标用户、核心价值主张。

## 2. 架构设计

<!-- 系统架构图、模块划分、技术栈选择 -->

### 检测到的源代码目录

- **{src_dirs}**

{dir_structure}

### 测试

- 测试：{has_tests}

## 3. 数据模型

<!-- 数据库表结构、核心实体定义 -->

## 4. API 设计

<!-- 接口定义、请求/响应格式 -->

## 5. 安全设计

<!-- 认证、授权、加密、数据保护 -->

## 6. 配置与部署

<!-- 环境配置、部署方式、运维要求 -->

## 7. 非功能性需求

<!-- 性能、可用性、兼容性、可扩展性 -->
"""


def _scan_directory(base_dir: Path, max_depth: int = 2, max_entries: int = 30) -> str:
    """扫描目录结构，生成 Markdown 代码块

    忽略 .git, node_modules, __pycache__, .venv, target 等通用目录
    """
    ignore_dirs = {
        ".git", "node_modules", "__pycache__", ".venv", "venv",
        ".idea", ".vscode", "target", "build", "dist", ".next",
        ".nuxt", ".output", "vendor", "bower_components",
    }
    ignore_exts = {".pyc", ".pyo", ".so", ".dll", ".dylib", ".exe"}

    lines = ["```"]
    lines.append(f"{base_dir.name}/")

    def _walk(dir_path: Path, prefix: str, depth: int) -> int:
        count = 0
        try:
            entries = sorted(
                [e for e in dir_path.iterdir() if e.name not in ignore_dirs],
                key=lambda x: (not x.is_dir(), x.name.lower()),
            )
        except PermissionError:
            return 0

        for i, entry in enumerate(entries):
            if count >= max_entries:
                lines.append(f"{prefix}   ... (更多文件)")
                count += 1
                break

            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "

            if entry.is_dir():
                lines.append(f"{prefix}{connector}{entry.name}/")
                if depth < max_depth:
                    sub_prefix = prefix + ("    " if is_last else "│   ")
                    count += _walk(entry, sub_prefix, depth + 1)
                count += 1
            else:
                ext = entry.suffix.lower()
                if ext not in ignore_exts:
                    lines.append(f"{prefix}{connector}{entry.name}")
                    count += 1

        return count

    _walk(base_dir, "", 1)
    lines.append("```")

    return "\n".join(lines)


# =============================================================================
# 绿地项目骨架生成
# =============================================================================

LANGUAGE_CONFIGS = {
    "python": {
        "gitignore": """# Python
__pycache__/
*.py[cod]
*.so
*.egg-info/
dist/
build/
.venv/
venv/
.env
.pytest_cache/
.mypy_cache/
.ruff_cache/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
""",
        "src_init": "",
        "test_init": "",
        "config_file": "pyproject.toml",
        "config_content": """[project]
name = "{name}"
version = "0.1.0"
description = "{desc}"
requires-python = ">=3.10"

[tool.pytest.ini_options]
minversion = "6.0"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py310"
""",
        "src_dir": "src",
    },
    "javascript": {
        "gitignore": """# Node
node_modules/
dist/
build/
.env
.env.local
*.log
npm-debug.log*

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
""",
        "src_init": "// Entry point\n",
        "test_init": "",
        "config_file": "package.json",
        "config_content": """{{
  "name": "{name}",
  "version": "0.1.0",
  "description": "{desc}",
  "main": "src/index.js",
  "scripts": {{
    "test": "echo \\"No test specified\\" && exit 0",
    "start": "node src/index.js"
  }}
}}
""",
        "src_dir": "src",
    },
    "typescript": {
        "gitignore": """# Node
node_modules/
dist/
build/
.env
.env.local
*.log
npm-debug.log*

# TypeScript
*.tsbuildinfo

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
""",
        "src_init": "// Entry point\n",
        "test_init": "",
        "config_file": "package.json",
        "config_content": """{{
  "name": "{name}",
  "version": "0.1.0",
  "description": "{desc}",
  "main": "dist/index.js",
  "scripts": {{
    "build": "tsc",
    "test": "echo \\"No test specified\\" && exit 0",
    "start": "node dist/index.js"
  }},
  "devDependencies": {{
    "typescript": "^5.0.0"
  }}
}}
""",
        "src_dir": "src",
    },
    "rust": {
        "gitignore": """# Rust
/target/
**/*.rs.bk
Cargo.lock

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
""",
        "src_init": "fn main() {\n    println!(\"Hello, world!\");\n}\n",
        "test_init": "",
        "config_file": "Cargo.toml",
        "config_content": """[package]
name = "{name}"
version = "0.1.0"
edition = "2021"
description = "{desc}"

[dependencies]
""",
        "src_dir": "src",
    },
    "go": {
        "gitignore": """# Go
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
/vendor/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
""",
        "src_init": "package main\n\nfunc main() {\n\tprintln(\"Hello, world!\")\n}\n",
        "test_init": "",
        "config_file": "go.mod",
        "config_content": 'module {name}\n\ngo 1.21\n',
        "src_dir": "src",
    },
    "unknown": {
        "gitignore": """# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Build
dist/
build/
""",
        "src_init": "",
        "test_init": "",
        "config_file": None,
        "config_content": None,
        "src_dir": "src",
    },
}


def generate_greenfield_structure(project_root: Path, name: str, desc: str, language: str) -> Dict:
    """为绿地项目创建完整的项目骨架

    创建目录结构、README.md、.gitignore、配置文件、源码入口文件、测试入口文件。

    Args:
        project_root: 项目根目录
        name: 项目名称
        desc: 项目描述
        language: 开发语言（python/javascript/typescript/rust/go）

    Returns:
        已创建的文件列表
    """
    lang = language.lower()
    if lang not in LANGUAGE_CONFIGS:
        lang = "unknown"

    config = LANGUAGE_CONFIGS[lang]
    created_files = []

    # 确保根目录存在
    project_root.mkdir(parents=True, exist_ok=True)

    # 创建 docs 目录（design.py 会创建 design.md 和 changelog.md）
    docs_dir = project_root / "docs"
    docs_dir.mkdir(exist_ok=True)
    created_files.append(str(docs_dir))

    # 创建 src 目录和入口文件
    src_dir = project_root / config["src_dir"]
    src_dir.mkdir(exist_ok=True)
    created_files.append(str(src_dir))

    # 语言入口文件
    src_ext_map = {
        "python": "__init__.py",
        "javascript": "index.js",
        "typescript": "index.ts",
        "rust": "main.rs",
        "go": "main.go",
    }
    src_file = src_dir / src_ext_map.get(lang, "main.txt")
    if not src_file.exists():
        src_file.write_text(config["src_init"], encoding="utf-8")
        created_files.append(str(src_file))

    # 创建 tests 目录
    tests_dir = project_root / "tests"
    tests_dir.mkdir(exist_ok=True)
    created_files.append(str(tests_dir))

    # 测试入口文件
    test_file_name = {
        "python": "__init__.py",
        "javascript": "test.js",
        "typescript": "test.ts",
        "rust": "mod.rs",
    }.get(lang, "test.txt")
    test_file = tests_dir / test_file_name
    if not test_file.exists():
        test_file.write_text(config["test_init"], encoding="utf-8")
        created_files.append(str(test_file))

    # 创建 .gitignore
    gitignore_file = project_root / ".gitignore"
    if not gitignore_file.exists():
        gitignore_file.write_text(config["gitignore"], encoding="utf-8")
        created_files.append(str(gitignore_file))

    # 创建 README.md
    readme_file = project_root / "README.md"
    if not readme_file.exists():
        readme_content = f"""# {name}

{desc}

## 开始

```bash
# 安装依赖
# TODO: 根据语言添加安装命令

# 运行测试
# TODO: 根据语言添加测试命令

# 启动
# TODO: 根据语言添加启动命令
```

## 项目结构

```
├── {config['src_dir']}/      # 源代码
├── tests/           # 测试
├── docs/            # 设计文档
├── README.md
└── .gitignore
```

## 技术栈

- 语言：{language}
- 版本：0.1.0
"""
        readme_file.write_text(readme_content, encoding="utf-8")
        created_files.append(str(readme_file))

    # 创建语言配置文件
    if config["config_file"]:
        config_file = project_root / config["config_file"]
        if not config_file.exists():
            cfg_content = config["config_content"].format(name=name, desc=desc or name)
            config_file.write_text(cfg_content, encoding="utf-8")
            created_files.append(str(config_file))

    # 初始化 git 仓库
    if not (project_root / ".git").exists():
        success, _, stderr = run_git_command(["git", "init"], project_root)
        if success:
            print(f"✅ Git 仓库已初始化")
        else:
            print(f"⚠️  Git 初始化失败：{stderr}")

    return created_files


def generate_greenfield_design(name: str, desc: str, language: str, date_str: str) -> str:
    """生成绿地项目的 design.md 内容

    Args:
        name: 项目名称
        desc: 项目描述
        language: 开发语言
        date_str: 日期字符串（ISO格式）

    Returns:
        design.md 内容
    """
    lang_config = LANGUAGE_CONFIGS.get(language.lower(), LANGUAGE_CONFIGS["unknown"])

    return f"""# 产品设计文档

> 版本：0.1.0
> 创建日期：{date_str}
> 最后更新：{date_str}

## 1. 项目概述

**项目名称：** {name}
**开发语言：** {language}
**初始版本：** 0.1.0

> {desc}

<!-- 请补充项目整体描述、目标用户、核心价值主张 -->

## 2. 架构设计

<!-- 系统架构图、模块划分、技术栈选择 -->

### 项目结构

```
├── {lang_config['src_dir']}/      # 源代码
├── tests/           # 测试
├── docs/            # 设计文档
├── README.md
└── .gitignore
```

## 3. 数据模型

<!-- 数据库表结构、核心实体定义 -->

## 4. API 设计

<!-- 接口定义、请求/响应格式 -->

## 5. 安全设计

<!-- 认证、授权、加密、数据保护 -->

## 6. 配置与部署

<!-- 环境配置、部署方式、运维要求 -->

## 7. 非功能性需求

<!-- 性能、可用性、兼容性、可扩展性 -->
"""


# =============================================================================
# 任务表格模板（保持向后兼容）
# =============================================================================


if __name__ == "__main__":
    setup_unicode_output()
    root = find_project_root()
    changes = get_changes_dir(Path(__file__).resolve().parent)
    print(f"项目根目录：{root}")
    print(f"Changes 目录：{changes}")
    print(f"Docs 目录：{get_docs_dir()}")
    print(f"当前版本：{read_version(get_docs_dir() / 'design.md') or '未设置'}")
