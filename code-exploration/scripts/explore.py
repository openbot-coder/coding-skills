#!/usr/bin/env python3
"""code-exploration Git 感知增量扫描工具

将 graphify 输出与 Git 版本管理结合，以 tag 为缓存粒度，
避免重复全量扫描，降低 token 和计算消耗。

用法：
    python explore.py                     # 增量扫描（默认）
    python explore.py --full              # 强制全量重扫
    python explore.py --check             # 仅检查是否需要更新
    python explore.py --status            # 查看缓存状态
    python explore.py --install-hooks     # 安装 Git hooks
    python explore.py --hook              # Git hook 模式（无交互输出）

工作流：
    1. 查找最近包含 graphify-out/ 的 git tag
    2. git diff tag..HEAD — 排除 docs/ graphify-out/
       ├─ 无变更 → 跳过扫描，复用缓存
       └─ 有变更 → graphify . --update（增量）
    3. git add + commit graphify-out/
    4. 输出精简摘要
"""

import argparse
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

# =============================================================================
# 内嵌公共工具（独立运行时无需依赖 common.py）
# =============================================================================

def _setup_unicode_output():
    """解决 Windows 控制台 Unicode 输出问题"""
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except AttributeError:
            pass


def _find_project_root(start_dir: Optional[Path] = None) -> Path:
    """从给定目录向上查找项目根目录"""
    start = start_dir or Path.cwd()
    markers = [".git", "pyproject.toml", "package.json", "Cargo.toml", "go.mod"]
    for parent in [start] + list(start.parents):
        for marker in markers:
            if (parent / marker).exists():
                return parent
    return start


def _run_git(args: list, cwd: Optional[Path] = None) -> Tuple[bool, str, str]:
    """运行 git 命令"""
    try:
        result = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True,
            encoding='utf-8', errors='replace',
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def _is_git_repo(project_root: Path) -> bool:
    """检查目录是否为 Git 仓库"""
    ok, _, _ = _run_git(["git", "rev-parse", "--git-dir"], project_root)
    return ok


def _has_pending_changes(project_root: Path) -> bool:
    """检查是否有未提交的更改"""
    ok, stdout, _ = _run_git(["git", "status", "--porcelain"], project_root)
    return ok and bool(stdout)


def _git_add_and_commit(project_root: Path, files: List[str], message: str) -> bool:
    """执行 git add 指定文件并 git commit"""
    ok, _, stderr = _run_git(["git", "add"] + files, project_root)
    if not ok:
        print(f"⚠️  git add 失败：{stderr}")
        return False
    ok, _, stderr = _run_git(["git", "commit", "-m", message], project_root)
    if not ok:
        print(f"⚠️  git commit 失败：{stderr}")
        return False
    return True


def _get_git_tags(project_root: Path) -> List[str]:
    """获取所有 git tag（按版本排序，最新在前）"""
    if not _is_git_repo(project_root):
        return []
    ok, stdout, _ = _run_git(["git", "tag", "-l", "--sort=-v:refname"], project_root)
    if not ok or not stdout:
        return []
    return [t.strip() for t in stdout.strip().split("\n") if t.strip()]


def _read_version(design_file: Path) -> Optional[str]:
    """从 design.md 读取当前版本号"""
    if not design_file.exists():
        return None
    import re
    content = design_file.read_text(encoding="utf-8")
    match = re.search(r'>\s*版本[：:]\s*(\d+\.\d+(?:\.\d+)?)', content)
    return match.group(1) if match else None


# =============================================================================
# 尝试从 vibe-coding/common.py 导入（更完整的函数）
# =============================================================================

try:
    _common_path = Path(__file__).resolve().parent.parent.parent / "vibe-coding" / "scripts"
    if _common_path.exists():
        sys.path.insert(0, str(_common_path))
        from common import (
            find_project_root as _common_find_root,
            run_git_command as _common_run_git,
            is_git_repo as _common_is_git,
            has_pending_changes as _common_has_pending,
            git_add_and_commit as _common_git_commit,
            get_git_tags as _common_get_tags,
            read_version as _common_read_version,
        )
        _HAS_COMMON = True
    else:
        _HAS_COMMON = False
except ImportError:
    _HAS_COMMON = False


def find_project_root(start_dir: Optional[Path] = None) -> Path:
    """查找项目根目录（优先 common.py，回退内嵌实现）"""
    if _HAS_COMMON:
        return _common_find_root(start_dir)
    return _find_project_root(start_dir)


def run_git(args: list, cwd: Optional[Path] = None) -> Tuple[bool, str, str]:
    """运行 git（优先 common.py）"""
    if _HAS_COMMON:
        return _common_run_git(args, cwd)
    return _run_git(args, cwd)


def get_git_tags(project_root: Path) -> List[str]:
    """获取 git tags"""
    if _HAS_COMMON:
        return _common_get_tags(project_root)
    return _get_git_tags(project_root)


def get_current_version(project_root: Path) -> Optional[str]:
    """获取当前版本号"""
    if _HAS_COMMON:
        return _common_read_version(project_root / "docs" / "design.md")
    return _read_version(project_root / "docs" / "design.md")


