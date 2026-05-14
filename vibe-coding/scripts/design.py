#!/usr/bin/env python3
"""vibe-coding 阶段1：设计文档管理

用法：
  # 方案 B：中央 design.md 模式（推荐）
  python scripts/design.py --init --name "my-project" --lang python --desc "描述"  # 绿地
  python scripts/design.py --adopt --name "my-project" --version 1.0.0             # 棕地
  python scripts/design.py --change --desc "新增XX需求" --bump minor
  python scripts/design.py --rollback --version 1.0.0

  # 向后兼容：创建独立变更设计文档（旧模式）
  python scripts/design.py --name add-dark-mode --desc "添加暗色模式支持"

功能：
  --init:    创建完整项目骨架 + design.md + changelog.md（绿地/全新项目）
  --adopt:   棕地领养：扫描已有项目，生成预填充的 design.md
  --change:  记录变更，递增版本号，更新 changelog.md
  --rollback: 回退到指定版本（从 git tag 恢复）
  --name:    （旧模式）创建独立变更设计文档和进度文件
"""

import argparse
import shutil
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from common import (
    setup_unicode_output, find_project_root, get_changes_dir, get_docs_dir,
    run_git_command, is_git_repo, has_pending_changes, git_add_and_commit,
    read_version, bump_version, update_version_in_design, update_last_updated,
    rollback_files_from_tag, find_tag_for_version, get_git_tags,
    detect_project_info, generate_adopt_design,
    generate_greenfield_structure, generate_greenfield_design,
    PROGRESS_TEMPLATE_TASK_SECTION,
)


setup_unicode_output()


















CHANGELOG_TEMPLATE = """# Changelog

所有重要的产品设计和需求变更都记录在此文件中。

## [0.1.0] - {date}

### Added
- 初始版本：产品基础设计

### Status
⏳ 设计中

---
"""

CHANGELOG_ADOPT_TEMPLATE = """# Changelog

所有重要的产品设计和需求变更都记录在此文件中。

## [{version}] - {date}

### Added
- 棕地导入：从现有项目创建设计文档，版本号 v{version}

### Status
✅ 已实现

---

"""


# =============================================================================
# 旧模式：独立变更设计文档模板（保持向后兼容）
# =============================================================================

DESIGN_TEMPLATE = """# 设计文档：{name}

> 创建日期：{date}
> 状态：待填充

## 设计状态

| 阶段 | 状态 | 日期 | 说明 |
|------|------|------|------|
| 设计编写 | ✅ | {date} | |
| Agent 审查 | ⏳ | - | |
| 用户批准 | ⏳ | - | |

## 目标

<!-- 这个变更要达成什么？用 1-3 句话描述预期结果 -->

## 背景

<!-- 为什么需要这个变更？当前有什么问题或机会？ -->

### 需求访谈记录

| 日期 | 访谈对象 | 主要内容 | 关键结论 |
|------|----------|----------|----------|
| - | - | - | - |

## 成功标准

<!-- 如何判断这个变更成功完成？必须可验证 -->

- [ ] 标准1：
- [ ] 标准2：
- [ ] 标准3：

## 范围

### 包含

<!-- 这个变更会做什么 -->

### 不包含

<!-- 这个变更不会做什么（明确边界） -->

## 非功能性需求

<!-- 性能、安全、兼容性等要求（如无则删除此节） -->

## 备注

<!-- 其他需要说明的内容（如无则删除此节） -->
"""


