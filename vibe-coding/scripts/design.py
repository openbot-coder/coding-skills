#!/usr/bin/env python3
"""vibe-coding 阶段1：创建变更设计文档

用法：
    python scripts/design.py --name add-dark-mode --desc "添加暗色模式支持"
    python scripts/design.py --name fix-login-bug

将生成 {name}-design.md 和 {name}-progress.md 模板。
"""

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Optional

from common import (
    setup_unicode_output, find_project_root, get_changes_dir,
    PROGRESS_TEMPLATE_TASK_SECTION
)


setup_unicode_output()


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
|------|------|
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
|------|------|
| **状态** | ⏳ |
| **开始时间** | - |
| **完成时间** | - |
| **当前任务** | - |

### 任务执行进度

| # | 任务名称 | 状态 | 优先级 | 预计工时 | 功能点数 | 完成时间 |
|---|----------|------|--------|----------|----------|----------|
| - | - | - | - | - | - | - |

---

## 阶段4：测试验证

| 字段 | 值 |
|------|------|
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
|------|------|
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


def create_proposal(name: str, desc: Optional[str], changes_dir: Path) -> int:
    """创建变更设计目录和 {name}-design.md"""
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="vibe-coding 阶段1：创建变更设计文档",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例：\n"
               "  python scripts/design.py --name add-dark-mode\n"
               "  python scripts/design.py --name fix-login-bug --desc '修复登录超时问题'",
    )
    parser.add_argument("--name", required=True, help="变更名称（小写字母和连字符）")
    parser.add_argument("--desc", default=None, help="简要描述")
    parser.add_argument("--dir", default=None, help="自定义 changes 目录路径")

    args = parser.parse_args()

    if not args.name.replace("-", "").replace("_", "").isalnum():
        print(f"❌ 变更名称格式错误：'{args.name}'")
        print(f"   仅允许小写字母、数字、连字符和下划线")
        return 1

    script_dir = Path(__file__).resolve().parent
    changes_dir = get_changes_dir(script_dir, args.dir)

    return create_proposal(args.name, args.desc, changes_dir)


if __name__ == "__main__":
    sys.exit(main())
