#!/usr/bin/env python3
"""
evolver CLI — coding-skills 自我进化引擎入口

基于 AHE 三大可观测性设计：
  - 经验可观测性：轨迹采集 & 证据蒸馏
  - 组件可观测性：失败类型 → 组件定位
  - 决策可观测性：manifest + 预测 + 验证 + 回滚

用法:
    python -m evolver.cli analyze           # 采集轨迹 + 蒸馏 evidence
    python -m evolver.cli evolve             # 执行完整进化循环
    python -m evolver.cli proposal           # 基于 evidence 生成修改方案
    python -m evolver.cli verify             # 验证 + 回滚 pending manifest
    python -m evolver.cli record <skill> <reason>  # 手动记录一条失败
    python -m evolver.cli report             # 生成进化报告
    python -m evolver.cli stats              # 查看进化统计
"""

import argparse
import json
import sys
from pathlib import Path

# 确保模块路径正确
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evolver.evolver import EvolutionLoop


def main():
    parser = argparse.ArgumentParser(
        description="coding-skills AHE 自我进化引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python -m evolver.cli analyze              # 分析失败模式
    python -m evolver.cli evolve                # 一键进化
    python -m evolver.cli record vibe-coding "工具路径错误: scripts/不存在的文件"
    python -m evolver.cli report                # 查看进化报告
        """,
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="analyze",
        choices=["analyze", "evolve", "proposal", "verify", "record", "report", "stats"],
        help="操作类型",
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="额外参数 (record 命令需要: <skill_used> <reason>)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON 格式输出",
    )

    args = parser.parse_args()

    loop = EvolutionLoop()

    if args.command == "analyze":
        result = {}
        collect = loop.collect()
        result["collect"] = collect
        if not args.json:
            print(f"📊 轨迹采集: {collect['new_traces']} 条新轨迹")
            print(f"   总轨迹: {collect['summary']['total_traces']} 条")
            print(f"   失败率: {collect['summary']['success_rate']}")
            print(f"   涉及技能: {', '.join(collect['summary']['skills_seen'])}")

        evidences = loop.distill()
        result["evidence_count"] = len(evidences)

        if not args.json:
            print(f"\n🔬 证据蒸馏: {len(evidences)} 条 evidence")
            for e in evidences:
                bar = "█" * min(e.frequency, 20)
                print(f"  {bar} [{e.severity}] {e.failure_type} x{e.frequency}")
                print(f"     🎯 组件: {e.component} → {e.file_path}")
                print(f"     💡 建议: {e.suggestion}")
                if e.evidence_snippets:
                    print(f"     📝 证据: {e.evidence_snippets[0][:100]}")

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "evolve":
        print(f"{'='*60}")
        print(f"  AHE 进化循环")
        print(f"{'='*60}")
        result = loop.run()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\n运行 ID: {result['run_id']}")
            for step in result["steps"]:
                print(f"  ✅ {step['step']}: {step['result']}")

    elif args.command == "proposal":
        evidences = loop.distill()
        if not evidences:
            print("暂无 evidence，无法生成修改方案")
            return

        proposals = loop.evolve(evidences)
        if not proposals:
            print("没有需要修改的组件")
            return

        if args.json:
            output = [{"manifest": m.to_dict(), "instructions": i} for m, i in proposals]
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            for manifest, instructions in proposals:
                print(f"\n{'─'*60}")
                print(f"  📝 方案: {manifest.edit_id}")
                print(f"  🎯 组件: {manifest.component}")
                print(f"  📄 文件: {manifest.file_path}")
                print(f"  💡 修改: {manifest.change_summary}")
                print(f"  📊 预测: {manifest.predicted_impact}")
                print(f"\n  修改指令:")
                for line in instructions.split('\n'):
                    print(f"    {line}")

    elif args.command == "verify":
        result = loop.verify()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"验证结果:")
            print(f"  ✅ 通过: {len(result.get('verified', []))}")
            print(f"  ❌ 回滚: {len(result.get('rolled_back', []))}")
            print(f"  ⏭ 跳过: {len(result.get('skipped', []))}")

    elif args.command == "record":
        if len(args.args) < 1:
            print("用法: python -m evolver.cli record <skill_used> [reason]")
            return
        skill_used = args.args[0]
        reason = " ".join(args.args[1:]) if len(args.args) > 1 else ""
        trace_id = loop.record_failure(skill_used, reason)
        if args.json:
            print(json.dumps({"trace_id": trace_id}, ensure_ascii=False))
        else:
            print(f"记录成功 | trace_id: {trace_id} | skill: {skill_used}")

    elif args.command == "report":
        report = loop.report()
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            stats = report.get("evolution_stats", {})
            trace_summary = report.get("trace_summary", {})
            verifier_summary = report.get("verifier_summary", {})

            print(f"{'='*60}")
            print(f"  coding-skills 自我进化报告")
            print(f"{'='*60}")
            print(f"\n📊 进化统计")
            print(f"{'─'*40}")
            print(f"  总编辑次数: {stats.get('total_edits', 0)}")
            print(f"  已验证通过: {stats.get('verified', 0)}")
            print(f"  已回滚: {stats.get('rolled_back', 0)}")
            print(f"  待验证: {stats.get('pending', 0)}")
            print(f"  成功率: {stats.get('success_rate', 'N/A')}")
            print(f"\n📊 轨迹统计")
            print(f"{'─'*40}")
            print(f"  总轨迹: {trace_summary.get('total_traces', 0)}")
            print(f"  失败轨迹: {trace_summary.get('failed_traces', 0)}")
            print(f"  成功率: {trace_summary.get('success_rate', 'N/A')}")
            print(f"  技能: {', '.join(trace_summary.get('skills_seen', []))}")
            print(f"\n✅ 验证统计")
            print(f"{'─'*40}")
            print(f"  总: {verifier_summary.get('total', 0)}")
            print(f"  通过: {verifier_summary.get('verified', 0)}")
            print(f"  回滚: {verifier_summary.get('rolled_back', 0)}")
            print(f"  待验证: {verifier_summary.get('pending', 0)}")
            print(f"\n📋 历史运行")
            for run in report.get("history_runs", []):
                print(f"  {run.get('run_id', '?')}")

    elif args.command == "stats":
        from .manifest import evolution_stats as es
        s = es()
        if args.json:
            print(json.dumps(s, ensure_ascii=False, indent=2))
        else:
            print(f"进化统计:")
            print(f"  总编辑: {s['total_edits']}")
            print(f"  已验证: {s['verified']}")
            print(f"  已回滚: {s['rolled_back']}")
            print(f"  待验证: {s['pending']}")
            print(f"  成功率: {s['success_rate']}")


if __name__ == "__main__":
    main()