PROGRESS_TEMPLATE = """# 进度跟踪：{name}

> 创建日期：{date}
> 最后更新：-

## 基本信息

| 字段 | 值 |
|------|---|
| **变更名称** | {name} |
| **当前阶段** | 阶段1：需求分析 |
| **创建日期** | {date} |
| **最后更新** | - |

## 设计状态

| 阶段 | 状态 | 日期 | 说明 |
|------|------|------|------|
| 设计编写 | ✅ | {date} | |
| Agent 审查 | ⏳ | - | |
| 用户批准 | ⏳ | - | |

---

## 阶段2：任务拆解

| 字段 | 值 |
|------|-----|
| **状态** | ⏳ |
| **开始时间** | - |
| **完成时间** | - |
| **概述** | - |
| **依赖** | - |
| **风险** | - |

### 任务清单

| # | 任务名称 | 状态 | 优先级 | 预计工时 | 功能点数 | 完成时间 |
|---|----------|------|--------|----------|----------|----------|
| - | - | - | - | - | - | - |

---

## 阶段3：代码执行

| 字段 | 值 |
|------|-----|
| **状态** | ⏳ |
| **开始时间** | - |
| **完成时间** | - |
| **当前任务** | - |

### 任务执行进度

| # | 任务名称 | 状态 | 优先级 | 预计工时 | 功能点数 | 完成时间 |
|---|----------|------|--------|----------|----------|----------|
| - | - | - | - | - | - |

---

## 阶段4：测试验证

| 字段 | 值 |
|------|-----|
| **状态** | ⏳ |
| **开始时间** | - |
| **完成时间** | - |

### 系统集成测试

| 测试项 | 状态 | 测试日期 | 说明 |
|--------|------|----------|------|
| 模块接口测试 | ⏳ | - | |
| 数据流转测试 | ⏳ | - | |
| 端到端测试 | ⏳ | - | |
| 异常处理测试 | ⏳ | - | |

### 调试记录

| 时间 | 问题描述 | 根因 | 修复方案 | 状态 |
|------|----------|------|----------|------|
| - | - | - | - | - |

---

## 阶段5：需求归档

| 字段 | 值 |
|------|-----|
| **状态** | ⏳ |
| **归档时间** | - |
| **Git 标签** | - |
| **归档路径** | - |

---

## 变更记录

| 日期 | 阶段 | 操作 | 说明 |
|------|------|------|------|
| {date} | 阶段1 | 创建 | 变更设计已创建 |
"""


# =============================================================================
# 方案 B 操作
# =============================================================================

def init_central_design(name: str, desc: Optional[str], docs_dir: Path, language: str = "unknown") -> int:
    """初始化绿地项目：创建完整项目骨架 + design.md + changelog.md

    Args:
        name: 项目名称
        desc: 项目描述
        docs_dir: docs 目录路径
        language: 开发语言（python/javascript/typescript/rust/go）
    """
    project_root = docs_dir.parent

    # 先检查 design.md 是否存在
    design_file = docs_dir / "design.md"
    if design_file.exists():
        print(f"❌ design.md 已存在：{design_file}")
        print(f"   如需修改，请使用 --change 命令")
        return 1

    today = date.today().isoformat()

    # 1. 创建项目骨架
    print("📁 正在创建项目目录结构...")
    created_files = generate_greenfield_structure(project_root, name, desc or name, language)
    print(f"   已创建 {len(created_files)} 个文件和目录")

    # 2. 生成预填充的 design.md
    design_content = generate_greenfield_design(name, desc or "", language, today)
    design_file.write_text(design_content, encoding="utf-8")

    # 3. 创建 changelog.md
    changelog_file = docs_dir / "changelog.md"
    changelog_content = CHANGELOG_TEMPLATE.format(date=today)
    if name:
        changelog_content = changelog_content.replace(
            "- 初始版本：产品基础设计",
            f"- {name}：初始版本，产品基础设计",
        )
    changelog_file.write_text(changelog_content, encoding="utf-8")

    print("=" * 60)
    print("🎉 绿地项目初始化完成（方案 B）")
    print("=" * 60)
    print(f"✅ design.md 已创建：{design_file}")
    print(f"✅ changelog.md 已创建：{changelog_file}")
    print(f"✅ 项目骨架已创建")
    print()
    print(f"📋 生成概要：")
    print(f"   项目名称：{name}")
    print(f"   开发语言：{language}")
    print(f"   初始版本：v0.1.0")
    print(f"   目录结构：")
    print(f"     ├── {project_root.name}/")
    print(f"     │   ├── src/          # 源代码")
    print(f"     │   ├── tests/        # 测试")
    print(f"     │   ├── docs/         # 设计文档")
    print(f"     │   ├── README.md")
    print(f"     │   └── .gitignore")
    print()
    print(f"📋 下一步：")
    print(f"   1. 编辑 docs/design.md，填充各章节的设计内容")
    print(f"   2. 安装开发依赖并开始编码")
    print(f"   3. 有需求变更时，使用：")
    print(f"      python scripts/design.py --change --desc \"变更描述\" --bump minor")
    print(f"   4. 需要回退时，使用：")
    print(f"      python scripts/design.py --rollback --version <版本号>")
    print()

    # Git 提交
    if is_git_repo(project_root):
        if has_pending_changes(project_root):
            git_add_and_commit(project_root, f"docs(design): 初始化 {name} v0.1.0")
            print(f"✅ Git 已提交：docs(design): 初始化 {name} v0.1.0")

    return 0