# =============================================================================
# graphify 操作
# =============================================================================

GRAPHIFY_DIR = "graphify-out"


def check_graphify() -> bool:
    """检查 graphify 是否已安装"""
    if shutil.which("graphify"):
        return True
    print("❌ graphify 未安装")
    print("   安装命令：pip install graphifyy && graphify install")
    print("   或：uv tool install graphifyy && graphify install")
    return False


def ensure_graphify_installed() -> bool:
    """确保 graphify 已安装，未安装则引导安装"""
    if check_graphify():
        return True
    print()
    print("请安装 graphify 后重试：")
    print("  pip install graphifyy")
    print("  graphify install")
    return False


def run_graphify(project_root: Path, full: bool = False) -> bool:
    """运行 graphify 扫描

    Args:
        project_root: 项目根目录
        full: True=全量扫描, False=增量扫描(--update)

    Returns:
        是否成功
    """
    cmd = ["graphify", "."]
    if not full:
        cmd.append("--update")
        print("  ↪ 增量模式 (--update)")
    else:
        print("  ↪ 全量模式")

    try:
        result = subprocess.run(
            cmd, cwd=project_root, capture_output=True, text=True,
            encoding='utf-8', errors='replace',
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()[:500] if result.stderr else "未知错误"
            print(f"❌ graphify 运行失败：{stderr}")
            return False

        # 检查输出是否生成
        graphify_dir = project_root / GRAPHIFY_DIR
        if not graphify_dir.exists():
            print("⚠️  graphify 未生成 graphify-out/ 目录")
            print("   这可能是因为 graphify 版本不兼容，尝试全量模式")
            return False

        # 显示输出文件
        files = [f.name for f in graphify_dir.iterdir() if f.is_file()]
        print(f"  📁 graphify-out/ 已更新（{len(files)} 个文件）")
        return True

    except FileNotFoundError:
        print("❌ graphify 命令未找到，请确认已安装")
        return False
    except Exception as e:
        print(f"❌ graphify 运行异常：{e}")
        return False


# =============================================================================
# Git 感知核心逻辑
# =============================================================================

CODE_DIRS = ["src", "app", "lib", "cmd", "pkg", "source", "tests", "test"]
EXCLUDE_PATTERNS = ["docs/", "graphify-out/", "*.md", "*.txt", "node_modules/"]


def find_last_exploration_tag(project_root: Path) -> Optional[str]:
    """查找最近一个包含 graphify-out/ 的 git tag

    遍历所有 tag，用 git ls-tree 检查 graphify-out 是否存在。
    从最新 tag 开始找，找到第一个就返回。
    """
    tags = get_git_tags(project_root)
    if not tags:
        return None

    for tag in tags:
        ok, stdout, _ = run_git(
            ["git", "ls-tree", "-d", tag, "--", GRAPHIFY_DIR],
            project_root,
        )
        if ok and stdout:
            return tag
    return None


def has_code_changed(project_root: Path, since_tag: str) -> Tuple[bool, List[str]]:
    """检查自 tag 以来代码是否有实质变更

    仅检查源码目录（src/ app/ tests/ 等），排除 docs/ graphify-out/ 等。
    返回 (是否变更, 变更文件列表)
    """
    # 构建 diff 的 path 参数
    paths = [d for d in CODE_DIRS if (project_root / d).exists()]
    if not paths:
        return False, []

    ok, stdout, _ = run_git(
        ["git", "diff", "--name-only", f"{since_tag}..HEAD", "--"] + paths,
        project_root,
    )
    if not ok or not stdout:
        return False, []

    changed = [line.strip() for line in stdout.split("\n") if line.strip()]
    return len(changed) > 0, changed


def run_exploration(project_root: Path, full: bool = False, hook_mode: bool = False) -> int:
    """执行 Git 感知的增量探索

    Args:
        project_root: 项目根目录
        full: 是否强制全量重扫
        hook_mode: 是否钩子模式（减少输出）

    Returns:
        退出码（0=成功, 1=跳过, 2=错误）
    """
    if not ensure_graphify_installed():
        return 2

    if not _is_git_repo(project_root):
        if not hook_mode:
            print("⚠️  当前项目不是 Git 仓库，将执行全量扫描")
        full = True
    else:
        # 查找上次包含 graphify-out 的 tag
        last_tag = find_last_exploration_tag(project_root)

        if last_tag and not full:
            has_changed, changed_files = has_code_changed(project_root, last_tag)

            if not has_changed:
                print(f"✅ 自 {last_tag} 以来代码无变更，跳过 graphify 扫描")
                print(f"   可直接复用 tag {last_tag} 的 graphify-out/ 缓存")
                return 0

            if not hook_mode:
                print(f"🔄 检测到变更（自 {last_tag}）")
                if changed_files and len(changed_files) <= 10:
                    for f in changed_files:
                        print(f"   📄 {f}")
                else:
                    print(f"   📄 {len(changed_files)} 个文件已变更")

    # 运行 graphify
    if not hook_mode:
        print(f"\n🔨 正在更新知识图谱...")
    success = run_graphify(project_root, full=full)
    if not success:
        return 2

    # 提交到 git
    version = get_current_version(project_root)
    version_suffix = f" [v{version}]" if version else ""
    commit_msg = f"chore: 更新 graphify 探索缓存{version_suffix}"

    if _has_pending_changes(project_root):
        ok = _git_add_and_commit(project_root, [GRAPHIFY_DIR], commit_msg)
        if ok:
            if not hook_mode:
                print(f"✅ graphify-out/ 已提交到 Git")

    if not hook_mode:
        print(f"\n📋 摘要：")
        print(f"   项目：{project_root.name}")
        print(f"   版本：{version or '未检测'}")
        print(f"   位置：{project_root / GRAPHIFY_DIR}/")
        print(f"   包含：graph.html（交互式图谱）, graph.json（图数据）, GRAPH_REPORT.md（分析报告）")
        print(f"\n💡 下次增量扫描：python scripts/explore.py")
        print(f"   强制全量重扫：python scripts/explore.py --full")

    return 0


def check_status(project_root: Path) -> int:
    """查看 graphify 缓存状态"""
    if not check_graphify():
        return 1

    graphify_dir = project_root / GRAPHIFY_DIR
    if not graphify_dir.exists():
        print("📭 graphify-out/ 不存在，尚未运行过代码探索")
        print(f"   运行 python scripts/explore.py 开始首次探索")
        return 1

    # 检查 git tags
    last_tag = find_last_exploration_tag(project_root)
    if last_tag:
        print(f"🏷️  最近包含 graphify-out 的 tag：{last_tag}")

        has_changed, changed_files = has_code_changed(project_root, last_tag)
        if has_changed:
            print(f"⚠️  自 {last_tag} 以来代码有变更（{len(changed_files)} 个文件）")
            print(f"   运行 python scripts/explore.py 更新图谱")
        else:
            print(f"✅ 代码无变更，缓存有效")
    else:
        print(f"⚠️  未有 tag 包含 graphify-out/ 缓存")

    # 显示 graphify-out 文件
    files = sorted([f.name for f in graphify_dir.iterdir() if f.is_file()])
    print(f"\n📁 graphify-out/（{len(files)} 个文件）：")
    for f in files:
        fpath = graphify_dir / f
        size = fpath.stat().st_size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / 1024 / 1024:.1f} MB"
        print(f"   📄 {f:<30} {size_str}")

    version = get_current_version(project_root)
    if version:
        print(f"\n📋 当前版本：v{version}")

    return 0


