#!/usr/bin/env python3
"""vibe-coding 阶段2：任务拆解

用法：
    python scripts/plans.py --name add-dark-mode

功能：
    - 基于设计文档更新 {name}-progress.md 中的阶段2内容
    - 不再生成单独的 plans.md 和 tasks.md 文件
    - 阶段完成时提交 Git
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


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
    # 默认路径：{项目根目录}/docs/vibe-coding/changes
    project_root = find_project_root()
    return project_root / "docs" / "vibe-coding" / "changes"


def run_git_command(args: list, cwd: Optional[Path] = None) -> tuple:
    """运行 git 命令"""
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


def git_commit(name: str, stage: str, changes_dir: Path) -> bool:
    """大阶段完成时提交 Git"""
    project_root = changes_dir.parent.parent
    
    # 检查是否有 Git 仓库
    success, _, _ = run_git_command(["git", "rev-parse", "--git-dir"], project_root)
    if not success:
        print("⚠️  当前目录不是 Git 仓库，跳过 Git 提交")
        return False
    
    # 检查是否有更改
    success, stdout, _ = run_git_command(["git", "status", "--porcelain"], project_root)
    if not stdout:
        print("📝 没有需要提交的更改")
        return True
    
    # 添加所有更改
    success, _, stderr = run_git_command(["git", "add", "."], project_root)
    if not success:
        print(f"⚠️  git add 失败：{stderr}")
        return False
    
    # 提交
    commit_message = f"chore: 完成{stage} {name}"
    success, _, stderr = run_git_command(["git", "commit", "-m", commit_message], project_root)
    if not success:
        print(f"⚠️  git commit 失败：{stderr}")
        return False
    
    print(f"✅ Git 已提交：{commit_message}")
    return True


def read_design(change_dir: Path, name: str) -> str:
    """读取设计内容作为上下文参考"""
    design_file = change_dir / f"{name}-design.md"
    if design_file.exists():
        return design_file.read_text(encoding="utf-8")
    return ""


def extract_design_summary(design_content: str) -> str:
    """从设计中提取目标作为提示"""
    if not proposal_content:
        return ""
    
    lines = proposal_content.strip().split("\n")
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
    
    # 更新基本信息和当前阶段
    lines = content.split("\n")
    new_lines = []
    in_plans_section = False
    updated = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # 更新最后更新时间
        if "**最后更新**" in line and "阶段2" not in line:
            new_lines[-1] = line.replace("-", timestamp)
        
        # 标记阶段2开始
        if "### 阶段2：任务拆解" in line:
            in_plans_section = True
            continue
        
        # 更新阶段2状态
        if in_plans_section and "**状态** | ⏳" in line and "**开始时间**" not in lines[i-1]:
            new_lines[-1] = line.replace("⏳", "⏳ 进行中")
            updated = True
        
        # 更新开始时间
        if in_plans_section and "**开始时间** | -" in line:
            new_lines[-1] = line.replace("-", timestamp)
        
        # 标记阶段2结束
        if in_plans_section and line.startswith("### 阶段3"):
            in_plans_section = False
    
    if updated:
        status_file.write_text("\n".join(new_lines), encoding="utf-8")
    
    return updated


def create_plans(name: str, changes_dir: Path) -> int:
    """基于设计制定实施计划"""
    change_dir = changes_dir / name
    progress_file = changes_dir / f"{name}-progress.md"
    status_file = progress_file  # 兼容旧变量名

    # 检查变更目录是否存在
    if not change_dir.exists():
        print(f"❌ 变更目录不存在：{change_dir}")
        print(f"   请先创建设计文档")
        return 1

    # 读取设计内容
    design_content = read_design(change_dir, name)
    design_summary = extract_design_summary(design_content)

    # 更新 {name}-progress.md
    updated = update_status_for_plans(status_file, name, design_summary)

    # 输出结果
    print(f"✅ 阶段2：任务拆解 已启动")
    print(f"📁 变更目录：{change_dir}")
    print(f"📋 进度文件：{progress_file}")
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