def adopt_central_design(name: Optional[str], version: Optional[str], docs_dir: Path) -> int:
    """棕地初始化：扫描已有项目，生成预填充的 design.md

    Args:
        name: 项目名称（可选，未指定则从项目文件自动检测）
        version: 初始版本号（可选，未指定则从项目文件自动检测，默认 1.0.0）
        docs_dir: docs 目录路径
    """
    project_root = docs_dir.parent

    # 扫描项目
    print("🔍 正在扫描现有项目...")
    info = detect_project_info(project_root)
    print(f"   项目名称：{info['name']}")
    print(f"   版本号：{info['version']}")
    print(f"   语言：{info['language']}")
    if info["frameworks"]:
        print(f"   框架：{', '.join(info['frameworks'])}")
    print(f"   源代码目录：{', '.join(info['src_dirs'])}")
    print()

    # 覆盖检测到的值
    if name:
        info["name"] = name
    if version:
        info["version"] = version

    docs_dir.mkdir(parents=True, exist_ok=True)

    design_file = docs_dir / "design.md"
    changelog_file = docs_dir / "changelog.md"

    if design_file.exists():
        print(f"❌ design.md 已存在：{design_file}")
        print(f"   如需重新领养，请先删除现有文件")
        return 1

    # 生成预填充的 design.md
    today = date.today().isoformat()
    design_content = generate_adopt_design(project_root, info)
    design_file.write_text(design_content, encoding="utf-8")

    # 创建棕地 changelog.md
    changelog_content = CHANGELOG_ADOPT_TEMPLATE.format(
        version=info["version"],
        date=today,
    )
    changelog_file.write_text(changelog_content, encoding="utf-8")

    print("=" * 60)
    print(f"棕地项目领养完成（方案 B）")
    print("=" * 60)
    print(f"✅ design.md 已创建：{design_file}")
    print(f"✅ changelog.md 已创建：{changelog_file}")
    print()
    print(f"📋 生成概要：")
    print(f"   项目名称：{info['name']}")
    print(f"   起始版本：v{info['version']}")
    print(f"   开发语言：{info['language']}")
    if info["frameworks"]:
        print(f"   框架：{', '.join(info['frameworks'])}")
    if info["src_dirs"]:
        print(f"   源代码目录：{', '.join(info['src_dirs'])}")
    print()
    print(f"📋 下一步：")
    print(f"   1. 编辑 docs/design.md，补充各章节描述")
    print(f"   2. 验证无误后提交：git add . && git commit -m \"docs(design): 领养现有项目 v{info['version']}\"")
    print(f"   3. 建议创建初始 tag：git tag -a v{info['version']} -m \"初始版本 v{info['version']}\"")
    print(f"   4. 有需求变更时，使用：")
    print(f"      python scripts/design.py --change --desc \"变更描述\" --bump minor")

    # Git 提交
    if is_git_repo(project_root):
        if has_pending_changes(project_root):
            git_add_and_commit(project_root, f"docs(design): 棕地导入 {info['name']} v{info['version']}")
            print(f"✅ Git 已提交：docs(design): 棕地导入 {info['name']} v{info['version']}")

    return 0


