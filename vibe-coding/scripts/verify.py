#!/usr/bin/env python3
"""vibe-coding 阶段4：测试验证

用法：
    python scripts/verify.py --name <变更名称> --action start   # 开始验证
    python scripts/verify.py --name <变更名称> --action log     # 记录验证结果
    python scripts/verify.py --name <变更名称> --action done   # 完成验证

参考：debugging-and-verification 子技能
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

from common import (
    setup_unicode_output, find_project_root, get_changes_dir,
    run_git_command, ensure_on_develop_branch, is_git_repo,
    has_pending_changes, git_add_and_commit,
    parse_tasks_from_status
)


setup_unicode_output()


def start_verification(name: str, changes_dir: Path) -> int:
    """开始验证阶段"""
    progress_file = changes_dir / f"{name}-progress.md"

    if not progress_file.exists():
        print(f"❌ {name}-progress.md 不存在：{progress_file}")
        print(f"   请先完成阶段2和阶段3：")
        print(f"   python scripts/plans.py --name {name}")
        return 1

    progress_content = progress_file.read_text(encoding="utf-8")
    tasks = parse_tasks_from_status(progress_content)

    if not tasks:
        print(f"⚠️  未找到任务。请先完成阶段3（代码执行）。")
        return 1

    pending_tasks = [t for t in tasks if t["status"] != "✅"]
    if pending_tasks:
        print(f"⚠️  存在 {len(pending_tasks)} 个未完成任务：")
        for t in pending_tasks:
            print(f"   ⬜ 任务{t['id']}: {t['name']}")
        print()

    new_status = f"""### 阶段4：测试验证

| 字段 | 值 |
|------|------|
| **状态** | 🔄 进行中 |
| **开始时间** | {datetime.now().strftime("%Y-%m-%d %H:%M")} |
| **完成时间** | - |

---

### 单元测试（所有任务实现后统一编写）

| 任务 | 正例数 | 反例数 | 边界值数 | 覆盖率 | 状态 |
|------|--------|--------|----------|--------|------|
| - | - | - | - | - | ⏳ |

---

### 系统集成测试

| 测试项 | 状态 | 测试日期 | 说明 |
|--------|------|----------|------|
| 模块接口测试 | ⏳ | - | 验证模块间调用正确 |
| 数据流转测试 | ⏳ | - | 验证数据完整流转 |
| 端到端测试 | ⏳ | - | 验证完整业务流程 |
| 异常处理测试 | ⏳ | - | 验证异常情况处理 |

---

### 调试记录

| 时间 | 问题描述 | 根因 | 修复方案 | 状态 |
|------|----------|------|----------|------|
| - | - | - | - | - |

---

### 验证结果

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 单元测试覆盖率 100% | ☐ | |
| 正例 + 反例 + 边界值覆盖 | ☐ | |
| 集成测试通过 | ☐ | |
| 代码风格检查通过 | ☐ | |
| Git 提交完成 | ☐ | |

---

