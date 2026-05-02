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
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# 解决 Windows 控制台 Unicode 输出问题
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


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


def ensure_on_develop_branch(project_root: Path) -> bool:
    """确保当前在 develop 分支"""
    success, current_branch, _ = run_git_command(["git", "branch", "--show-current"], project_root)
    if current_branch != "develop":
        print(f"⚠️  当前不在 develop 分支（当前：{current_branch}）")
        print(f"   请切换到 develop 分支后再验证")
        return False
    return True


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


def parse_tasks_from_status(status_content: str) -> List[dict]:
    """从 {name}-progress.md 中解析任务执行进度"""
    tasks = []
    
    # 查找任务执行进度表格
    in_task_section = False
    for line in status_content.split("\n"):
        if "#### 任务执行进度" in line:
            in_task_section = True
            continue
        if in_task_section:
            # 找到下一个标题或分隔符
            if line.startswith("####") or line.startswith("---"):
                break
            # 解析表格行（跳过表头和分隔符）
            if line.startswith("|") and not line.startswith("|------"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 6 and parts[1].isdigit():
                    tasks.append({
                        "id": parts[1],
                        "name": parts[2],
                        "start_time": parts[3],
                        "end_time": parts[4],
                        "status": parts[5],
                        "note": parts[6] if len(parts) > 6 else "",
                    })
    
    return tasks


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
    
    # 检查任务是否都已完成
    pending_tasks = [t for t in tasks if t["status"] != "✅"]
    if pending_tasks:
        print(f"⚠️  存在 {len(pending_tasks)} 个未完成任务：")
        for t in pending_tasks:
            print(f"   ⬜ 任务{t['id']}: {t['name']}")
        print()
    
    # 更新 {name}-progress.md 中的阶段4状态
    new_status = f"""### 阶段4：测试验证

| 字段 | 值 |
|------|-----|
| **状态** | 🔄 进行中 |
| **开始时间** | {datetime.now().strftime("%Y-%m-%d %H:%M")} |
| **完成时间** | - |

**涉及文档：**
| 文档 | 操作 | 说明 |
|------|------|------|
| - | - | - |

---

#### 系统集成测试

| 测试项 | 状态 | 说明 |
|--------|------|------|
| 模块接口测试 | ⏳ | 验证模块间调用正确 |
| 数据流转测试 | ⏳ | 验证数据完整流转 |
| 端到端测试 | ⏳ | 验证完整业务流程 |
| 异常处理测试 | ⏳ | 验证异常情况处理 |

---

#### 调试记录

| 时间 | 问题 | 根因 | 修复方案 | 状态 |
|------|------|------|----------|------|
| - | - | - | - | - |

---

#### 验证结果

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 集成测试通过 | ☐ | |
| 单元测试覆盖率 ≥ 90% | ☐ | |
| 代码风格检查通过 | ☐ | |
| Git 提交完成 | ☐ | |

---
"""
    
    # 更新 {name}-progress.md 中的阶段4部分
    lines = status_content.split("\n")
    new_lines = []
    in_stage4 = False
    skip_until_next_stage = False
    
    for i, line in enumerate(lines):
        if line.strip().startswith("### 阶段4：verify") or line.strip().startswith("### 阶段4"):
            in_stage4 = True
            new_lines.append(new_status)
            continue
        
        if in_stage4:
            # 跳过旧的阶段4内容直到下一个阶段
            if line.strip().startswith("### 阶段") and ("5" in line or "archive" in line.lower()):
                in_stage4 = False
                new_lines.append(line)
            elif line.strip().startswith("---") and i > 0 and "阶段4" not in lines[i-1]:
                # 如果不是阶段4的分隔符，恢复写入
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
    print("系统集成测试要点")
    print("=" * 60)
    print()
    print("1. 模块接口测试：验证模块间调用是否正确")
    print("2. 数据流转测试：验证数据完整流转")
    print("3. 端到端测试：验证完整业务流程")
    print("4. 异常处理测试：验证异常情况处理")
    print()
    print("详细说明请参考：./debugging-and-verification/SKILL.md")
    
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
    
    # 更新系统集成测试表
    test_map = {
        "1": ("模块接口测试", "module_interface"),
        "2": ("数据流转测试", "data_flow"),
        "3": ("端到端测试", "e2e"),
        "4": ("异常处理测试", "exception_handling"),
    }
    
    if test_type in test_map:
        test_name, test_key = test_map[test_type]
        status_icon = "✅" if test_status == "通过" else "❌"
        
        # 替换对应测试项的状态
        pattern = rf"(\| {test_name} \| )([⏳✅❌])(\|)"
        replacement = rf"\g<1>{status_icon}\g<3>"
        progress_content = re.sub(pattern, replacement, progress_content)
    
    # 如果是失败，添加到调试记录
    if test_status == "失败":
        print()
        root_cause = input("根因分析: ").strip()
        fix_solution = input("修复方案: ").strip()
        
        debug_record = f"| {datetime.now().strftime('%Y-%m-%d %H:%M')} | {description} | {root_cause} | {fix_solution} | 🔧 进行中 |"
        
        # 在调试记录表末尾添加新记录
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
    
    # 检查系统集成测试是否全部通过
    incomplete_tests = []
    for test_name in ["模块接口测试", "数据流转测试", "端到端测试", "异常处理测试"]:
        if f"| {test_name} | ⏳ |" in progress_content:
            incomplete_tests.append(test_name)
    
    if incomplete_tests:
        print(f"⚠️  以下测试尚未完成：")
        for test in incomplete_tests:
            print(f"   ⬜ {test}")
        print()
        response = input("是否继续完成验证？(y/N): ").strip().lower()
        if response != 'y':
            print("已取消。")
            return 1
    
    # 检查是否有未解决的调试问题
    if "| 🔧 进行中 |" in progress_content:
        print("⚠️  存在未解决的调试问题。")
        print()
        response = input("是否继续完成验证？(y/N): ").strip().lower()
        if response != 'y':
            print("已取消。")
            return 1
    
    # 更新阶段4状态为已完成
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
    
    # 更新当前阶段标记
    progress_content = re.sub(
        r"(\*\*当前阶段\*\* \| )([^|]+)( \|)",
        rf"\g<1>阶段4.5：等待用户批准 \g<3>",
        progress_content
    )
    
    progress_file.write_text(progress_content, encoding="utf-8")
    
    print(f"✅ 验证完成：{name}")
    print(f"   {name}-progress.md 已更新")
    print()
    
    # Git 提交
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

    # 确保在 develop 分支
    if not ensure_on_develop_branch(project_root):
        return False

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
    commit_message = f"chore: 完成阶段4 测试验证 {name}"
    success, _, stderr = run_git_command(["git", "commit", "-m", commit_message], project_root)
    if not success:
        print(f"⚠️  git commit 失败：{stderr}")
        return False
    
    print(f"✅ Git 已提交到 develop：{commit_message}")
    return True


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