def record_change(desc: str, bump_type: str, docs_dir: Path, change_type: Optional[str] = None) -> int:
    """记录变更，递增版本号，更新 changelog.md"""
    design_file = docs_dir / "design.md"
    changelog_file = docs_dir / "changelog.md"

    if not design_file.exists():
        print(f"❌ design.md 不存在：{design_file}")
        print(f"   请先运行：python scripts/design.py --init")
        return 1

    # 读取当前版本号
    current_version = read_version(design_file)
    if not current_version:
        print(f"⚠️  design.md 中未找到版本号，使用默认 0.1.0")
        current_version = "0.1.0"

    # 递增版本号
    new_version = bump_version(current_version, bump_type)

    # 更新 design.md 的版本号和日期
    update_version_in_design(design_file, new_version)
    print(f"✅ design.md 版本号更新：{current_version} → {new_version}")

    # 更新 changelog.md
    today = date.today().isoformat()

    # 读取类型标签
    type_label = change_type or "Changed"
    type_map = {
        "added": "### Added",
        "changed": "### Changed",
        "fixed": "### Fixed",
        "removed": "### Removed",
        "deprecated": "### Deprecated",
        "security": "### Security",
    }
    section_header = type_map.get(type_label.lower(), "### Changed") if change_type else "### Changed"

    entry = f"""## [{new_version}] - {today}

{section_header}
- {desc}

### Status
⏳ 开发中

---

"""

    if changelog_file.exists():
        changelog_content = changelog_file.read_text(encoding="utf-8")
        # 在第一个 --- 分隔线之前插入新版本
        if "---\n" in changelog_content:
            parts = changelog_content.split("---\n", 1)
            # 去掉 entry 末尾的 ---，由原有分隔线承担
            entry_stripped = entry.rstrip()
            if entry_stripped.endswith("---"):
                entry_stripped = entry_stripped[:-3].rstrip()
            changelog_content = parts[0] + entry_stripped + "\n\n---\n" + parts[1]
        else:
            # 没有 --- 分隔符，直接追加到末尾
            changelog_content = changelog_content.rstrip() + "\n\n" + entry
        changelog_file.write_text(changelog_content, encoding="utf-8")
    else:
        # changelog.md 不存在，创建
        changelog_content = "# Changelog\n\n所有重要的产品设计和需求变更都记录在此文件中。\n\n" + entry
        changelog_file.write_text(changelog_content, encoding="utf-8")

    print(f"✅ changelog.md 已更新：[{new_version}] - {desc}")

    # Git 提交
    project_root = docs_dir.parent
    if is_git_repo(project_root):
        if has_pending_changes(project_root):
            git_add_and_commit(project_root, f"docs(design): v{new_version} - {desc}")
            print(f"✅ Git 已提交：docs(design): v{new_version} - {desc}")

    print()
    print(f"📋 产品版本：{current_version} → {new_version}")
    print(f"   变更类型：{bump_type}")
    print(f"   变更描述：{desc}")
    print()
    print(f"📌 请编辑 docs/design.md 更新对应章节的内容")
    print(f"   编辑完成后使用 git add . && git commit 提交代码变更")

    return 0