def install_hooks(project_root: Path) -> int:
    """安装 graphify Git hooks"""
    if not ensure_graphify_installed():
        return 2

    if not _is_git_repo(project_root):
        print("⚠️  当前项目不是 Git 仓库，跳过 hooks 安装")
        return 1

    print("🔧 安装 graphify Git hooks...")
    try:
        result = subprocess.run(
            ["graphify", "hook", "install"],
            cwd=project_root, capture_output=True, text=True,
            encoding='utf-8', errors='replace',
        )
        if result.returncode == 0:
            print("✅ graphify hooks 已安装")
            print("   - post-commit: 提交后自动增量更新图谱")
            print("   - post-checkout: 切换分支后自动增量更新")
            print("   - merge driver: 多人并行提交 graph.json 自动合并")
            return 0
        else:
            stderr = result.stderr.strip()[:300] if result.stderr else ""
            print(f"⚠️  hooks 安装可能失败：{stderr}")
            return 1
    except Exception as e:
        print(f"❌ hooks 安装异常：{e}")
        return 2


# =============================================================================
# CLI
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="code-exploration Git 感知增量扫描工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python scripts/explore.py                        # 增量扫描
  python scripts/explore.py --full                 # 强制全量重扫
  python scripts/explore.py --check                # 仅检查状态
  python scripts/explore.py --install-hooks        # 安装 Git hooks
        """,
    )
    parser.add_argument("--full", action="store_true", help="强制全量重扫")
    parser.add_argument("--check", action="store_true", help="仅检查是否需要更新")
    parser.add_argument("--status", action="store_true", help="查看缓存状态")
    parser.add_argument("--hook", action="store_true", help="Git hook 模式（减少输出）")
    parser.add_argument("--install-hooks", action="store_true", help="安装 graphify Git hooks")
    parser.add_argument("--dir", default=None, help="项目根目录（默认自动检测）")

    args = parser.parse_args()
    _setup_unicode_output()

    if args.dir:
        project_root = Path(args.dir).resolve()
    else:
        project_root = find_project_root()

    print(f"📂 项目目录：{project_root}")

    if not project_root.exists():
        print(f"❌ 目录不存在：{project_root}")
        return 1

    if args.install_hooks:
        return install_hooks(project_root)

    if args.check:
        return check_status(project_root)

    if args.status:
        return check_status(project_root)

    return run_exploration(project_root, full=args.full, hook_mode=args.hook)


if __name__ == "__main__":
    sys.exit(main())