"""

    lines = progress_content.split("\n")
    new_lines = []
    in_stage4 = False

    for i, line in enumerate(lines):
        if line.strip().startswith("### 阶段4：verify") or line.strip().startswith("### 阶段4"):
            in_stage4 = True
            new_lines.append(new_status)
            continue

        if in_stage4:
            if line.strip().startswith("### 阶段") and ("5" in line or "archive" in line.lower()):
                in_stage4 = False
                new_lines.append(line)
            elif line.strip().startswith("---") and i > 0 and "阶段4" not in lines[i-1]:
                pass
            elif not line.strip():
                pass
            else:
                continue
        else:
            new_lines.append(line)

    progress_file.write_text("\n".join(new_lines), encoding="utf-8")

    print(f"✅ 已开始验证：{name}")
    print(f"   {name}-progress.md 已更新")
    print()

    print("=" * 60)
    print("验证流程")
    print("=" * 60)
    print()
    print("1. 先确认所有任务的单元测试已编写完成（覆盖率100%）")
    print("2. 运行全部单元测试，确保通过")
    print("3. 进行系统集成测试：")
    print("   模块接口测试：验证模块间调用是否正确")
    print("   数据流转测试：验证数据完整流转")
    print("   端到端测试：验证完整业务流程")
    print("   异常处理测试：验证异常情况处理")
    print()
    print("详细说明请参考：./debugging-and-verification/SKILL.md")
    print("SDD 单元测试参考：./sdd-unit-development/SKILL.md")

    return 0


def log_verification_result(name: str, changes_dir: Path) -> int:
    """记录验证结果到 {name}-progress.md"""
    progress_file = changes_dir / f"{name}-progress.md"

    if not progress_file.exists():
        print(f"❌ {name}-progress.md 不存在：{progress_file}")
        return 1

    print(f"记录验证结果到 {name}-progress.md")
    print()
    print("请输入以下信息：")
    print()

    test_type = input("测试类型 (1.模块接口 2.数据流转 3.端到端 4.异常处理): ").strip()
    test_status = input("测试状态 (通过/失败): ").strip()
    description = input("测试说明: ").strip()

    progress_content = progress_file.read_text(encoding="utf-8")

    test_map = {
        "1": ("模块接口测试", "module_interface"),
        "2": ("数据流转测试", "data_flow"),
        "3": ("端到端测试", "e2e"),
        "4": ("异常处理测试", "exception_handling"),
    }

    if test_type in test_map:
        test_name, test_key = test_map[test_type]
        status_icon = "✅" if test_status == "通过" else "❌"

        pattern = rf"(\| {test_name} \| )([⏳✅❌])(\|)"
        replacement = rf"\g<1>{status_icon}\g<3>"
        progress_content = re.sub(pattern, replacement, progress_content)

    if test_status == "失败":
        print()
        root_cause = input("根因分析: ").strip()
        fix_solution = input("修复方案: ").strip()

        debug_record = f"| {datetime.now().strftime('%Y-%m-%d %H:%M')} | {description} | {root_cause} | {fix_solution} | 🔧 进行中 |"

        progress_content = progress_content.replace(
            "| - | - | - | - | - |",
            f"| - | - | - | - | - |\n{debug_record}"
        )

    progress_file.write_text(progress_content, encoding="utf-8")
    print()
    print(f"✅ 验证结果已记录到 {name}-progress.md")

    return 0


def complete_verification(name: str, changes_dir: Path) -> int:
    """完成验证阶段"""
    progress_file = changes_dir / f"{name}-progress.md"

    if not progress_file.exists():
        print(f"❌ {name}-progress.md 不存在：{progress_file}")
        return 1

    progress_content = progress_file.read_text(encoding="utf-8")

    incomplete_tests = []
    for test_name in ["模块接口测试", "数据流转测试", "端到端测试", "异常处理测试"]:
        if f"| {test_name} | ⏳ |" in progress_content:
            incomplete_tests.append(test_name)

    if incomplete_tests:
        print(f"❌ 以下测试尚未完成：")
        for test in incomplete_tests:
            print(f"   ⬜ {test}")
        print()
        print("⚠️  验证未通过，必须完成所有测试才能继续")
        print("   请先完成测试，运行：")
        print(f"   python scripts/verify.py --name {name} --action log")
        print()
        print("📋 正确流程：发现问题 → 立即报告用户 → 修复 → 重新测试")
        return 1

    if "| 🔧 进行中 |" in progress_content:
        print("❌ 存在未解决的调试问题")
        print()
        print("⚠️  验证未通过，必须解决所有问题才能继续")
        print("   请先解决调试问题，运行：")
        print(f"   python scripts/verify.py --name {name} --action log")
        print()
        print("📋 正确流程：发现问题 → 立即报告用户 → 修复 → 重新测试")
        return 1

    progress_content = re.sub(
        r"(\| \*\*状态\*\* \| )([^|]+)( \|)",
        rf"\g<1>✅ 已完成 \g<3>",
        progress_content
    )
    progress_content = re.sub(
        r"(\| \*\*完成时间\*\* \| )([^|]+)( \|)",
        rf"\g<1>{datetime.now().strftime('%Y-%m-%d %H:%M')} \g<3>",
        progress_content
    )
    progress_content = re.sub(
        r"(\*\*当前阶段\*\* \| )([^|]+)( \|)",
        rf"\g<1>阶段4.5：等待用户批准 \g<3>",
        progress_content
    )

    progress_file.write_text(progress_content, encoding="utf-8")

    print(f"✅ 验证完成：{name}")
    print(f"   {name}-progress.md 已更新")
    print()

    print("=" * 60)
    print("Git 提交")
    print("=" * 60)
    git_commit(name, changes_dir)
    print()

    print("=" * 60)
    print("下一步操作")
    print("=" * 60)
    print()
    print(f"⚠️  验证已通过，需要用户批准后才能归档")
    print()
    print(f"📋 请向用户展示验证结果，请求批准")
    print()
    print(f"   用户批准后，运行：python scripts/archive.py --name {name}")

    return 0


def git_commit(name: str, changes_dir: Path) -> bool:
    """大阶段完成时提交 Git 到 develop 分支"""
    project_root = changes_dir.parent.parent

    if not ensure_on_develop_branch(project_root):
        return False

    if not is_git_repo(project_root):
        print("⚠️  当前目录不是 Git 仓库，跳过 Git 提交")
        return False

    if not has_pending_changes(project_root):
        print("📝 没有需要提交的更改")
        return True

    if git_add_and_commit(project_root, f"chore: 完成阶段4 测试验证 {name}"):
        print(f"✅ Git 已提交到 develop：chore: 完成阶段4 测试验证 {name}")
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="vibe-coding 阶段4：验证执行结果",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python scripts/verify.py --name add-dark-mode --action start
  python scripts/verify.py --name add-dark-mode --action log
  python scripts/verify.py --name add-dark-mode --action done
        """,
    )
    parser.add_argument("--name", required=True, help="变更名称")
    parser.add_argument(
        "--action",
        choices=["start", "log", "done"],
        default="start",
        help="start: 开始验证 / log: 记录结果 / done: 完成验证",
    )
    parser.add_argument("--dir", default=None, help="自定义 changes 目录路径")

    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    changes_dir = get_changes_dir(script_dir, args.dir)

    if args.action == "start":
        return start_verification(args.name, changes_dir)
    elif args.action == "log":
        return log_verification_result(args.name, changes_dir)
    else:
        return complete_verification(args.name, changes_dir)


if __name__ == "__main__":
    sys.exit(main())
