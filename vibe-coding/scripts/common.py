#!/usr/bin/env python3
"""vibe-coding 公共工具模块

提供项目根目录查找、changes 目录管理、Git 操作、任务表格模板等公共功能。
"""

import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional


def setup_unicode_output():
    """解决 Windows 控制台 Unicode 输出问题"""
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def find_project_root() -> Path:
    """从当前工作目录向上查找项目根目录（包含 .git 或 pyproject.toml）"""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    return cwd


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


if __name__ == "__main__":
    setup_unicode_output()
    root = find_project_root()
    changes = get_changes_dir(Path(__file__).resolve().parent)
    print(f"项目根目录：{root}")
    print(f"Changes 目录：{changes}")
