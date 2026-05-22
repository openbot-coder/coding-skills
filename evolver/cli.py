#!/usr/bin/env python3
"""
CLI entry point for evolver module.

Usage:
    python -m evolver.cli analyze       # 分析失败 trace，生成 evidence
    python -m evolver.cli evolve        # 运行完整进化循环
    python -m evolver.cli report         # 生成进化报告
    python -m evolver.cli record --skill xxx --reason "..."  # 手动记录失败
    python -m evolver.cli verify         # 验证所有待审 manifest
    python -m evolver.cli stats          # 展示统计数据
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evolver import (
    EvolutionLoop,
    EvidenceDistiller,
    EvolutionAgent,
    TraceCollector,
    Verifier,
    evolution_stats,
)


def cmd_analyze(args):
    """分析失败 traces，生成 evidence"""
    print("\n🔍 [1/3] 收集 traces...")
    collector = TraceCollector()
    collect_result = collector.collect()
    print(f"   收集完成: {collect_result}")

    print("\n🔬 [2/3] 蒸馏 evidence...")
    distiller = EvidenceDistiller()
    evidences = distiller.distill()
    print(f"   生成 {len(evidences)} 条 evidence")

    print("\n📋 [3/3] Evidence 摘要:")
    distiller.print_summary(evidences)

    return 0


def cmd_evolve(args):
    """运行完整进化循环"""
    print("\n🚀 运行完整进化循环...")
    loop = EvolutionLoop()
    result = loop.run()

    for step in result["steps"]:
        print(f"\n  [{step['step']}]")
        for k, v in step["result"].items():
            print(f"    {k}: {v}")

    print(f"\n✅ 进化循环完成 (run_id: {result['run_id']})")
    return 0


def cmd_report(args):
    """生成进化报告"""
    print("\n📊 生成进化报告...")
    loop = EvolutionLoop()
    report = loop.report()

    print("\n=== Evolution Stats ===")
    stats = report["evolution_stats"]
    for k, v in stats.items():
        print(f"  {k}: {v}")

    print("\n=== Trace Summary ===")
    ts = report["trace_summary"]
    for k, v in ts.items():
        print(f"  {k}: {v}")

    print("\n=== Verifier Summary ===")
    vs = report["verifier_summary"]
    for k, v in vs.items():
        print(f"  {k}: {v}")

    if report.get("history_runs"):
        print(f"\n=== History ({len(report['history_runs'])} runs) ===")
        for run in report["history_runs"][-5:]:
            print(f"  {run['run_id']}: steps={len(run['steps'])}")

    return 0


def cmd_record(args):
    """手动记录失败"""
    if not args.skill or not args.reason:
        print("❌ 需要提供 --skill 和 --reason", file=sys.stderr)
        return 1
    collector = TraceCollector()
    trace_id = collector.record_failure(args.skill, args.reason)
    print(f"✅ 记录失败 trace: {trace_id}")
    return 0


def cmd_verify(args):
    """验证所有待审 manifest"""
    print("\n🔬 验证所有待审 manifest...")
    verifier = Verifier()
    result = verifier.verify_all()
    print(f"\n  verified: {result.get('verified', [])}")
    print(f"  rolled_back: {result.get('rolled_back', [])}")
    print(f"  skipped: {result.get('skipped', [])}")
    return 0


def cmd_stats(args):
    """展示统计数据"""
    print("\n📈 Evolution Stats:")
    stats = evolution_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")

    print("\n📈 Trace Count:")
    collector = TraceCollector()
    counts = collector.count_traces()
    for k, v in counts.items():
        print(f"  {k}: {v}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="coding-skills evolver CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("analyze", help="分析失败 traces，生成 evidence")
    subparsers.add_parser("evolve", help="运行完整进化循环")
    subparsers.add_parser("report", help="生成进化报告")
    subparsers.add_parser("verify", help="验证所有待审 manifest")
    subparsers.add_parser("stats", help="展示统计数据")

    p_record = subparsers.add_parser("record", help="手动记录失败")
    p_record.add_argument("--skill", required=True, help="使用的技能名称")
    p_record.add_argument("--reason", required=True, help="失败原因")

    args = parser.parse_args()

    commands = {
        "analyze": cmd_analyze,
        "evolve": cmd_evolve,
        "report": cmd_report,
        "record": cmd_record,
        "verify": cmd_verify,
        "stats": cmd_stats,
    }

    if args.command not in commands:
        parser.print_help()
        return 1

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
