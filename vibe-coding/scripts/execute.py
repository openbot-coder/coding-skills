#!/usr/bin/env python3
"""vibe-coding 阶段3：执行任务管理（采用 TDD 模式）

用法：
    python scripts/execute.py --name add-dark-mode --action list
    python scripts/execute.py --name add-dark-mode --task 1 --action start
    python scripts/execute.py --name add-dark-mode --task 1 --action done
    python scripts/execute.py --name add-dark-mode --task 1 --action skip

功能：
    - 每个子任务完成时自动提交 Git
    - TDD 模式指导
    - 更新 STATUS.md 任务状态
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# 解决 Windows 控制台 Unicode 输出问题
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
    """获取 changes 目录路径（默认：项目根目录/docs/changes）"""
    if custom_dir:
        return Path(custom_dir)
    # 默认路径：{项目根目录}/docs/changes
    project_root = find_project_root()
    return project_root / "docs" / "changes"


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


def git_commit_on_complete(task_id: str, task_name: str, changes_dir: Path) -> bool:
    """子任务完成时自动提交 Git"""
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
    commit_message = f"feat: task-{task_id} {task_name}"
    success, _, stderr = run_git_command(["git", "commit", "-m", commit_message], project_root)
    if not success:
        print(f"⚠️  git commit 失败：{stderr}")
        return False
    
    print(f"✅ Git 已提交：{commit_message}")
    return True


def parse_tasks_from_status(status_content: str) -> List[dict]:
    """从 STATUS.md 解析任务列表"""
    tasks = []
    # 查找任务清单表格
    in_task_table = False
    for line in status_content.split("\n"):
        if "| 序号 | 任务名称 |" in line and "功能点数" in line:
            in_task_table = True
            continue
        if in_task_table:
            if line.startswith("---") or line.startswith("**"):
                break
            # 匹配表格行
            match = re.match(r"\|\s*(\d+)\s*\|\s*([^\|]+)\s*\|", line)
            if match:
                tasks.append({
                    "id": match.group(1),
                    "name": match.group(2).strip(),
                    "status": "pending",
                })
    return tasks


def update_status_file(status_file: Path, task_id: str, action: str) -> bool:
    """更新 STATUS.md 中的任务状态"""
    if not status_file.exists():
        return False
    
    content = status_file.read_text(encoding="utf-8")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    # 查找并更新任务行
    lines = content.split("\n")
    new_lines = []
    updated = False
    
    for i, line in enumerate(lines):
        # 匹配任务行
        match = re.match(r"(\|\s*)(\d+)(\s*\|\s*[^\|]+\|\s*)[^\|]+(\s*\|\s*⏳)", line)
        if match and match.group(2) == task_id:
            if action == "done":
                new_line = f"{match.group(1)}{task_id}{match.group(3)}✅{match.group(4).replace('⏳', '')}"
                new_lines.append(new_line)
                updated = True
                continue
            elif action == "skip":
                new_line = f"{match.group(1)}{task_id}{match.group(3)}⏭️{match.group(4).replace('⏳', '')}"
                new_lines.append(new_line)
                updated = True
                continue
        
        # 更新最后更新时间
        if "**最后更新**" in line and not updated:
            new_lines[-1] = line.replace("-", timestamp)
        else:
            new_lines.append(line)
    
    if updated:
        status_file.write_text("\n".join(new_lines), encoding="utf-8")
    
    return updated


def get_status_icon(status: str) -> str:
    """获取状态图标"""
    icons = {"pending": "⬜", "done": "✅", "skipped": "⏭️"}
    return icons.get(status, "❓")


def get_status_label(status: str) -> str:
    """获取状态标签"""
    labels = {"pending": "待执行", "done": "已完成", "skipped": "已跳过"}
    return labels.get(status, status)


def list_tasks(name: str, changes_dir: Path) -> int:
    """列出任务状态"""
    status_file = changes_dir / "STATUS.md"

    if not status_file.exists():
        print(f"❌ STATUS.md 不存在：{status_file}")
        print(f"   请先运行：python scripts/plans.py --name {name}")
        return 1

    status_content = status_file.read_text(encoding="utf-8")
    tasks = parse_tasks_from_status(status_content)

    if not tasks:
        print(f"⚠️  未找到任务。请先在 STATUS.md 中定义任务。")
        return 1

    # 统计
    done_count = sum(1 for t in tasks if t["status"] == "done")
    pending_count = sum(1 for t in tasks if t["status"] == "pending")
    total = len(tasks)

    print(f"📋 任务清单：{name}")
    print(f"   进度：{done_count}/{total} 完成，{pending_count} 待执行")
    print()
    print(f"🔄 采用 TDD 模式：红 → 绿 → 重构")

    for task in tasks:
        icon = get_status_icon(task["status"])
        label = get_status_label(task["status"])
        print(f"   {icon} 任务{task['id']}: {task['name']} [{label}]")

    # 提示下一步
    next_pending = next((t for t in tasks if t["status"] == "pending"), None)
    if next_pending:
        print()
        print(f"📌 下一个待执行任务：任务{next_pending['id']}")
        print(f"   python scripts/execute.py --name {name} --task {next_pending['id']} --action start")
    elif pending_count == 0 and done_count > 0:
        print()
        print(f"🎉 所有任务已完成！下一步：")
        print(f"   python scripts/verify.py --name {name}")

    return 0


def start_task(name: str, task_id: str, changes_dir: Path) -> int:
    """开始执行任务（提示 TDD 流程）"""
    status_file = changes_dir / "STATUS.md"

    if not status_file.exists():
        print(f"❌ STATUS.md 不存在：{status_file}")
        return 1

    print(f"🚀 开始执行：任务{task_id}")
    print()
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🔴 TDD 模式 - 红：编写失败测试")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   1. 编写一个最小测试展示应该发生什么")
    print(f"   2. 测试用例必须覆盖：正例 + 反例 + 边界值")
    print(f"   3. 运行测试，确认失败（而非报错）")
    print()
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🟢 TDD 模式 - 绿：最少代码")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   1. 编写最简单的代码让测试通过")
    print(f"   2. 不要添加功能、重构或"改进"超出测试范围的部分")
    print(f"   3. 运行测试，确认全部通过")
    print()
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🔵 TDD 模式 - 重构：清理")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   1. 只在绿色之后重构")
    print(f"   2. 移除重复、改善命名、提取辅助函数")
    print(f"   3. 保持测试绿色，不要添加行为")
    print()
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📋 测试覆盖率要求：100%")
    print(f"   未覆盖行必须以 # UNCOVERED: [原因] 标注")
    print(f"   无法覆盖的代码需用户批准")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print(f"   完成后运行：")
    print(f"   python scripts/execute.py --name {name} --task {task_id} --action done")
    print()
    print(f"   如需跳过：")
    print(f"   python scripts/execute.py --name {name} --task {task_id} --action skip")

    return 0


def complete_task(name: str, task_id: str, changes_dir: Path) -> int:
    """将任务标记为完成"""
    status_file = changes_dir / "STATUS.md"

    if not status_file.exists():
        print(f"❌ STATUS.md 不存在：{status_file}")
        return 1

    # 获取任务名称用于 Git 提交
    status_content = status_file.read_text(encoding="utf-8")
    tasks = parse_tasks_from_status(status_content)
    task_info = next((t for t in tasks if t["id"] == task_id), None)
    task_name = task_info["name"] if task_info else f"任务{task_id}"

    updated = update_status_file(status_file, task_id, "done")

    if not updated:
        print(f"⚠️  请在 STATUS.md 中手动更新任务状态为 ✅")

    print(f"✅ 任务完成：任务{task_id}")
    print()
    
    # 自动提交 Git
    print("=" * 60)
    print("Git 提交")
    print("=" * 60)
    git_commit_on_complete(task_id, task_name, changes_dir)
    print()
    
    print(f"📌 记录 TDD 循环次数到 STATUS.md：")
    print(f"   - 红：__ 次")
    print(f"   - 绿：__ 次")
    print(f"   - 重构：__ 次")
    print()
    print(f"📌 记录测试用例数到 STATUS.md：")
    print(f"   - 正例：__ 个")
    print(f"   - 反例：__ 个")
    print(f"   - 边界值：__ 个")

    # 检查是否还有待执行任务
    status_content = status_file.read_text(encoding="utf-8")
    tasks = parse_tasks_from_status(status_content)
    pending = [t for t in tasks if t["status"] == "pending"]

    if pending:
        next_task = pending[0]
        print()
        print(f"📌 下一个待执行任务：任务{next_task['id']}")
        print(f"   python scripts/execute.py --name {name} --task {next_task['id']} --action start")
    else:
        done_count = sum(1 for t in tasks if t["status"] == "done")
        total = len(tasks)
        print()
        print(f"🎉 所有任务处理完毕！({done_count}/{total} 完成)")
        print()
        print(f"📌 大阶段完成，请提交 Git：")
        print(f"   git add . && git commit -m \"chore: 完成阶段3 execute {name}\"")
        print()
        print(f"   下一步：python scripts/verify.py --name {name}")

    return 0


def skip_task(name: str, task_id: str, changes_dir: Path) -> int:
    """跳过任务"""
    status_file = changes_dir / "STATUS.md"

    if not status_file.exists():
        print(f"❌ STATUS.md 不存在：{status_file}")
        return 1

    updated = update_status_file(status_file, task_id, "skip")

    if not updated:
        print(f"⚠️  请在 STATUS.md 中手动更新任务状态为 ⏭️")

    print(f"⏭️  任务已跳过：任务{task_id}")
    print(f"   原因：_______________")

    # 检查剩余任务
    status_content = status_file.read_text(encoding="utf-8")
    tasks = parse_tasks_from_status(status_content)
    pending = [t for t in tasks if t["status"] == "pending"]

    if pending:
        next_task = pending[0]
        print()
        print(f"📌 下一个待执行任务：任务{next_task['id']}")
        print(f"   python scripts/execute.py --name {name} --task {next_task['id']} --action start")
    else:
        print()
        print(f"   下一步：python scripts/verify.py --name {name}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="vibe-coding 阶段3：执行任务管理（采用 TDD 模式）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例：\n"
               "  python scripts/execute.py --name add-dark-mode --action list\n"
               "  python scripts/execute.py --name add-dark-mode --task 1 --action start\n"
               "  python scripts/execute.py --name add-dark-mode --task 1 --action done\n"
               "  python scripts/execute.py --name add-dark-mode --task 1 --action skip",
    )
    parser.add_argument("--name", required=True, help="变更名称")
    parser.add_argument("--task", default=None, help="任务编号（如 1）")
    parser.add_argument(
        "--action",
        choices=["list", "start", "done", "skip"],
        default="list",
        help="操作：list=列出任务，start=开始任务，done=完成任务，skip=跳过任务",
    )
    parser.add_argument("--dir", default=None, help="自定义 changes 目录路径")

    args = parser.parse_args()

    # start/done/skip 需要 --task
    if args.action != "list" and not args.task:
        print(f"❌ 操作 '{args.action}' 需要指定 --task 参数")
        return 1

    script_dir = Path(__file__).resolve().parent
    changes_dir = get_changes_dir(script_dir, args.dir)

    if not changes_dir.exists():
        print(f"❌ 变更目录不存在：{changes_dir}")
        print(f"   请先运行：python scripts/plans.py --name {args.name}")
        return 1

    if args.action == "list":
        return list_tasks(args.name, changes_dir)
    elif args.action == "start":
        return start_task(args.name, args.task, changes_dir)
    elif args.action == "done":
        return complete_task(args.name, args.task, changes_dir)
    elif args.action == "skip":
        return skip_task(args.name, args.task, changes_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
