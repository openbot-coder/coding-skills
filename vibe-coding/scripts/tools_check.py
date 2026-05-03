#!/usr/bin/env python3
"""vibe-coding 工具检查：验证必需工具是否已安装

用法：
    python scripts/tools_check.py

功能：
    - 检查必需的基础工具（ripgrep, git, graphify）
    - 检测项目开发所需的语言特定工具
    - 输出检查结果和建议
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


# 必需的基础工具
REQUIRED_CORE_TOOLS = {
    "git": {
        "command": ["git", "--version"],
        "required": True,
        "install_hint": "https://git-scm.com/downloads",
        "description": "版本控制"
    },
    "ripgrep": {
        "command": ["rg", "--version"],
        "required": True,
        "install_hint": "winget install BurntSushi.ripgrep",
        "description": "代码搜索"
    },
}

# 可选的代码库分析工具
OPTIONAL_ANALYSIS_TOOLS = {
    "graphify": {
        "commands": [
            ["graphify", "--help"],
        ],
        "required": False,
        "install_hint": "uv tool install graphifyy && graphify install",
        "description": "代码库结构分析"
    },
    "sourcegraph": {
        "commands": [["sg", "--version"]],
        "required": False,
        "install_hint": "https://sourcegraph.com",
        "description": "代码搜索和分析"
    },
}

# 项目开发工具（按语言自动检测）
LANGUAGE_TOOLS = {
    "python": {
        "detectors": ["pyproject.toml", "setup.py", "requirements.txt"],
        "tools": {
            "python": {
                "commands": [["python", "--version"], ["python3", "--version"]],
                "install_hint": "winget install Python.Python.3.11",
                "description": "Python 解释器"
            },
            "uv": {
                "commands": [["uv", "--version"]],
                "install_hint": "winget install uv",
                "description": "Python 包管理器"
            },
            "pytest": {
                "commands": [["pytest", "--version"]],
                "install_hint": "uv pip install pytest",
                "description": "单元测试"
            },
            "ruff": {
                "commands": [["ruff", "--version"]],
                "install_hint": "uv pip install ruff",
                "description": "代码检查和格式化"
            },
        }
    },
    "javascript": {
        "detectors": ["package.json"],
        "tools": {
            "npm": {
                "commands": [["npm", "--version"]],
                "install_hint": "winget install npm",
                "description": "Node.js 包管理"
            },
            "pnpm": {
                "commands": [["pnpm", "--version"]],
                "install_hint": "npm install -g pnpm",
                "description": "快速的包管理器"
            },
            "eslint": {
                "commands": [["npx", "eslint", "--version"]],
                "install_hint": "npm install -D eslint",
                "description": "JavaScript 代码检查"
            },
        }
    },
    "typescript": {
        "detectors": ["tsconfig.json"],
        "tools": {
            "typescript": {
                "commands": [["npx", "tsc", "--version"]],
                "install_hint": "npm install -D typescript",
                "description": "TypeScript 编译器"
            },
            "prettier": {
                "commands": [["npx", "prettier", "--version"]],
                "install_hint": "npm install -D prettier",
                "description": "代码格式化"
            },
        }
    },
    "rust": {
        "detectors": ["Cargo.toml"],
        "tools": {
            "cargo": {
                "commands": [["cargo", "--version"]],
                "install_hint": "https://rustup.rs",
                "description": "Rust 包管理器"
            },
            "rustfmt": {
                "commands": [["rustfmt", "--version"]],
                "install_hint": "rustup component add rustfmt",
                "description": "Rust 代码格式化"
            },
            "clippy": {
                "commands": [["cargo", "clippy", "--version"]],
                "install_hint": "rustup component add clippy",
                "description": "Rust 代码检查"
            },
        }
    },
    "go": {
        "detectors": ["go.mod"],
        "tools": {
            "go": {
                "commands": [["go", "version"]],
                "install_hint": "https://go.dev/dl/",
                "description": "Go 编译器"
            },
            "gofmt": {
                "commands": [["gofmt", "--version"]],
                "install_hint": "随 Go 安装",
                "description": "Go 代码格式化"
            },
        }
    },
}


def find_project_root() -> Path:
    """从当前工作目录向上查找项目根目录"""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
        return cwd


def detect_project_languages(project_root: Path) -> list[str]:
    """检测项目使用的编程语言"""
    detected = []
    for lang, config in LANGUAGE_TOOLS.items():
        for detector in config["detectors"]:
            if (project_root / detector).exists():
                if lang not in detected:
                    detected.append(lang)
                break
    return detected


def check_command(commands: list[list[str]]) -> tuple[bool, str]:
    """检查命令是否可用"""
    for cmd in commands:
        program = shutil.which(cmd[0])
        if program:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=10,
                )
                if result.returncode == 0:
                    # 提取版本信息
                    version = result.stdout.strip().split('\n')[0] if result.stdout else "OK"
                    return True, version
            except (subprocess.TimeoutExpired, Exception):
                pass
    return False, ""


def print_section(title: str) -> None:
    """打印分节标题"""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_tool_status(name: str, status: str, description: str, hint: Optional[str] = None) -> None:
    """打印工具状态"""
    icon = "✅" if status == "installed" else "❌"
    print(f"  {icon} {name:<20} {description}")
    if status != "installed" and hint:
        print(f"     安装命令: {hint}")


def main() -> int:
    project_root = find_project_root()
    print(f"📂 项目目录: {project_root}")
    
    all_required_ok = True
    
    # 1. 检查必需的核心工具
    print_section("必需工具检查")
    for name, config in REQUIRED_CORE_TOOLS.items():
        ok, version = check_command([config["command"]])
        status = "installed" if ok else "missing"
        if not ok and config["required"]:
            all_required_ok = False
        print_tool_status(
            name, 
            status, 
            config["description"],
            config["install_hint"] if not ok else None
        )
        if ok:
            print(f"     {version}")
    
    # 2. 检查可选的分析工具
    print_section("代码分析工具检查")
    for name, config in OPTIONAL_ANALYSIS_TOOLS.items():
        ok, version = check_command(config["commands"])
        status = "installed" if ok else "missing"
        if not ok:
            print_tool_status(name, status, config["description"], config["install_hint"])
        else:
            print_tool_status(name, status, config["description"])
            print(f"     {version}")
    
    # 3. 检测项目语言并检查相关工具
    detected_languages = detect_project_languages(project_root)
    
    if detected_languages:
        print_section(f"项目开发工具检查 ({', '.join(detected_languages)})")
        
        for lang in detected_languages:
            print(f"\n  [{lang}]")
            lang_config = LANGUAGE_TOOLS[lang]
            for tool_name, tool_config in lang_config["tools"].items():
                ok, version = check_command(tool_config["commands"])
                status = "installed" if ok else "missing"
                if not ok:
                    all_required_ok = False
                print_tool_status(
                    tool_name, 
                    status, 
                    tool_config["description"],
                    tool_config["install_hint"] if not ok else None
                )
                if ok:
                    print(f"     {version}")
    else:
        print_section("项目开发工具检查")
        print("  ⚠️  未检测到项目语言类型")
        print("     请确认项目根目录是否包含以下文件：")
        print("     - Python: pyproject.toml, setup.py, requirements.txt")
        print("     - JavaScript/TypeScript: package.json, tsconfig.json")
        print("     - Rust: Cargo.toml")
        print("     - Go: go.mod")
    
    # 4. 输出总结
    print_section("检查总结")
    if all_required_ok:
        print("  ✅ 所有必需工具已安装")
        return 0
    else:
        print("  ⚠️  部分必需工具缺失")
        print()
        print("  请安装缺失的工具后重新运行初始化")
        return 1


if __name__ == "__main__":
    sys.exit(main())
