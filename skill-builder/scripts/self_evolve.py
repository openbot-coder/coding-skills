#!/usr/bin/env python3
"""
Backward-compat wrapper for self-evolve.

原来的命令:
    python scripts/self_evolve.py analyze
    python scripts/self_evolve.py suggest
    python scripts/self_evolve.py update-rules

新命令（推荐）:
    python -m evolver.cli analyze
    python -m evolver.cli evolve
    python -m evolver.cli report
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from evolver import EvolutionLoop, EvidenceDistiller, EvolutionAgent
from evolver.cli import cmd_analyze, cmd_evolve, cmd_report


def main():
    if len(sys.argv) < 2:
        print("Usage: python self_evolve.py <command>")
        print("Commands: analyze, suggest, evolve, report")
        return 1

    cmd = sys.argv[1]

    if cmd == "analyze":
        # 原来的 analyze 功能：蒸馏 evidence
        from evolver.cli import cmd_analyze as _cmd
        import argparse
        return _cmd(argparse.Namespace())

    elif cmd == "suggest":
        # 原来的 suggest 功能：生成修改建议
        print("🔧 正在生成修改建议...")
        distiller = EvidenceDistiller()
        evidences = distiller.distill()
        if not evidences:
            print("没有失败 traces 可分析")
            return 0
        agent = EvolutionAgent()
        proposals = agent.propose(evidences)
        print(f"\n生成了 {len(proposals)} 个修改方案:")
        for manifest, instructions in proposals:
            print(f"\n📝 [{manifest.edit_id}] {manifest.change_summary}")
            print(f"   组件: {manifest.component}")
            print(f"   文件: {manifest.file_path}")
        return 0

    elif cmd == "evolve":
        # 新增：运行完整进化循环
        from evolver.cli import cmd_evolve as _cmd
        import argparse
        return _cmd(argparse.Namespace())

    elif cmd == "report":
        from evolver.cli import cmd_report as _cmd
        import argparse
        return _cmd(argparse.Namespace())

    elif cmd == "stats":
        from evolver.cli import cmd_stats as _cmd
        import argparse
        return _cmd(argparse.Namespace())

    elif cmd == "update-rules":
        # update-rules 现在通过 manifest + verifier 实现
        print("update-rules 已废弃，请使用 'python -m evolver.cli evolve' 代替")
        print("\n新的进化流程:")
        print("  1. python -m evolver.cli analyze   # 分析失败")
        print("  2. python -m evolver.cli evolve    # 运行进化循环（包含 propose + apply + verify）")
        print("  3. python -m evolver.cli report     # 查看报告")
        return 0

    else:
        print(f"未知命令: {cmd}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
