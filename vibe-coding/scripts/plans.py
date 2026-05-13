#!/usr/bin/env python3
"""vibe-coding 阶段2：任务拆解

用法：
    python scripts/plans.py --name add-dark-mode

功能：
    - 基于设计文档更新 {name}-progress.md 中的阶段2内容
    - 不再生成单独的 plans.md 和 tasks.md 文件
    - 阶段完成时提交 Git

参考：./task-breakdown/SKILL.md - 任务拆解子技能
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from common import (
    setup_unicode_output, find_project_root, get_changes_dir, get_docs_dir,
    run_git_command, is_git_repo, has_pending_changes, git_add_and_commit,
    read_version, update_last_updated,
)


setup_unicode_output()


def git_commit(name: str, stage: str, changes_dir: Path) -> bool:
    """大阶段完成时提交 Git"""
    project_root = changes_dir.parent.parent

    if not is_git_repo(project_root):
        print("⚠️  当前目录不是 Git 仓库，跳过 Git 提交")
        return False

    if not has_pending_changes(project_root):
        print("📝 没有需要提交的更改")
        return True

    if git_add_and_commit(project_root, f"chore: 完成{stage} {name}"):
        print(f"✅ Git 已提交：chore: 完成{stage} {name}")
        return True
    return False


def read_design(change_dir: Path, name: str) -> str:
    """读取设计内容作为上下文参考"""
    design_file = change_dir / f"{name}-design.md"
    if design_file.exists():
        return design_file.read_text(encoding="utf-8")
    return ""


def read_central_design(docs_dir: Path) -> str:
    """读取中央 design.md（方案 B）"""
    design_file = docs_dir / "design.md"
    if design_file.exists():
        return design_file.read_text(encoding="utf-8")
    return ""


def extract_design_summary(design_content: str) -> str:
    """从设计中提取目标作为提示"""
    if not design_content:
        return ""

    lines = design_content.strip().split("\n")
    goal_hint = []
    in_goal = False

    for line in lines:
        if "## 目标" in line:
            in_goal = True
            continue
        if in_goal:
            if line.startswith("## "):
                break
            if line.strip() and not line.strip().startswith("<!--"):
                goal_hint.append(line.strip())

    return " ".join(goal_hint[:3]) if goal_hint else ""


def update_status_for_plans(status_file: Path, name: str, proposal_summary: str) -> bool:
    """更新 {name}-progress.md 中的阶段2内容"""
    if not status_file.exists():
        print(f"❌ {name}-progress.md 不存在：{status_file}")
        print(f"   请先确保变更目录存在")
        return False

    content = status_file.read_text(encoding="utf-8")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    lines = content.split("\n")
    new_lines = []
    in_plans_section = False
    updated = False

    for i, line in enumerate(lines):
        new_lines.append(line)

        if "**最后更新**" in line and "阶段2" not in line:
            new_lines[-1] = line.replace("-", timestamp)

        if "### 阶段2：任务拆解" in line:
            in_plans_section = True
            continue

        if in_plans_section and "**状态** | ⏳" in line and "**开始时间**" not in lines[i-1]:
            new_lines[-1] = line.replace("⏳", "⏳ 进行中")
            updated = True

        if in_plans_section and "**开始时间** | -" in line:
            new_lines[-1] = line.replace("-", timestamp)

        if in_plans_section and line.startswith("### 阶段3"):
            in_plans_section = False

    if updated:
        status_file.write_text("\n".join(new_lines), encoding="utf-8")

    return updated


def create_plans(name: str, changes_dir: Path) -> int:
    """基于设计制定实施计划"""
    change_dir = changes_dir / name
    progress_file = changes_dir / f"{name}-progress.md"

    if not change_dir.exists():
        print(f"❌ 变更目录不存在：{change_dir}")
        print(f"   请先创建设计文档")
        return 1

    # 优先读取独立变更设计文档，其次读取中央 design.md
    design_content = read_design(change_dir, name)
    design_source = "独立变更设计文档"

    if not design_content:
        docs_dir = get_docs_dir(Path(__file__).resolve().parent)
        design_content = read_central_design(docs_dir)
        if design_content:
            design_source = "中央 design.md"

    design_summary = extract_design_summary(design_content)

    updated = update_status_for_plans(progress_file, name, design_summary)

    # 更新中央 design.md 的最后更新日期
    docs_dir = get_docs_dir(Path(__file__).resolve().parent)
    central_design = docs_dir / "design.md"
    if central_design.exists():
        update_last_updated(central_design)

    print(f"✅ 阶段2：任务拆解 已启动")
    print(f"📁 变更目录：{change_dir}")
    print(f"📋 进度文件：{progress_file}")
    if design_source == "中央 design.md":
        version = read_version(central_design)
        print(f"📖 设计来源：{design_source}（v{version or '未知'}）")
    else:
        print(f"📖 设计来源：{design_source}")
    print()

    if design_summary:
        print(f"📖 设计文档目标参考：{design_summary}")

    print(f"📋 下一步：")
    print(f"   1. 编辑 {name}-progress.md 中阶段2的计划概述")
    print(f"   2. 填充任务清单（每个任务 10~20 个功能点）")
    print(f"   3. 填充任务详情（功能列表、验证方式）")
    print(f"   4. 计划完整后，运行：")
    print(f"      python scripts/execute.py --name {name} --action list")
    print()

    print("=" * 60)
    print("Git 提交")
    print("=" * 60)
    git_commit(name, "阶段2 任务拆解", changes_dir)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="vibe-coding 阶段2：任务拆解",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例：\n"
               "  python scripts/plans.py --name add-dark-mode",
    )
    parser.add_argument("--name", required=True, help="变更名称")
    parser.add_argument("--dir", default=None, help="自定义 changes 目录路径")

    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    changes_dir = get_changes_dir(script_dir, args.dir)

    return create_plans(args.name, changes_dir)


if __name__ == "__main__":
    sys.exit(main())
