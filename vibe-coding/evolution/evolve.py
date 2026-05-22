#!/usr/bin/env python3
"""
进化主脚本 - 基于 AHE 论文实现自我升级功能
整合证据收集、轨迹分析、变更管理
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from collect_evidence import EvidenceCollector
from analyze_trajectories import TrajectoryAnalyzer


class EvolveAgent:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.evolution_dir = self.project_dir / ".vibe-coding" / "evolution"
        self.evidence_dir = self.evolution_dir / "evidence"
        self.change_manifests_dir = self.evolution_dir / "change-manifests"

        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.change_manifests_dir.mkdir(parents=True, exist_ok=True)

        self.evolve_log = self.evolution_dir / "evolve-log.md"

    def get_current_iteration(self) -> int:
        """获取当前迭代编号"""
        if not self.evidence_dir.exists():
            return 1

        iterations = [d for d in self.evidence_dir.iterdir()
                      if d.is_dir() and d.name.startswith("iteration-")]

        if not iterations:
            return 1

        max_iter = 0
        for d in iterations:
            try:
                num = int(d.name.split("-")[1])
                max_iter = max(max_iter, num)
            except (ValueError, IndexError):
                pass

        return max_iter + 1

    def create_change_manifest(self, iteration: int, template_path: Path = None) -> Path:
        """创建变更清单"""
        if template_path is None:
            template_path = Path(__file__).parent / "change-manifest-template.md"

        template = template_path.read_text(encoding='utf-8')

        manifest = template.replace("{N}", f"{iteration:03d}")
        manifest = manifest.replace("{YYYY-MM-DD HH:MM:SS}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        manifest_file = self.change_manifests_dir / f"iteration-{iteration:03d}_manifest.md"
        manifest_file.write_text(manifest, encoding='utf-8')

        print(f"[Evolve] Change manifest created: {manifest_file}")
        return manifest_file

    def init_evolution(self):
        """初始化进化目录"""
        iteration = self.get_current_iteration()

        collector = EvidenceCollector(str(self.project_dir))
        collector.create_iteration_dir(iteration)

        self.create_change_manifest(iteration)

        self._update_evolve_log(iteration, "initialized")

        print(f"[Evolve] Evolution initialized for iteration {iteration}")
        return iteration

    def record_phase(self, iteration: int, phase: str, content: str):
        """记录阶段信息"""
        collector = EvidenceCollector(str(self.project_dir))
        collector.record_trajectory(iteration, "workflow", phase, content)

    def analyze_and_recommend(self, iteration: int):
        """分析并生成建议"""
        analyzer = TrajectoryAnalyzer(str(self.project_dir))
        report_file = analyzer.generate_analysis_report(iteration)

        print(f"[Evolve] Analysis report: {report_file}")
        return report_file

    def update_manifest(self, iteration: int, updates: dict):
        """更新变更清单"""
        manifest_file = self.change_manifests_dir / f"iteration-{iteration:03d}_manifest.md"

        if not manifest_file.exists():
            print(f"[Error] Manifest not found: {manifest_file}")
            return

        content = manifest_file.read_text(encoding='utf-8')

        if "problems" in updates:
            problems_section = "\n".join([
                f"| {i+1} | {p['desc']} | {p['severity']} | {p.get('scope', 'N/A')} |"
                for i, p in enumerate(updates["problems"])
            ])
            content = content.replace("| 1 | ... | ... | ... |", problems_section)

        if "verification" in updates:
            for i, v in enumerate(updates["verification"]):
                old = f"| {i+1} | 预期改进 | 实际结果 | ✅ 达成 / ❌ 未达成 |"
                new = f"| {i+1} | {v['expected']} | {v['actual']} | {'✅ 达成' if v['achieved'] else '❌ 未达成'} |"
                content = content.replace(old, new)

        if "status" in updates:
            content = content.replace("Status | Draft", f"Status | {updates['status']}")

        manifest_file.write_text(content, encoding='utf-8')
        print(f"[Evolve] Manifest updated: {manifest_file}")

    def _update_evolve_log(self, iteration: int, action: str):
        """更新进化日志"""
        entry = f"\n## Iteration {iteration:03d} - {datetime.now().isoformat()}\n\n"
        entry += f"- **Action**: {action}\n"
        entry += f"- **Timestamp**: {datetime.now().isoformat()}\n"

        if self.evolve_log.exists():
            existing = self.evolve_log.read_text(encoding='utf-8')
            header = existing.split("\n## Iteration")[0]
            entries = existing.split("\n## Iteration")[1:]

            self.evolve_log.write_text(
                header + entry + "\n## Iteration ".join(entries),
                encoding='utf-8'
            )
        else:
            log_content = f"""# Evolution Log

{entry}
"""
            self.evolve_log.write_text(log_content, encoding='utf-8')

        print(f"[Evolve] Log updated: {self.evolve_log}")

    def run_full_cycle(self, iteration: int = None):
        """运行完整进化循环"""
        if iteration is None:
            iteration = self.get_current_iteration()

        print(f"[Evolve] Starting evolution cycle for iteration {iteration}")

        self.record_phase(iteration, "evidence_collection", "Evidence collection started")

        report_file = self.analyze_and_recommend(iteration)

        self.record_phase(iteration, "analysis_complete", f"Analysis report: {report_file}")

        self._update_evolve_log(iteration, "cycle_completed")

        print(f"[Evolve] Evolution cycle {iteration} completed")
        return iteration


def main():
    parser = argparse.ArgumentParser(description="vibe-coding 进化主脚本")
    parser.add_argument("--project-dir", required=True, help="项目根目录")
    parser.add_argument("--action", choices=["init", "record", "analyze", "update", "cycle", "status"],
                        required=True, help="操作类型")
    parser.add_argument("--iteration", type=int, help="迭代编号（可选）")
    parser.add_argument("--phase", help="阶段名称（用于 record）")
    parser.add_argument("--content", help="内容（用于 record）")
    parser.add_argument("--manifest-update", help="变更清单更新（JSON格式）")

    args = parser.parse_args()

    agent = EvolveAgent(args.project_dir)

    if args.action == "init":
        iteration = agent.init_evolution()
        print(f"[Evolve] Initialized iteration {iteration}")

    elif args.action == "record":
        if not args.iteration or not args.phase or not args.content:
            print("[Error] --iteration, --phase, and --content required for record")
            return
        agent.record_phase(args.iteration, args.phase, args.content)

    elif args.action == "analyze":
        iteration = args.iteration or agent.get_current_iteration()
        agent.analyze_and_recommend(iteration)

    elif args.action == "update":
        if not args.iteration:
            print("[Error] --iteration required for update")
            return
        import json
        updates = json.loads(args.manifest_update or "{}")
        agent.update_manifest(args.iteration, updates)

    elif args.action == "cycle":
        iteration = agent.run_full_cycle(args.iteration)
        print(f"[Evolve] Cycle completed for iteration {iteration}")

    elif args.action == "status":
        iteration = agent.get_current_iteration()
        print(f"[Evolve] Current iteration: {iteration}")
        print(f"[Evolve] Evolution dir: {agent.evolution_dir}")


if __name__ == "__main__":
    main()