def rollback_design(version: str, docs_dir: Path, code_only: bool = False, design_only: bool = False) -> int:
    """回退到指定版本

    Args:
        version: 目标版本号（如 1.0.0）
        docs_dir: docs 目录路径
        code_only: 仅回退代码，不回退设计
        design_only: 仅回退设计，不回退代码
    """
    project_root = docs_dir.parent if docs_dir.name == "docs" else find_project_root(docs_dir)

    if not is_git_repo(project_root):
        print(f"❌ 不是 Git 仓库，无法回退")
        return 1

    tag_name = find_tag_for_version(version, project_root)
    if not tag_name:
        print(f"⚠️  未找到版本 v{version} 的 git tag")
        print(f"   当前可用的 tag：")
        tags = get_git_tags(project_root)
        if tags:
            for t in tags[:10]:
                print(f"   {t}")
            if len(tags) > 10:
                print(f"   ... 共 {len(tags)} 个")
        else:
            print(f"   （无可用 tag）")
        print()
        print(f"   如需回退，请先创建 tag：")
        print(f"   git tag -a v{version} -m \"Release v{version}\"")
        return 1

    # 确定要回退的文件
    files_to_restore = []

    if not code_only:
        # 回退设计文档
        design_path = "docs/design.md"
        changelog_path = "docs/changelog.md"
        if (project_root / design_path).exists() or (project_root / changelog_path).exists():
            files_to_restore.extend([design_path, changelog_path])

    if not design_only:
        # 回退代码：src/ 目录
        src_dir = project_root / "src"
        if src_dir.exists():
            files_to_restore.append("src/")

    if not files_to_restore:
        print(f"⚠️  没有需要回退的文件")
        return 1

    print("=" * 60)
    print(f"回退到版本 v{version}")
    print("=" * 60)
    print(f"   Tag：{tag_name}")
    print(f"   回退范围：")
    if not code_only:
        print(f"     - 设计文档 (docs/design.md, docs/changelog.md)")
    if not design_only:
        print(f"     - 代码 (src/)")
    print()

    # 执行回退
    success, message = rollback_files_from_tag(tag_name, project_root, files_to_restore)

    if success:
        print(f"✅ {message}")
    else:
        print(f"⚠️  {message}")
        return 1

    # 提交回退
    print()
    print(f"📌 回退已完成，请检查恢复的文件是否正确")
    print()

    rollback_desc = f"回退到 v{version}"
    if design_only:
        rollback_desc += "（仅设计文档）"
    elif code_only:
        rollback_desc += "（仅代码）"

    if has_pending_changes(project_root):
        print(f"   建议提交：")
        print(f"   git add .")
        print(f'   git commit -m "revert: {rollback_desc}"')
        print()

    if design_only:
        # 设计回退后，更新版本号
        design_file = docs_dir / "design.md"
        current_in_file = read_version(design_file)
        print(f"📋 design.md 当前版本号：{current_in_file}")
        print(f"   如需更新版本号，运行：")
        print(f"   python scripts/design.py --change --desc \"{rollback_desc}\" --bump patch")
    else:
        print(f"📋 建议：")
        print(f"   1. 检查恢复的文件是否正确")
        print(f"   2. git add . && git commit -m \"revert: {rollback_desc}\"")
        print(f"   3. 如需更新版本号，运行：")
        print(f"      python scripts/design.py --change --desc \"{rollback_desc}\" --bump patch")

    return 0


# =============================================================================
# 旧模式：创建独立变更设计文档（保持向后兼容）
# =============================================================================

def create_proposal(name: str, desc: Optional[str], changes_dir: Path) -> int:
    """创建变更设计目录和 {name}-design.md（旧模式）"""
    change_dir = changes_dir / name

    if change_dir.exists():
        design_file = change_dir / f"{name}-design.md"
        if design_file.exists():
            print(f"❌ 变更 '{name}' 已存在：{design_file}")
            print(f"   如需修改，请直接编辑 {name}-design.md")
            return 1

    change_dir.mkdir(parents=True, exist_ok=True)

    content = DESIGN_TEMPLATE.format(
        name=name,
        date=date.today().isoformat(),
    )

    if desc:
        content = content.replace(
            "<!-- 这个变更要达成什么？用 1-3 句话描述预期结果 -->",
            desc,
        )

    design_file = change_dir / f"{name}-design.md"
    design_file.write_text(content, encoding="utf-8")

    progress_content = PROGRESS_TEMPLATE.format(
        name=name,
        date=date.today().isoformat(),
    )
    progress_file = change_dir / f"{name}-progress.md"
    try:
        progress_file.write_text(progress_content, encoding="utf-8")
        print(f"✅ 进度文件已创建：{progress_file}")
    except Exception as e:
        print(f"⚠️  进度文件创建失败：{e}")

    print(f"✅ 设计文档已创建：{design_file}")
    print()
    print(f"📋 下一步：")
    print(f"   1. 编辑 {name}-design.md，填充目标、背景和成功标准")
    print(f"   2. 确认提案完整后，运行：")
    print(f"      python scripts/plans.py --name {name}")

    return 0


