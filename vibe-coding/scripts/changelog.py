#!/usr/bin/env python3
"""vibe-coding Changelog 管理工具

用法：
    python scripts/changelog.py --list              # 列出所有版本
    python scripts/changelog.py --current           # 显示当前版本
    python scripts/changelog.py --status            # 显示各版本状态
    python scripts/changelog.py --mark <version> --state done    # 标记版本为已完成
    python scripts/changelog.py --mark <version> --state dev      # 标记版本为开发中

功能：
    查看和管理 changelog.md 中的版本信息
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional, Dict

from common import (
    setup_unicode_output, find_project_root, get_docs_dir,
    read_version, find_tag_for_version,
)


setup_unicode_output()


def parse_changelog(changelog_file: Path) -> List[Dict]:
    """解析 changelog.md，提取所有版本条目

    Returns:
        版本列表，每项包含 version, date, sections, status
    """
    if not changelog_file.exists():
        return []

    content = changelog_file.read_text(encoding="utf-8")
    entries = []

    # 匹配版本头：## [1.0.0] - 2026-05-11
    version_pattern = r"##\s*\[(\d+\.\d+(?:\.\d+)?)\]\s*-\s*(\d{4}-\d{2}-\d{2})"
    version_blocks = list(re.finditer(version_pattern, content))

    for i, match in enumerate(version_blocks):
        version = match.group(1)
        ver_date = match.group(2)

        # 提取该版本的文本块
        start = match.start()
        end = version_blocks[i + 1].start() if i + 1 < len(version_blocks) else len(content)
        block = content[start:end]

        # 提取状态
        status = "开发中"
        if "✅ 已实现" in block:
            status = "已实现"
        elif "✅ 已完成" in block:
            status = "已完成"
        elif "⏳ 开发中" in block or "⏳ 进行中" in block:
            status = "开发中"
        elif "📋 计划中" in block:
            status = "计划中"

        # 提取各节内容
        sections = {}
        section_pattern = r"###\s*(Added|Changed|Fixed|Removed|Deprecated|Security)\s*\n((?:.*\n)*?)(?=\n###|\n##|\n---|\Z)"
        for sec_match in re.finditer(section_pattern, block):
            section_name = sec_match.group(1)
            section_content = sec_match.group(2).strip()
            if section_content and section_content != "-":
                sections[section_name] = section_content

        entries.append({
            "version": version,
            "date": ver_date,
            "status": status,
            "sections": sections,
        })

    return entries


def list_versions(docs_dir: Path) -> int:
    """列出所有版本"""
    changelog_file = docs_dir / "changelog.md"
    entries = parse_changelog(changelog_file)

    if not entries:
        print("❌ changelog.md 不存在或无版本记录")
        print("   请先运行：python scripts/design.py --init")
        return 1

    design_file = docs_dir / "design.md"
    current_version = read_version(design_file) or "未知"

    print(f"📋 版本列表（当前：v{current_version}）")
    print("=" * 60)
    print(f"{'版本':<12} {'日期':<14} {'状态':<8} {'变更概要'}")
    print("-" * 60)

    for entry in entries:
        v = entry["version"]
        d = entry["date"]
        s = entry["status"]

        # 概要：取第一个 section 的第一条
        summary = ""
        for sec_name, sec_content in entry["sections"].items():
            lines = [l.strip() for l in sec_content.split("\n") if l.strip().startswith("-")]
            if lines:
                summary = lines[0][1:].strip()[:30]
                break

        marker = " ← 当前" if v == current_version else ""
        print(f"v{v:<11} {d:<14} {s:<8} {summary}{marker}")

    print()
    return 0


def show_current_version(docs_dir: Path) -> int:
    """显示当前版本"""
    design_file = docs_dir / "design.md"

    if not design_file.exists():
        print("❌ design.md 不存在")
        print("   请先运行：python scripts/design.py --init")
        return 1

    version = read_version(design_file)
    if not version:
        print("⚠️  design.md 中未找到版本号")
        return 1

    changelog_file = docs_dir / "changelog.md"
    entries = parse_changelog(changelog_file)
    current_entry = next((e for e in entries if e["version"] == version), None)

    print(f"📌 当前版本：v{version}")
    if current_entry:
        print(f"   创建日期：{current_entry['date']}")
        print(f"   状态：{current_entry['status']}")
        if current_entry["sections"]:
            print(f"   变更内容：")
            for sec_name, sec_content in current_entry["sections"].items():
                print(f"     {sec_name}:")
                for line in sec_content.split("\n"):
                    if line.strip().startswith("-"):
                        print(f"       {line.strip()}")

    return 0


def show_status(docs_dir: Path) -> int:
    """显示各版本状态"""
    changelog_file = docs_dir / "changelog.md"
    entries = parse_changelog(changelog_file)

    if not entries:
        print("❌ changelog.md 不存在或无版本记录")
        return 1

    design_file = docs_dir / "design.md"
    current_version = read_version(design_file) or "未知"

    print("📊 版本状态总览")
    print("=" * 60)

    for entry in entries:
        v = entry["version"]
        is_current = v == current_version
        marker = " ← 当前" if is_current else ""

        status_icon = {
            "已实现": "✅",
            "已完成": "✅",
            "开发中": "⏳",
            "计划中": "📋",
        }.get(entry["status"], "❓")

        print(f"  {status_icon} v{v} ({entry['date']}) - {entry['status']}{marker}")

    print()
    return 0


def mark_version(version: str, state: str, docs_dir: Path) -> int:
    """标记版本状态"""
    changelog_file = docs_dir / "changelog.md"

    if not changelog_file.exists():
        print("❌ changelog.md 不存在")
        return 1

    content = changelog_file.read_text(encoding="utf-8")

    # 查找目标版本块的范围
    # 先找到版本头
    version_header = rf"##\s*\[{re.escape(version)}\]\s*-\s*\d{{4}}-\d{{2}}-\d{{2}}"
    header_match = re.search(version_header, content)
    if not header_match:
        print(f"❌ 未找到版本 {version} 的条目")
        return 1

    # 找到下一个版本头作为结束位置
    next_header_match = re.search(rf"\n##\s*\[\d+\.\d+(?:\.\d+)?\]", content[header_match.end():])
    if next_header_match:
        block_end = header_match.end() + next_header_match.start()
    else:
        block_end = len(content)

    version_block = content[header_match.start():block_end]

    state_map = {
        "done": "✅ 已实现",
        "dev": "⏳ 开发中",
        "plan": "📋 计划中",
    }
    new_status = state_map.get(state, f"⏳ {state}")

    # 仅在该版本块内替换状态
    # 如果标记为已实现，加上 git tag 信息
    if state == "done":
        project_root = docs_dir.parent if docs_dir.name == "docs" else find_project_root()
        tag = find_tag_for_version(version, project_root)
        if tag:
            new_status_with_tag = f"{new_status} (git: {tag})"
        else:
            new_status_with_tag = new_status
    else:
        new_status_with_tag = new_status

    # 替换该版本块内的 ### Status 部分
    # 只替换 ### Status 行后的内容（到块结束或下一个 ### 之前）
    new_block = re.sub(
        r"(###\s*Status\s*\n)[^\n]*",
        rf"\g<1>{new_status_with_tag}",
        version_block,
    )

    # 用新块替换旧块
    content = content[:header_match.start()] + new_block + content[block_end:]

    changelog_file.write_text(content, encoding="utf-8")
    print(f"✅ 版本 v{version} 状态已更新为：{new_status_with_tag}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="vibe-coding Changelog 管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python scripts/changelog.py --list              # 列出所有版本
  python scripts/changelog.py --current           # 显示当前版本
  python scripts/changelog.py --status            # 显示各版本状态
  python scripts/changelog.py --mark 1.0.0 --state done    # 标记版本为已完成
  python scripts/changelog.py --mark 1.1.0 --state dev     # 标记版本为开发中
        """,
    )

    parser.add_argument("--list", action="store_true", help="列出所有版本")
    parser.add_argument("--current", action="store_true", help="显示当前版本")
    parser.add_argument("--status", action="store_true", help="显示各版本状态")
    parser.add_argument("--mark", default=None, metavar="VERSION",
                        help="标记指定版本的状态")
    parser.add_argument("--state", default=None,
                        choices=["done", "dev", "plan"],
                        help="版本状态（done=已实现, dev=开发中, plan=计划中）")
    parser.add_argument("--dir", default=None, help="自定义 docs 目录路径")

    args = parser.parse_args()

    docs_dir = get_docs_dir(Path(__file__).resolve().parent, args.dir)

    if args.list:
        return list_versions(docs_dir)
    elif args.current:
        return show_current_version(docs_dir)
    elif args.status:
        return show_status(docs_dir)
    elif args.mark:
        if not args.state:
            print("❌ --mark 需要指定 --state 参数")
            print("   可选值：done（已实现）、dev（开发中）、plan（计划中）")
            return 1
        return mark_version(args.mark, args.state, docs_dir)
    else:
        # 默认显示帮助
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())