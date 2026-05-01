#!/usr/bin/env python3
"""vibe-coding 阶段5：归档已完成工作

用法：
    python scripts/archive.py --name <变更名称>    # 归档变更
    python scripts/archive.py --list               # 列出已归档变更

功能：
    - 提交 Git
    - 推送到远程仓库
    - 询问是否打标签
    - 移动变更目录到 archive/
"""

import argparse
import subprocess
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

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


def git_commit(name: str, changes_dir: Path) -> bool:
    """提交 Git"""
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
        return False
    
    # 添加所有更改
    success, _, stderr = run_git_command(["git", "add", "."], project_root)
    if not success:
        print(f"❌ git add 失败：{stderr}")
        return False
    
    # 提交
    commit_message = f"chore: 完成变更 {name}"
    success, _, stderr = run_git_command(["git", "commit", "-m", commit_message], project_root)
    if not success:
        print(f"❌ git commit 失败：{stderr}")
        return False
    
    print(f"✅ Git 已提交：{commit_message}")
    return True


def git_push(project_root: Path) -> bool:
    """推送到远程仓库"""
    # 检查远程仓库
    success, stdout, _ = run_git_command(["git", "remote"], project_root)
    if not stdout:
        print("⚠️  没有远程仓库，跳过推送")
        return False
    
    # 推送
    success, _, stderr = run_git_command(["git", "push"], project_root)
    if not success:
        print(f"⚠️  git push 失败：{stderr}")
        return False
    
    print("✅ 已推送到远程仓库")
    return True


def create_tag(name: str, project_root: Path) -> bool:
    """创建标签"""
    # 生成默认标签名
    default_tag = f"v1.0/{name}"
    
    print()
    response = input(f"是否需要打标签？(直接回车使用默认格式 v1.0/{name}，输入 n 跳过): ").strip()
    
    if response.lower() == 'n':
        print("跳过打标签")
        return False
    
    tag_name = response if response else default_tag
    
    # 创建标签
    success, _, stderr = run_git_command(["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"], project_root)
    if not success:
        print(f"⚠️  创建标签失败：{stderr}")
        return False
    
    # 推送标签
    success, _, stderr = run_git_command(["git", "push", "origin", tag_name], project_root)
    if not success:
        print(f"⚠️  推送标签失败：{stderr}")
        return False
    
    print(f"✅ 已创建并推送标签：{tag_name}")
    return True


def check_archive_conditions(status_file: Path) -> tuple:
    """检查归档条件"""
    if not status_file.exists():
        return False, "STATUS.md 不存在"
    
    status_content = status_file.read_text(encoding="utf-8")
    
    # 检查阶段4是否完成
    if "| ✅ 已完成 |" not in status_content and "| 已完成 |" not in status_content:
        # 检查是否有待完成的验证
        if "🔄 进行中" in status_content:
            return False, "阶段4验证尚未完成"
    
    return True, ""


def archive_change(name: str, changes_dir: Path) -> int:
    """归档已完成变更"""
    change_dir = changes_dir / name
    archive_dir = changes_dir / "archive"
    status_file = changes_dir / "STATUS.md"

    # 检查变更是否存在
    if not change_dir.exists():
        print(f"❌ 变更 '{name}' 不存在：{change_dir}")
        print(f"   请确认变更名称是否正确")
        return 1

    # 检查归档条件
    can_archive, reason = check_archive_conditions(status_file)
    if not can_archive:
        print(f"⚠️  归档条件不满足：{reason}")
        response = input("是否仍要归档？(y/N): ").strip().lower()
        if response != 'y':
            return 1

    project_root = changes_dir.parent.parent

    # Git 提交
    print("=" * 60)
    print("Git 操作")
    print("=" * 60)
    git_commit(name, changes_dir)
    
    # 推送到远程
    git_push(project_root)
    
    # 询问是否打标签
    create_tag(name, project_root)

    # 创建 archive 目录
    archive_dir.mkdir(parents=True, exist_ok=True)

    # 检查是否已在 archive 中
    archive_target = archive_dir / name
    if archive_target.exists():
        print(f"❌ 归档目录已存在：{archive_target}")
        print(f"   请手动处理冲突")
        return 1

    # 移动目录
    shutil.move(str(change_dir), str(archive_target))

    # 列出归档内容
    archived_files = list(archive_target.iterdir())
    file_names = [f.name for f in archived_files]

    print()
    print("=" * 60)
    print("归档完成")
    print("=" * 60)
    print(f"✅ 变更 '{name}' 已归档")
    print(f"   位置：{archive_target}")
    print(f"   文件：{', '.join(sorted(file_names))}")
    print()
    print(f"🎉 工作流完成！可以开始新的变更：")
    print(f"   python scripts/propose.py --name <新变更名称>")

    return 0


def list_archived(changes_dir: Path) -> int:
    """列出已归档的变更"""
    archive_dir = changes_dir / "archive"

    if not archive_dir.exists():
        print(f"📂 归档目录为空")
        return 0

    archived = [d for d in archive_dir.iterdir() if d.is_dir()]

    if not archived:
        print(f"📂 归档目录为空")
        return 0

    print(f"📂 已归档变更（{len(archived)} 个）：")
    for d in sorted(archived):
        # 尝试读取验证结论
        status = d / "STATUS.md"
        conclusion = ""
        if status.exists():
            content = status.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if "结论" in line:
                    conclusion = line.strip()
                    break
        print(f"   📁 {d.name}")
        if conclusion:
            print(f"      {conclusion}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="vibe-coding 阶段5：归档已完成工作",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python scripts/archive.py --name add-dark-mode
  python scripts/archive.py --list
        """,
    )
    parser.add_argument("--name", default=None, help="变更名称")
    parser.add_argument("--list", action="store_true", help="列出已归档变更")
    parser.add_argument("--dir", default=None, help="自定义 changes 目录路径")

    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    changes_dir = get_changes_dir(script_dir, args.dir)

    if args.list:
        return list_archived(changes_dir)

    if not args.name:
        print(f"❌ 请指定 --name 或 --list")
        parser.print_help()
        return 1

    return archive_change(args.name, changes_dir)


if __name__ == "__main__":
    sys.exit(main())