# =============================================================================
# 主入口
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="vibe-coding 设计文档管理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
方案 B（推荐）：中央 design.md 模式
  初始化（绿地新项目）：
    python scripts/design.py --init --name "my-project" --lang python --desc "描述"
  棕地领养（已有代码项目）：
    python scripts/design.py --adopt --name "my-project"
  记录变更：
    python scripts/design.py --change --desc "新增XX需求" --bump minor
  回退版本：
    python scripts/design.py --rollback --version 1.0.0

旧模式（向后兼容）：独立变更设计文档
    python scripts/design.py --name add-dark-mode --desc "添加暗色模式支持"

版本递增类型：
  major  - 架构重构 / 不兼容变更 (0.1.0 → 1.0.0)
  minor  - 新增需求 / 修改设计 (1.0.0 → 1.1.0)
  patch  - bug 修复 / 微调 (1.0.0 → 1.0.1)
        """,
    )

    # 方案 B 参数
    parser.add_argument("--init", action="store_true",
                        help="初始化中央 design.md 和 changelog.md（绿地项目）")
    parser.add_argument("--adopt", action="store_true",
                        help="棕地领养：扫描已有项目，生成预填充的 design.md")
    parser.add_argument("--change", action="store_true",
                        help="记录变更，递增版本号")
    parser.add_argument("--rollback", action="store_true",
                        help="回退到指定版本（从 git tag 恢复）")
    parser.add_argument("--bump", choices=["major", "minor", "patch"],
                        default="minor",
                        help="版本递增类型（默认 minor）")
    parser.add_argument("--version", default=None,
                        help="目标版本号（用于 --rollback 和 --adopt）")
    parser.add_argument("--type", default=None, dest="change_type",
                        choices=["added", "changed", "fixed", "removed", "deprecated", "security"],
                        help="变更类型（用于 --change）")
    parser.add_argument("--desc", default=None,
                        help="变更描述（用于 --change 和 --init）")
    parser.add_argument("--lang", "--language", default=None,
                        choices=["python", "javascript", "typescript", "rust", "go"],
                        help="开发语言（用于 --init，默认自动检测或 unknown）")

    # 旧模式参数（向后兼容）
    parser.add_argument("--name", default=None,
                        help="变更名称（旧模式）或项目名称（--init/--adopt 模式）")
    parser.add_argument("--dir", default=None,
                        help="自定义 docs 目录路径（--init/--change）或 changes 目录路径（旧模式）")

    args = parser.parse_args()

    # 方案 B：--adopt（棕地项目，优先于 --init 检查）
    if args.adopt:
        docs_dir = get_docs_dir(Path(__file__).resolve().parent, args.dir)
        return adopt_central_design(args.name, args.version, docs_dir)

    # 方案 B：--init（绿地项目）- 获取开发语言
    if args.init:
        language = args.lang or "unknown"
        docs_dir = get_docs_dir(Path(__file__).resolve().parent, args.dir)
        return init_central_design(args.name or "", args.desc, docs_dir, language)

    # 方案 B：--change
    if args.change:
        docs_dir = get_docs_dir(Path(__file__).resolve().parent, args.dir)
        if not args.desc:
            print("❌ --change 需要指定 --desc 参数")
            print("   示例：python scripts/design.py --change --desc \"新增XX需求\" --bump minor")
            return 1
        return record_change(args.desc, args.bump, docs_dir, args.change_type)

    # 方案 B：--rollback
    if args.rollback:
        docs_dir = get_docs_dir(Path(__file__).resolve().parent, args.dir)
        if not args.version:
            print("❌ --rollback 需要指定 --version 参数")
            print("   示例：python scripts/design.py --rollback --version 1.0.0")
            return 1
        return rollback_design(args.version, docs_dir)

    # 旧模式：--name
    if args.name:
        script_dir = Path(__file__).resolve().parent
        changes_dir = get_changes_dir(script_dir, args.dir)
        return create_proposal(args.name, args.desc, changes_dir)

    # 无参数时显示帮助
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())