#!/usr/bin/env python3
"""
轨迹分析脚本 - Experience Observability
分析收集的轨迹，生成证据报告
"""

import os
import json
import argparse
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict


class TrajectoryAnalyzer:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.evidence_dir = self.project_dir / ".vibe-coding" / "evolution" / "evidence"
        self.analysis_dir = self.evidence_dir / "analysis"

    def analyze_iteration(self, iteration: int) -> dict:
        """分析指定迭代的轨迹"""
        iteration_dir = self.evidence_dir / f"iteration-{iteration:03d}"
        tasks_dir = iteration_dir / "tasks"
        trajectories_dir = iteration_dir / "trajectories"

        analysis = {
            "iteration": iteration,
            "timestamp": datetime.now().isoformat(),
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "patterns": {
                "success": [],
                "failure": []
            },
            "error_types": defaultdict(int),
            "recommendations": []
        }

        task_files = list(tasks_dir.glob("*.md"))
        analysis["total_tasks"] = len(task_files)

        for task_file in task_files:
            content = task_file.read_text(encoding='utf-8')

            if "**Status**: Completed" in content:
                analysis["completed_tasks"] += 1
                self._extract_success_patterns(task_file.stem, trajectories_dir, analysis)

            elif "**Status**: Failed" in content:
                analysis["failed_tasks"] += 1
                self._extract_failure_patterns(task_file.stem, trajectories_dir, analysis)

        self._generate_recommendations(analysis)
        return analysis

    def _extract_success_patterns(self, task_name: str, trajectories_dir: Path, analysis: dict):
        """提取成功模式"""
        trajectory_files = list(trajectories_dir.glob(f"{task_name}_*.md"))

        for traj_file in trajectory_files:
            content = traj_file.read_text(encoding='utf-8')
            patterns = self._find_patterns(content, is_success=True)
            if patterns:
                analysis["patterns"]["success"].extend(patterns)

    def _extract_failure_patterns(self, task_name: str, trajectories_dir: Path, analysis: dict):
        """提取失败模式"""
        trajectory_files = list(trajectories_dir.glob(f"{task_name}_*.md"))

        for traj_file in trajectory_files:
            content = traj_file.read_text(encoding='utf-8')
            patterns = self._find_patterns(content, is_success=False)
            if patterns:
                analysis["patterns"]["failure"].extend(patterns)

            errors = self._find_errors(content)
            for error in errors:
                analysis["error_types"][error] += 1

    def _find_patterns(self, content: str, is_success: bool) -> list:
        """从轨迹中查找模式"""
        patterns = []

        if is_success:
            if "phase:" in content.lower():
                patterns.append({"type": "phase_transition", "count": content.lower().count("phase:")})

            if "task completed" in content.lower():
                patterns.append({"type": "task_completion", "found": True})

        return patterns

    def _find_errors(self, content: str) -> list:
        """从轨迹中查找错误类型"""
        errors = []

        error_patterns = {
            r"FileNotFoundError": "File Not Found",
            r"PermissionError": "Permission Denied",
            r"ImportError": "Import Error",
            r"SyntaxError": "Syntax Error",
            r"TypeError": "Type Error",
            r"ValueError": "Value Error",
            r"TimeoutError": "Timeout",
            r"ConnectionError": "Connection Error",
            r"测试.*失败|test.*fail": "Test Failure",
            r"覆盖率为|coverage": "Coverage Issue"
        }

        for pattern, error_type in error_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                errors.append(error_type)

        return errors

    def _generate_recommendations(self, analysis: dict):
        """根据分析结果生成建议"""
        if analysis["failed_tasks"] > 0:
            failure_rate = analysis["failed_tasks"] / analysis["total_tasks"]

            if failure_rate > 0.3:
                analysis["recommendations"].append({
                    "priority": "high",
                    "category": "quality",
                    "suggestion": f"失败率 {failure_rate*100:.1f}% 过高，建议加强设计审查"
                })

        if analysis["error_types"]:
            top_errors = sorted(analysis["error_types"].items(), key=lambda x: x[1], reverse=True)[:3]
            for error_type, count in top_errors:
                analysis["recommendations"].append({
                    "priority": "medium",
                    "category": "error_type",
                    "suggestion": f"'{error_type}' 错误出现 {count} 次，建议针对性优化"
                })

        if not analysis["patterns"]["success"]:
            analysis["recommendations"].append({
                "priority": "low",
                "category": "observation",
                "suggestion": "缺少成功模式记录，建议增加轨迹详细度"
            })

    def generate_analysis_report(self, iteration: int) -> Path:
        """生成分析报告"""
        analysis = self.analyze_iteration(iteration)

        report = f"""# Iteration {iteration} Analysis Report

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | {analysis['total_tasks']} |
| Completed | {analysis['completed_tasks']} |
| Failed | {analysis['failed_tasks']} |
| Success Rate | {analysis['completed_tasks'] / analysis['total_tasks'] * 100 if analysis['total_tasks'] > 0 else 0:.1f}% |

## Error Distribution

"""

        if analysis["error_types"]:
            for error_type, count in sorted(analysis["error_types"].items(), key=lambda x: x[1], reverse=True):
                report += f"- **{error_type}**: {count} occurrences\n"
        else:
            report += "_No errors recorded_\n"

        report += "\n## Recommendations\n\n"

        if analysis["recommendations"]:
            for i, rec in enumerate(analysis["recommendations"], 1):
                report += f"{i}. [{rec['priority'].upper()}] {rec['category']}: {rec['suggestion']}\n"
        else:
            report += "_No specific recommendations at this time_\n"

        report += f"\n---\n*Report generated at {datetime.now().isoformat()}*\n"

        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        report_file = self.analysis_dir / f"iteration-{iteration:03d}_analysis.md"
        report_file.write_text(report, encoding='utf-8')

        return report_file


def main():
    parser = argparse.ArgumentParser(description="轨迹分析脚本")
    parser.add_argument("--project-dir", required=True, help="项目根目录")
    parser.add_argument("--iteration", type=int, required=True, help="迭代编号")
    parser.add_argument("--action", choices=["analyze", "report"], default="report",
                        help="操作类型")

    args = parser.parse_args()

    analyzer = TrajectoryAnalyzer(args.project_dir)

    if args.action == "analyze":
        analysis = analyzer.analyze_iteration(args.iteration)
        print(json.dumps(analysis, indent=2, ensure_ascii=False))

    elif args.action == "report":
        report_file = analyzer.generate_analysis_report(args.iteration)
        print(f"[Analysis] Report generated: {report_file}")


if __name__ == "__main__":
    main()
