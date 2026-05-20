#!/usr/bin/env python3
"""code-exploration — graphify + agentgrep 双引擎代码探索工具

将 graphify（知识图谱）与 agentgrep（即时搜索）结合，
实现"点 → 面"的代码深度理解工作流。

用法：
    python explore.py                         # 增量扫描（graphify）
    python explore.py --full                  # 强制全量重扫
    python explore.py --check                 # 仅检查是否需要更新
    python explore.py --status                # 查看缓存状态
    python explore.py --install-hooks         # 安装 Git hooks
    python explore.py --hook                  # Git hook 模式（无交互输出）

    # --- 新增 agentgrep 集成模式 ---
    python explore.py --quick                # 快速模式：agentgrep 轻量扫描
    python explore.py --search <query>       # 即时搜索：agentgrep grep
    python explore.py --find <terms>         # 文件发现：agentgrep find
    python explore.py --trace <terms>        # 关系追踪：agentgrep trace
    python explore.py --outline <file>       # 结构概览：agentgrep outline
    python explore.py --graph-agent          # 图谱驱动搜索：graph.json → agentgrep 关联分析
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

# =============================================================================
# 内嵌公共工具
# =============================================================================


def _setup_unicode_output():
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except AttributeError:
            pass


def _find_project_root(start_dir: Optional[Path] = None) -> Path:
    start = start_dir or Path.cwd()
    markers = [".git", "pyproject.toml", "package.json", "Cargo.toml", "go.mod"]
    for parent in [start] + list(start.parents):
        for marker in markers:
            if (parent / marker).exists():
                return parent
    return start


def _run_git(args: list, cwd: Optional[Path] = None) -> Tuple[bool, str, str]:
    try:
        result = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True,
            encoding='utf-8', errors='replace',
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def _is_git_repo(project_root: Path) -> bool:
    ok, _, _ = _run_git(["git", "rev-parse", "--git-dir"], project_root)
    return ok


def _has_pending_changes(project_root: Path) -> bool:
    ok, stdout, _ = _run_git(["git", "status", "--porcelain"], project_root)
    return ok and bool(stdout)


def _git_add_and_commit(project_root: Path, files: List[str], message: str) -> bool:
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
    if not _is_git_repo(project_root):
        return []
    ok, stdout, _ = _run_git(["git", "tag", "-l", "--sort=-v:refname"], project_root)
    if not ok or not stdout:
        return []
    return [t.strip() for t in stdout.strip().split("\n") if t.strip()]


def _read_version(design_file: Path) -> Optional[str]:
    if not design_file.exists():
        return None
    import re
    content = design_file.read_text(encoding="utf-8")
    match = re.search(r'>\s*版本[：:]\s*(\d+\.\d+(?:\.\d+)?)', content)
    return match.group(1) if match else None


# =============================================================================
# 尝试从 vibe-coding/common.py 导入
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
    if _HAS_COMMON:
        return _common_find_root(start_dir)
    return _find_project_root(start_dir)


def run_git(args: list, cwd: Optional[Path] = None) -> Tuple[bool, str, str]:
    if _HAS_COMMON:
        return _common_run_git(args, cwd)
    return _run_git(args, cwd)


def get_git_tags(project_root: Path) -> List[str]:
    if _HAS_COMMON:
        return _common_get_tags(project_root)
    return _get_git_tags(project_root)


def get_current_version(project_root: Path) -> Optional[str]:
    if _HAS_COMMON:
        return _common_read_version(project_root / "docs" / "design.md")
    return _read_version(project_root / "docs" / "design.md")


# =============================================================================
# agentgrep 操作
# =============================================================================


def check_agentgrep() -> bool:
    """检查 agentgrep 是否已安装"""
    if shutil.which("agentgrep"):
        return True
    print("❌ agentgrep 未安装")
    return False


def run_agentgrep_quick(project_root: Path) -> int:
    """快速模式：用 agentgrep 做轻量代码扫描（替代 graphify）

    扫描项目代码结构概览，输出文件分布和关键模块。
    """
    if not check_agentgrep():
        return 2

    print(f"\n🔍 快速代码扫描（agentgrep）...")
    print(f"   📂 {project_root}\n")

    # 统计代码文件类型分布
    print("━━━ 文件类型分布 ━━━")
    for ext, label in [(".py", "Python"), (".ts", "TypeScript"),
                       (".js", "JavaScript"), (".go", "Go"),
                       (".rs", "Rust"), (".java", "Java"),
                       (".c", "C"), (".cpp", "C++"),
                       (".h", "Header"), (".md", "Markdown"),
                       (".json", "JSON"), (".yaml", "YAML"),
                       (".yml", "YAML"), (".toml", "TOML")]:
        result = subprocess.run(
            ["find", str(project_root), "-type", "f", "-name", f"*{ext}",
             "-not", "-path", "*/node_modules/*",
             "-not", "-path", "*/.git/*",
             "-not", "-path", "*/graphify-out/*"],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
        )
        count = len([l for l in result.stdout.strip().split("\n") if l.strip()]) if result.stdout.strip() else 0
        if count > 0:
            print(f"   {label:15s}  {count:5d} 个文件")

    # 主要目录结构
    print(f"\n━━━ 主要模块目录 ━━━")
    for d in ["src", "app", "lib", "cmd", "pkg", "tests", "test"]:
        dpath = project_root / d
        if dpath.exists():
            files = list(dpath.rglob("*")) if dpath.is_dir() else []
            py_files = [f for f in files if f.suffix in (".py", ".ts", ".js", ".go", ".rs", ".java")]
            print(f"   📁 {d}/    ~{len(py_files)} 个源码文件")

    # 找主要入口文件
    print(f"\n━━━ 入口文件 ━━━")
    for name in ["main", "index", "app", "cli", "server", "api", "handler"]:
        result = subprocess.run(
            ["find", str(project_root), "-type", "f",
             "-name", f"{name}.py",
             "-o", "-name", f"{name}.ts",
             "-o", "-name", f"{name}.js",
             "-o", "-name", f"{name}.go",
             "-o", "-name", f"{name}.rs",
             "-not", "-path", "*/node_modules/*",
             "-not", "-path", "*/.git/*",
             "-not", "-path", "*/graphify-out/*"],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            cwd=project_root,
        )
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                rel = Path(line).relative_to(project_root) if Path(line).is_absolute() else line
                print(f"   📄 {rel}")

    print(f"\n💡 提示：用以下命令深入探索")
    print(f"   python explore.py --search <关键词>    # 搜索代码")
    print(f"   python explore.py --find <文件名>      # 发现文件")
    print(f"   python explore.py --outline <文件路径>  # 查看结构")
    print(f"   python explore.py --trace <查询>       # 关系追踪")
    return 0


def run_agentgrep_search(project_root: Path, query: str) -> int:
    """即时搜索：用 agentgrep grep 搜索代码"""
    if not check_agentgrep():
        return 2

    print(f"\n🔎 搜索: {query}")
    print(f"   路径: {project_root}\n")

    # agentgrep v0.1.2 中 paths-only 模式正常工作
    # 先用 paths-only 找到匹配的文件
    cmd = ["agentgrep", "grep", query, "--path", str(project_root), "--paths-only"]
    result = subprocess.run(cmd, capture_output=True, text=True,
                            encoding='utf-8', errors='replace')
    matching_files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]

    if matching_files:
        print(f"📁 匹配文件 ({len(matching_files)} 个):")
        for f in matching_files:
            print(f"   📄 {f}")
    else:
        # 尝试正则模式
        print("   尝试正则搜索...")
        cmd = ["agentgrep", "grep", query, "--path", str(project_root),
               "--regex", "--paths-only"]
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding='utf-8', errors='replace')
        matching_files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        if matching_files:
            print(f"📁 匹配文件 ({len(matching_files)} 个):")
            for f in matching_files:
                print(f"   📄 {f}")

    if not matching_files:
        print("   (无匹配结果)")
        return 0

    # 显示这些文件中的实际匹配内容（用 built-in grep）
    print(f"\n━━━ 匹配详情 ━━━")
    for f in matching_files[:10]:
        fpath = project_root / f
        if fpath.exists() and fpath.is_file():
            try:
                r = subprocess.run(
                    ["grep", "-n", query, str(fpath)],
                    capture_output=True, text=True,
                    encoding='utf-8', errors='replace',
                )
                if r.stdout.strip():
                    print(f"📄 {f}:")
                    for line in r.stdout.strip().split("\n")[:8]:
                        print(f"   {line}")
                    if len(r.stdout.strip().split("\n")) > 8:
                        print(f"   ... (还有更多)")
            except Exception:
                pass

    return 0


def run_agentgrep_find(project_root: Path, terms: List[str]) -> int:
    """文件发现：用 agentgrep find 发现文件"""
    if not check_agentgrep():
        return 2

    query = " ".join(terms)
    print(f"\n📁 文件发现: {query}")
    print(f"   路径: {project_root}\n")

    cmd = ["agentgrep", "find", "--path", str(project_root),
           "--max-files", "20"] + terms
    result = subprocess.run(cmd, capture_output=True, text=True,
                            encoding='utf-8', errors='replace')

    if result.stdout.strip():
        print(result.stdout)
    if result.stderr.strip():
        print(f"⚠️  {result.stderr.strip()[:300]}")

    return 0


def run_agentgrep_trace(project_root: Path, terms: List[str]) -> int:
    """关系追踪：用 agentgrep trace 追踪代码关系"""
    if not check_agentgrep():
        return 2

    query = " ".join(terms)
    print(f"\n🔗 关系追踪: {query}")
    print(f"   路径: {project_root}\n")

    cmd = ["agentgrep", "trace", "--path", str(project_root),
           "--max-files", "10", "--max-regions", "10"] + terms
    result = subprocess.run(cmd, capture_output=True, text=True,
                            encoding='utf-8', errors='replace')

    # agentgrep trace 可能输出空（v0.1.2 bug），显示 stderr 作为参考
    if result.stdout.strip():
        print(result.stdout)
    if result.stderr.strip():
        print(f"   {result.stderr.strip()[:300]}")

    # 如果 agentgrep trace 无输出，用 grep 做基本搜索
    if not result.stdout.strip():
        print("   尝试用文件搜索替代...")
        for term in terms[:3]:
            search_term = term.replace("subject:", "").replace("relation:", "")
            cmd2 = ["agentgrep", "grep", search_term, "--path", str(project_root), "--paths-only"]
            r2 = subprocess.run(cmd2, capture_output=True, text=True,
                                encoding='utf-8', errors='replace')
            files = [f.strip() for f in r2.stdout.strip().split("\n") if f.strip()]
            if files:
                print(f"   '{search_term}' 出现在以下文件中:")
                for f in files[:10]:
                    print(f"      📄 {f}")

    return 0


def run_agentgrep_outline(project_root: Path, file_path: str) -> int:
    """结构概览：用 agentgrep outline 查看文件结构"""
    if not check_agentgrep():
        return 2

    target = Path(file_path)
    if not target.is_absolute():
        target = project_root / target
    if not target.exists():
        print(f"❌ 文件不存在: {target}")
        return 1

    rel_path = target.relative_to(project_root) if target.is_absolute() and project_root in target.parents else target
    print(f"\n📋 文件结构: {rel_path}\n")

    cmd = ["agentgrep", "outline", str(target), "--path", str(project_root)]
    result = subprocess.run(cmd, capture_output=True, text=True,
                            encoding='utf-8', errors='replace')

    if result.stdout.strip():
        print(result.stdout)
    elif result.stderr.strip():
        # agentgrep outline 无输出时尝试 Python 模式
        print(f"   (agentgrep 无输出，尝试内置分析...)\n")
        _fallback_outline(target)

    return 0


def _fallback_outline(file_path: Path):
    """内置结构概览（当 agentgrep outline 不可用时）"""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    lines = content.split("\n")

    classes = []
    functions = []
    imports = []

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith(("class ", "class\t")):
            classes.append((i, stripped))
        elif stripped.startswith(("def ", "def\t")):
            functions.append((i, stripped))
        elif stripped.startswith(("import ", "from ")):
            imports.append((i, stripped))

    if classes:
        print("   ── Classes ──")
        for ln, text in classes:
            print(f"      L{ln:4d}  {text}")
    if functions:
        print("   ── Functions ──")
        for ln, text in functions:
            print(f"      L{ln:4d}  {text}")
    if imports:
        print("   ── Imports (top-level) ──")
        for ln, text in imports[:15]:
            print(f"      L{ln:4d}  {text}")
    if not any([classes, functions, imports]):
        print(f"   ({len(lines)} lines, {len(content)} chars)")


# =============================================================================
# 图谱驱动搜索（graph-agent）：从 graphify graph.json → agentgrep 关联分析
# =============================================================================

GRAPHIFY_DIR = "graphify-out"


def run_graph_agent(project_root: Path) -> int:
    """图谱驱动搜索模式

    从 graphify graph.json 中提取文件和模块关系，
    然后用 agentgrep 对关联文件做深度分析。
    """
    if not check_agentgrep():
        return 2

    graph_file = project_root / GRAPHIFY_DIR / "graph.json"
    if not graph_file.exists():
        print(f"❌ graph.json 不存在，请先运行 graphify 构建知识图谱")
        print(f"   python explore.py    # 构建图谱")
        return 1

    print(f"\n🧠 图谱驱动搜索模式")
    print(f"   读取: {graph_file}\n")

    try:
        with open(graph_file, "r", encoding="utf-8") as f:
            graph = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ graph.json 读取失败: {e}")
        return 1

    # 提取图谱中的文件列表
    files = set()
    clusters = {}
    relationships = []

    raw = graph.get("files", graph.get("nodes", graph.get("modules", [])))
    if isinstance(raw, dict):
        for name, info in raw.items():
            files.add(name)
            if isinstance(info, dict) and "cluster" in info:
                cluster_name = info["cluster"]
                clusters.setdefault(cluster_name, []).append(name)
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                files.add(item)
            elif isinstance(item, dict):
                name = item.get("name", item.get("file", item.get("path", "")))
                if name:
                    files.add(name)
                    cluster = item.get("cluster", item.get("module", ""))
                    if cluster:
                        clusters.setdefault(cluster, []).append(name)

    # 提取关系边
    if "edges" in graph:
        relationships = graph["edges"][:20]

    print(f"📊 图谱统计")
    print(f"   文件数量: {len(files)}")
    if clusters:
        print(f"   模块聚类: {len(clusters)}")
    if relationships:
        print(f"   关系边数: {len(relationships)}")

    # 按聚类分组用 agentgrep 分析
    if clusters:
        print(f"\n━━━ 模块聚类概览（agentgrep outline）━━━")
        for cluster_name, cluster_files in sorted(clusters.items())[:10]:
            print(f"\n📦 模块: {cluster_name} ({len(cluster_files)} 个文件)")

            # 取前 3 个文件做 outline
            for fname in cluster_files[:3]:
                fpath = project_root / fname
                if fpath.exists():
                    rel = fpath.relative_to(project_root)
                    cmd = ["agentgrep", "outline", str(fpath),
                           "--path", str(project_root), "--max-items", "8"]
                    result = subprocess.run(cmd, capture_output=True, text=True,
                                            encoding='utf-8', errors='replace')
                    outline_text = result.stdout.strip()
                    if outline_text:
                        print(f"   📄 {rel}:")
                        for line in outline_text.split("\n")[:8]:
                            print(f"      {line}")

    # 显示关键关系
    if relationships:
        print(f"\n━━━ 关键关系 ━━━")
        for rel in relationships[:10]:
            if isinstance(rel, dict):
                src = rel.get("source", rel.get("from", "?"))
                tgt = rel.get("target", rel.get("to", "?"))
                rtype = rel.get("type", rel.get("relation", "关联"))
                print(f"   {src}  ──[{rtype}]──→  {tgt}")

    # 用 agentgrep trace 对关键模块做关系追踪
    if clusters:
        main_clusters = sorted(clusters.keys())[:3]
        print(f"\n━━━ 关联关系追踪（agentgrep trace）━━━")
        for cname in main_clusters:
            print(f"\n🔗 追踪模块: {cname}")
            for fname in clusters[cname][:2]:
                # 用文件名中的关键词做 trace
                stem = Path(fname).stem
                cmd = ["agentgrep", "trace",
                       f"subject:{stem}",
                       "--path", str(project_root),
                       "--max-files", "5", "--max-regions", "3"]
                result = subprocess.run(cmd, capture_output=True, text=True,
                                        encoding='utf-8', errors='replace')
                if result.stdout.strip():
                    print(f"   ← {stem}:")
                    for line in result.stdout.strip().split("\n")[:6]:
                        print(f"     {line}")

    print(f"\n✅ 图谱驱动搜索完成")
    print(f"💡 进阶探索:")
    print(f"   python explore.py --search <关键词>     # 搜索具体代码")
    print(f"   python explore.py --find <模块名>       # 发现更多文件")
    print(f"   graphify query \"你的问题\"               # 自然语言查询图谱")
    return 0


# =============================================================================
# graphify 操作（原有逻辑）
# =============================================================================


def check_graphify() -> bool:
    if shutil.which("graphify"):
        return True
    print("❌ graphify 未安装")
    print("   安装命令：pip install graphifyy && graphify install")
    print("   或：uv tool install graphifyy && graphify install")
    return False


def ensure_graphify_installed() -> bool:
    if check_graphify():
        return True
    print()
    print("请安装 graphify 后重试：")
    print("  pip install graphifyy")
    print("  graphify install")
    return False


def run_graphify(project_root: Path, full: bool = False) -> bool:
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

        graphify_dir = project_root / GRAPHIFY_DIR
        if not graphify_dir.exists():
            print("⚠️  graphify 未生成 graphify-out/ 目录")
            print("   这可能是因为 graphify 版本不兼容，尝试全量模式")
            return False

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
# Git 感知核心逻辑（原有）
# =============================================================================

CODE_DIRS = ["src", "app", "lib", "cmd", "pkg", "source", "tests", "test"]
EXCLUDE_PATTERNS = ["docs/", "graphify-out/", "*.md", "*.txt", "node_modules/"]


def find_last_exploration_tag(project_root: Path) -> Optional[str]:
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
    if not ensure_graphify_installed():
        return 2

    if not _is_git_repo(project_root):
        if not hook_mode:
            print("⚠️  当前项目不是 Git 仓库，将执行全量扫描")
        full = True
    else:
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

    if not hook_mode:
        print(f"\n🔨 正在更新知识图谱...")
    success = run_graphify(project_root, full=full)
    if not success:
        return 2

    version = get_current_version(project_root)
    version_suffix = f" [v{version}]" if version else ""
    commit_msg = f"chore: 更新 graphify 探索缓存{version_suffix}"

    if _has_pending_changes(project_root):
        ok = _git_add_and_commit(project_root, [GRAPHIFY_DIR], commit_msg)
        if ok and not hook_mode:
            print(f"✅ graphify-out/ 已提交到 Git")

    if not hook_mode:
        print(f"\n📋 摘要：")
        print(f"   项目：{project_root.name}")
        print(f"   版本：{version or '未检测'}")
        print(f"   位置：{project_root / GRAPHIFY_DIR}/")
        print(f"   包含：graph.html（交互式图谱）, graph.json（图数据）, GRAPH_REPORT.md（分析报告）")
        print(f"\n💡 下次增量扫描：python scripts/explore.py")
        print(f"   强制全量重扫：python scripts/explore.py --full")
        print(f"\n🤖 图谱 + agentgrep 结合探索：")
        print(f"   python explore.py --graph-agent   # 图谱驱动 agentgrep 搜索")

    return 0


def check_status(project_root: Path) -> int:
    if not check_graphify():
        return 1

    graphify_dir = project_root / GRAPHIFY_DIR
    if not graphify_dir.exists():
        print("📭 graphify-out/ 不存在，尚未运行过代码探索")
        print(f"   运行 python scripts/explore.py 开始首次探索")
        return 1

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
        description="code-exploration — graphify + agentgrep 双引擎代码探索",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # graphify 模式（默认）
  python scripts/explore.py                        # 增量扫描
  python scripts/explore.py --full                 # 强制全量重扫
  python scripts/explore.py --check                # 仅检查状态
  python scripts/explore.py --status               # 查看缓存状态
  python scripts/explore.py --install-hooks        # 安装 Git hooks

  # agentgrep 快速模式
  python scripts/explore.py --quick                # 快速代码扫描
  python scripts/explore.py --search "def login"    # 搜索代码
  python scripts/explore.py --find auth handler     # 发现文件
  python scripts/explore.py --trace subject:auth    # 关系追踪
  python scripts/explore.py --outline src/main.py   # 结构概览

  # 图谱驱动搜索（结合两者）
  python scripts/explore.py --graph-agent          # graph.json → agentgrep 分析
        """,
    )
    parser.add_argument("--full", action="store_true", help="强制全量重扫")
    parser.add_argument("--check", action="store_true", help="仅检查是否需要更新")
    parser.add_argument("--status", action="store_true", help="查看缓存状态")
    parser.add_argument("--hook", action="store_true", help="Git hook 模式（减少输出）")
    parser.add_argument("--install-hooks", action="store_true", help="安装 graphify Git hooks")
    parser.add_argument("--dir", default=None, help="项目根目录（默认自动检测）")

    # agentgrep 集成参数
    parser.add_argument("--quick", action="store_true", help="快速模式：agentgrep 轻量扫描")
    parser.add_argument("--search", default=None, metavar="<query>", help="搜索代码（agentgrep grep）")
    parser.add_argument("--find", nargs="+", default=None, metavar="<terms>", help="发现文件（agentgrep find）")
    parser.add_argument("--trace", nargs="+", default=None, metavar="<terms>", help="关系追踪（agentgrep trace）")
    parser.add_argument("--outline", default=None, metavar="<file>", help="结构概览（agentgrep outline）")
    parser.add_argument("--graph-agent", action="store_true", help="图谱驱动搜索：graph.json → agentgrep")

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

    # 路由：agentgrep 模式优先
    if args.quick:
        return run_agentgrep_quick(project_root)

    if args.search:
        return run_agentgrep_search(project_root, args.search)

    if args.find:
        return run_agentgrep_find(project_root, args.find)

    if args.trace:
        return run_agentgrep_trace(project_root, args.trace)

    if args.outline:
        return run_agentgrep_outline(project_root, args.outline)

    if args.graph_agent:
        return run_graph_agent(project_root)

    # graphify 模式（原有）
    if args.install_hooks:
        return install_hooks(project_root)

    if args.check:
        return check_status(project_root)

    if args.status:
        return check_status(project_root)

    return run_exploration(project_root, full=args.full, hook_mode=args.hook)


if __name__ == "__main__":
    sys.exit(main())
