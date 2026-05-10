#!/usr/bin/env python3
"""vibe-coding 阶段3：代码执行（采用 TDD 模式）

用法：
    python scripts/execute.py --name add-dark-mode --action list
    python scripts/execute.py --name add-dark-mode --task 1 --action start
    python scripts/execute.py --name add-dark-mode --task 1 --action done
    python scripts/execute.py --name add-dark-mode --task 1 --action skip

功能：
    - 每个子任务完成时自动提交 Git
    - TDD 模式指导
    - 更新 progress.md 任务状态
"""

import argparse
import sys
from pathlib import Path

from common import (
    setup_unicode_output, find_project_root, get_changes_dir,
    run_git_command, ensure_on_develop_branch, is_git_repo,
    has_pending_changes, git_add_and_commit,
    parse_tasks_from_status, update_task_status
)


setup_unicode_output()


def git_commit_on_complete(task_id: str, task_name: str, changes_dir: Path) -> bool:
    """子任务完成时自动提交 Git 到 develop 分支"""
    project_root = changes_dir.parent.parent

    if not ensure_on_develop_branch(project_root):
        return False

    if not is_git_repo(project_root):
        print("⚠️  当前目录不是 Git 仓库，跳过 Git 提交")
        return False

    if not has_pending_changes(project_root):
        print("📝 没有需要提交的更改")
        return True

    if git_add_and_commit(project_root, f"feat: task-{task_id} {task_name}"):
        print(f"✅ Git 已提交到 develop：feat: task-{task_id} {task_name}")
        return True
    return False


def get_status_icon(status: str) -> str:
    icons = {"pending": "⬜", "done": "✅", "skipped": "⏭️"}
    return icons.get(status, "❓")


def get_status_label(status: str) -> str:
    labels = {"pending": "待执行", "done": "已完成", "skipped": "已跳过"}
    return labels.get(status, status)


def list_tasks(name: str, changes_dir: Path) -> int:
    """列出任务状态"""
    progress_file = changes_dir / f"{name}-progress.md"

    if not progress_file.exists():
        print(f"❌ {name}-progress.md 不存在：{progress_file}")
        print(f"   请先运行：python scripts/plans.py --name {name}")
        return 1

    progress_content = progress_file.read_text(encoding="utf-8")
    tasks = parse_tasks_from_status(progress_content)

    if not tasks:
        print(f"⚠️  未找到任务。请先在 {name}-progress.md 中定义任务。")
        return 1

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
    progress_file = changes_dir / f"{name}-progress.md"

    if not progress_file.exists():
        print(f"❌ {name}-progress.md 不存在：{progress_file}")
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
    print(f"   2. 不要添加功能、重构或「改进」超出测试范围的部分")
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
    """将任务标记为完成（TDD 合规检查）"""
    progress_file = changes_dir / f"{name}-progress.md"

    if not progress_file.exists():
        print(f"❌ {name}-progress.md 不存在：{progress_file}")
        return 1

    progress_content = progress_file.read_text(encoding="utf-8")
    tasks = parse_tasks_from_status(progress_content)
    task_info = next((t for t in tasks if t["id"] == task_id), None)
    task_name = task_info["name"] if task_info else f"任务{task_id}"

    print()
    print("=" * 60)
    print("📋 TDD 合规检查")
    print("=" * 60)
    print()
    print("请确认以下 TDD 流程已正确执行：")
    print()
    print("  🔴 红：是否先编写了失败的测试？")
    print("  🟢 绿：是否编写了最少代码使测试通过？")
    print("  🔵 重构：是否在绿色后进行了代码清理？")
    print("  📊 覆盖率：测试覆盖率是否达到 100%？")
    print()

    tdd_confirmed = input("确认已遵循 TDD 流程？(y/N): ").strip().lower()
    if tdd_confirmed != 'y':
        print()
        print("❌ TDD 合规检查未通过")
        print("   请先完成 TDD 流程再标记任务为完成")
        print()
        print("📋 正确流程：")
        print("   1. [红] 编写失败测试")
        print("   2. [绿] 编写最少代码通过测试")
        print("   3. [重构] 清理代码")
        print()
        print("   参考：./test-driven-development/SKILL.md")
        return 1

    updated = update_task_status(progress_file, task_id, "done")

    if not updated:
        print(f"⚠️  请在 {name}-progress.md 中手动更新任务状态为 ✅")

    print(f"✅ 任务完成：任务{task_id}")
    print()

    print("=" * 60)
    print("Git 提交")
    print("=" * 60)
    git_commit_on_complete(task_id, task_name, changes_dir)
    print()

    print(f"📌 记录 TDD 循环次数到 {name}-progress.md：")
    print(f"   - 红：__ 次")
    print(f"   - 绿：__ 次")
    print(f"   - 重构：__ 次")
    print()
    print(f"📌 记录测试用例数到 {name}-progress.md：")
    print(f"   - 正例：__ 个")
    print(f"   - 反例：__ 个")
    print(f"   - 边界值：__ 个")

    progress_content = progress_file.read_text(encoding="utf-8")
    tasks = parse_tasks_from_status(progress_content)
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
        print(f"📌 大阶段完成，请提交 Git 到 develop：")
        print(f"   git add . && git commit -m \"chore: 完成阶段3 代码执行 {name}\"")
        print(f"   git push origin develop")
        print()
        print(f"   下一步：python scripts/verify.py --name {name}")

    return 0


def skip_task(name: str, task_id: str, changes_dir: Path) -> int:
    """跳过任务"""
    progress_file = changes_dir / f"{name}-progress.md"

    if not progress_file.exists():
        print(f"❌ {name}-progress.md 不存在：{progress_file}")
        return 1

    updated = update_task_status(progress_file, task_id, "skip")

    if not updated:
        print(f"⚠️  请在 {name}-progress.md 中手动更新任务状态为 ⏭️")

    print(f"⏭️  任务已跳过：任务{task_id}")
    print(f"   原因：_______________")

    progress_content = progress_file.read_text(encoding="utf-8")
    tasks = parse_tasks_from_status(progress_content)
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
