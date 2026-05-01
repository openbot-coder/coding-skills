#!/usr/bin/env python3
"""vibe-coding 阶段1：创建变更提案

用法：
    python scripts/propose.py --name add-dark-mode --desc "添加暗色模式支持"
    python scripts/propose.py --name fix-login-bug

将在 docs/changes/{name}/ 下生成 proposal.md 模板。
"""

import argparse
import sys
from datetime import date
from pathlib import Path

# 解决 Windows 控制台 Unicode 输出问题
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from typing import Optional


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


PROPOSAL_TEMPLATE = """# 提案：{name}

> 创建日期：{date}
> 状态：待填充

## 提案状态

| 阶段 | 状态 | 日期 | 说明 |
|------|------|------|------|
| 提案编写 | ✅ | {date} | |
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


STATUS_TEMPLATE = """# 状态跟踪：{name}

> 创建日期：{date}
> 最后更新：-

## 基本信息

| 字段 | 值 |
|------|---|
| **变更名称** | {name} |
| **当前阶段** | 阶段1：propose |
| **创建日期** | {date} |
| **最后更新** | - |

## 提案状态

| 阶段 | 状态 | 日期 | 说明 |
|------|------|------|------|
| 提案编写 | ✅ | {date} | |
| Agent 审查 | ⏳ | - | |
| 用户批准 | ⏳ | - | |

---

## 阶段2：plans

| 字段 | 值 |
|------|---|
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

## 阶段3：execute

| 字段 | 值 |
|------|---|
| **状态** | ⏳ |
| **开始时间** | - |
| **完成时间** | - |
| **当前任务** | - |

### 任务执行进度

| # | 任务 | 状态 | 开始时间 | 完成时间 | 功能点进度 |
|---|------|------|----------|----------|------------|
| - | - | - | - | - | - |

---

## 阶段4：verify

| 字段 | 值 |
|------|---|
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

| # | 问题描述 | 根因 | 修复方案 | 状态 | 记录时间 |
|---|----------|------|----------|------|----------|
| - | - | - | - | - | - |

---

## 阶段5：archive

| 字段 | 值 |
|------|---|
| **状态** | ⏳ |
| **归档时间** | - |
| **Git 标签** | - |
| **归档路径** | - |

---

## 变更记录

| 日期 | 阶段 | 操作 | 说明 |
|------|------|------|------|
| {date} | 阶段1 | 创建 | 变更提案已创建 |
"""


def create_proposal(name: str, desc: Optional[str], changes_dir: Path) -> int:
    """创建变更提案目录和 proposal.md"""
    change_dir = changes_dir / name

    # 检查是否已存在
    if change_dir.exists():
        proposal_file = change_dir / "proposal.md"
        if proposal_file.exists():
            print(f"❌ 变更 '{name}' 已存在：{proposal_file}")
            print(f"   如需修改，请直接编辑 proposal.md")
            return 1

    # 创建目录
    change_dir.mkdir(parents=True, exist_ok=True)

    # 生成 proposal.md
    content = PROPOSAL_TEMPLATE.format(
        name=name,
        date=date.today().isoformat(),
    )

    # 如果有描述，填充到目标中
    if desc:
        content = content.replace(
            "<!-- 这个变更要达成什么？用 1-3 句话描述预期结果 -->",
            desc,
        )

    proposal_file = change_dir / "proposal.md"
    proposal_file.write_text(content, encoding="utf-8")

    # 创建 STATUS.md
    status_content = STATUS_TEMPLATE.format(
        name=name,
        date=date.today().isoformat(),
    )
    status_file = change_dir / "STATUS.md"
    try:
        status_file.write_text(status_content, encoding="utf-8")
        print(f"✅ 状态文件已创建：{status_file}")
    except Exception as e:
        print(f"⚠️  状态文件创建失败：{e}")

    # 输出结果
    print(f"✅ 提案已创建：{proposal_file}")
    print()
    print(f"📋 下一步：")
    print(f"   1. 编辑 proposal.md，填充目标、背景和成功标准")
    print(f"   2. 确认提案完整后，运行：")
    print(f"      python scripts/plans.py --name {name}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="vibe-coding 阶段1：创建变更提案",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例：\n"
               "  python scripts/propose.py --name add-dark-mode\n"
               "  python scripts/propose.py --name fix-login-bug --desc '修复登录超时问题'",
    )
    parser.add_argument("--name", required=True, help="变更名称（小写字母和连字符）")
    parser.add_argument("--desc", default=None, help="简要描述")
    parser.add_argument("--dir", default=None, help="自定义 changes 目录路径")

    args = parser.parse_args()

    # 验证名称格式
    if not args.name.replace("-", "").replace("_", "").isalnum():
        print(f"❌ 变更名称格式错误：'{args.name}'")
        print(f"   仅允许小写字母、数字、连字符和下划线")
        return 1

    script_dir = Path(__file__).resolve().parent
    changes_dir = get_changes_dir(script_dir, args.dir)

    return create_proposal(args.name, args.desc, changes_dir)


if __name__ == "__main__":
    sys.exit(main())
