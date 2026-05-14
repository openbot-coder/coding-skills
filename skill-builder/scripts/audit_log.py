#!/usr/bin/env python3
"""
SKILL 审计日志系统 — v2.0
===========================
统一记录 SKILL 创建、审核、调用的日志，支持统计和复盘。

用法:
    python scripts/audit_log.py record <skill-dir> --result pass --checks {...}
    python scripts/audit_log.py record <skill-dir> --result fail --checks {...} --reason "xxx"
    python scripts/audit_log.py stats                            # 查看统计
    python scripts/audit_log.py failures                         # 查看失败案例
    python scripts/audit_log.py list                             # 列出所有记录
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def get_log_dir(project_root: str = None) -> str:
    """获取日志目录"""
    if project_root:
        base = Path(project_root)
    else:
        # 向上查找 skill-builder 根目录
        base = Path(__file__).resolve().parent.parent
    log_dir = base / "logs" / "skill-audit"
    log_dir.mkdir(parents=True, exist_ok=True)
    return str(log_dir)


def get_audit_log_path(log_dir: str) -> str:
    return os.path.join(log_dir, "skill-builder-audit.log")


def get_stats_path(log_dir: str) -> str:
    return os.path.join(log_dir, "skill-call-stats.json")


def get_failures_dir(log_dir: str) -> str:
    path = os.path.join(log_dir, "failure-cases")
    os.makedirs(path, exist_ok=True)
    return path


# ============================================================
# 记录操作
# ============================================================

def record(skill_dir: str, result: str, checks: dict = None, reason: str = "",
           caller: str = "", project_root: str = None):
    """记录一次 SKILL 审核/调用日志"""
    log_dir = get_log_dir(project_root)
    log_path = get_audit_log_path(log_dir)
    skill_name = os.path.basename(os.path.abspath(skill_dir))

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "skill_name": skill_name,
        "result": result,        # "pass" | "fail"
        "checks": checks or {},
        "reason": reason,
        "caller": caller,
    }

    # 追加到日志文件
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # 更新统计数据
    stats_path = get_stats_path(log_dir)
    stats = {}
    if os.path.exists(stats_path):
        with open(stats_path, "r", encoding="utf-8") as f:
            stats = json.load(f)

    today = timestamp[:10]
    if today not in stats:
        stats[today] = {"total": 0, "pass": 0, "fail": 0, "skills": {}}
    stats[today]["total"] += 1
    stats[today][result] += 1
    if skill_name not in stats[today]["skills"]:
        stats[today]["skills"][skill_name] = {"pass": 0, "fail": 0}
    stats[today]["skills"][skill_name][result] += 1

    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    # 记录失败案例
    if result == "fail" and (reason or checks):
        fail_dir = get_failures_dir(log_dir)
        fail_filename = f"{timestamp[:10]}-{timestamp[11:13]}{timestamp[14:16]}{timestamp[17:19]}-{skill_name}.md"
        fail_path = os.path.join(fail_dir, fail_filename)
        with open(fail_path, "w", encoding="utf-8") as f:
            f.write(f"# 失败案例: {skill_name}\n\n")
            f.write(f"- **时间**: {timestamp}\n")
            f.write(f"- **SKILL**: {skill_name}\n")
            f.write(f"- **来源**: {caller or '未知'}\n\n")
            f.write(f"## 原因\n\n{reason or '无详细信息'}\n\n")
            if checks:
                f.write("## 检查明细\n\n")
                for check_name, check_result in checks.items():
                    status = "✅" if check_result.get("pass") else "❌"
                    f.write(f"- {status} {check_name}: {check_result.get('message', '')}\n")
                    if not check_result.get("pass"):
                        for key in ["errors", "warnings", "issues", "findings"]:
                            if key in check_result:
                                for item in check_result[key]:
                                    if isinstance(item, dict):
                                        f.write(f"    - {item.get('description', item)}\n")
                                    else:
                                        f.write(f"    - {item}\n")

    return entry


# ============================================================
# 查询操作
# ============================================================

def show_stats(project_root: str = None):
    """显示统计信息"""
    log_dir = get_log_dir(project_root)
    stats_path = get_stats_path(log_dir)
    if not os.path.exists(stats_path):
        print("暂无统计数据")
        return

    with open(stats_path, "r", encoding="utf-8") as f:
        stats = json.load(f)

    print(f"\n{'='*50}")
    print("  SKILL 审计统计")
    print(f"{'='*50}")

    total_pass = sum(d["pass"] for d in stats.values())
    total_fail = sum(d["fail"] for d in stats.values())
    total_all = sum(d["total"] for d in stats.values())

    print(f"  总记录: {total_all}")
    print(f"  ✅ 通过: {total_pass}")
    print(f"  ❌ 失败: {total_fail}")
    if total_all > 0:
        print(f"  成功率: {total_pass / total_all * 100:.1f}%")
    print()

    for date in sorted(stats.keys(), reverse=True)[:14]:  # 最近14天
        d = stats[date]
        bar_pass = "█" * int(d["pass"] / max(d["total"], 1) * 20)
        bar_fail = "░" * (20 - len(bar_pass))
        print(f"  {date}  [{bar_pass}{bar_fail}]  {d['total']}次"
              f"  (✅{d['pass']} ❌{d['fail']})")

    print(f"\n  SKILL 排行:")
    skill_totals = {}
    for d in stats.values():
        for sname, sdata in d.get("skills", {}).items():
            if sname not in skill_totals:
                skill_totals[sname] = {"pass": 0, "fail": 0}
            skill_totals[sname]["pass"] += sdata["pass"]
            skill_totals[sname]["fail"] += sdata["fail"]

    for sname in sorted(skill_totals, key=lambda x: skill_totals[x]["fail"], reverse=True):
        s = skill_totals[sname]
        rate = s["pass"] / max(s["pass"] + s["fail"], 1) * 100
        print(f"    {sname}: {s['pass']}✅/{s['fail']}❌ ({rate:.0f}%)")


def show_failures(project_root: str = None):
    """显示所有失败案例"""
    log_dir = get_log_dir(project_root)
    fail_dir = get_failures_dir(log_dir)
    files = sorted(os.listdir(fail_dir), reverse=True)

    if not files:
        print("暂无失败案例")
        return

    print(f"\n  📂 失败案例 ({len(files)} 个):")
    for f in files[:20]:  # 最近20条
        print(f"    - {f}")


def list_records(project_root: str = None):
    """列出最近的审核记录"""
    log_dir = get_log_dir(project_root)
    log_path = get_audit_log_path(log_dir)
    if not os.path.exists(log_path):
        print("暂无审核记录")
        return

    print(f"\n{'='*50}")
    print("  最近审核记录")
    print(f"{'='*50}")

    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 取最近30条
    for line in lines[-30:]:
        try:
            entry = json.loads(line.strip())
            icon = "✅" if entry["result"] == "pass" else "❌"
            print(f"  {icon} {entry['timestamp']} | {entry['skill_name']} | {entry.get('reason', entry['result'])}")
        except json.JSONDecodeError:
            continue


# ============================================================
# 主函数
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="SKILL 审计日志系统 v2.0")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # record
    record_parser = subparsers.add_parser("record", help="记录一条日志")
    record_parser.add_argument("skill_dir", help="SKILL 目录路径")
    record_parser.add_argument("--result", required=True, choices=["pass", "fail"],
                               help="审核结果")
    record_parser.add_argument("--checks", type=str, default="{}",
                               help="检查明细 JSON")
    record_parser.add_argument("--reason", default="", help="失败原因")
    record_parser.add_argument("--caller", default="", help="调用来源")
    record_parser.add_argument("--project-root", default=None, help="项目根目录")

    # stats
    subparsers.add_parser("stats", help="查看统计")
    subparsers.add_parser("failures", help="查看失败案例")
    subparsers.add_parser("list", help="列出最近记录")

    args = parser.parse_args()

    if args.command == "record":
        checks = json.loads(args.checks) if isinstance(args.checks, str) else args.checks
        entry = record(args.skill_dir, args.result, checks, args.reason,
                       args.caller, args.project_root)
        print(f"✅ 已记录: {entry['skill_name']} — {args.result}")

    elif args.command == "stats":
        show_stats(args.project_root if hasattr(args, 'project_root') else None)

    elif args.command == "failures":
        show_failures()

    elif args.command == "list":
        list_records()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
