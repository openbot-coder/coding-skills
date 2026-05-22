#!/usr/bin/env python3
"""
证据收集脚本 - Experience Observability
基于 AHE 论文实现，记录每次任务执行轨迹
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path


class EvidenceCollector:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.evidence_dir = self.project_dir / ".vibe-coding" / "evolution" / "evidence"
        self.trajectory_dir = self.evidence_dir / "trajectories"

    def create_iteration_dir(self, iteration: int) -> Path:
        """创建第 N 次迭代的目录"""
        iteration_dir = self.evidence_dir / f"iteration-{iteration:03d}"
        iteration_dir.mkdir(parents=True, exist_ok=True)
        (iteration_dir / "tasks").mkdir(exist_ok=True)
        (iteration_dir / "trajectories").mkdir(exist_ok=True)
        return iteration_dir

    def record_task_start(self, iteration: int, task_name: str, task_type: str):
        """记录任务开始"""
        iteration_dir = self.evidence_dir / f"iteration-{iteration:03d}"
        task_file = iteration_dir / "tasks" / f"{task_name}.md"

        content = f"""# Task: {task_name}

## Metadata
- **Type**: {task_type}
- **Start Time**: {datetime.now().isoformat()}
- **Status**: In Progress

## Task Details
- Task Name: {task_name}
- Task Type: {task_type}

## Progress
- [ ] In Progress
- [ ] Completed
- [ ] Failed
- [ ] Skipped
"""
        task_file.write_text(content, encoding='utf-8')
        print(f"[Evidence] Task {task_name} started at {datetime.now().isoformat()}")
        return task_file

    def record_task_complete(self, iteration: int, task_name: str, status: str, duration: float):
        """记录任务完成"""
        iteration_dir = self.evidence_dir / f"iteration-{iteration:03d}"
        task_file = iteration_dir / "tasks" / f"{task_name}.md"

        if task_file.exists():
            content = task_file.read_text(encoding='utf-8')
            content = content.replace("**Status**: In Progress", f"**Status**: {status}")
            content = content.replace("**Start Time**", f"**End Time**: {datetime.now().isoformat()}\n- **Start Time**")
            content = content.replace("**Duration**:", f"**Duration**: {duration:.2f}s\n- **Duration**:")
            task_file.write_text(content, encoding='utf-8')

        print(f"[Evidence] Task {task_name} completed with status: {status}")
        return task_file

    def record_trajectory(self, iteration: int, task_name: str, phase: str, content: str):
        """记录执行轨迹"""
        iteration_dir = self.evidence_dir / f"iteration-{iteration:03d}"
        trajectory_file = iteration_dir / "trajectories" / f"{task_name}_{phase}.md"

        trajectory_file.write_text(content, encoding='utf-8')
        print(f"[Evidence] Trajectory recorded: {task_name}_{phase}")
        return trajectory_file

    def generate_overview(self, iteration: int):
        """生成迭代概览"""
        iteration_dir = self.evidence_dir / f"iteration-{iteration:03d}"
        tasks_dir = iteration_dir / "tasks"

        task_files = list(tasks_dir.glob("*.md"))
        completed = 0
        failed = 0
        skipped = 0

        for task_file in task_files:
            content = task_file.read_text(encoding='utf-8')
            if "**Status**: Completed" in content:
                completed += 1
            elif "**Status**: Failed" in content:
                failed += 1
            elif "**Status**: Skipped" in content:
                skipped += 1

        overview = f"""# Iteration {iteration} Overview

## Summary
- **Total Tasks**: {len(task_files)}
- **Completed**: {completed}
- **Failed**: {failed}
- **Skipped**: {skipped}
- **Success Rate**: {completed / len(task_files) * 100 if task_files else 0:.1f}%

## Generated At
{datetime.now().isoformat()}
"""
        overview_file = iteration_dir / "overview.md"
        overview_file.write_text(overview, encoding='utf-8')
        print(f"[Evidence] Overview generated for iteration {iteration}")
        return overview_file


def main():
    parser = argparse.ArgumentParser(description="证据收集脚本")
    parser.add_argument("--project-dir", required=True, help="项目根目录")
    parser.add_argument("--iteration", type=int, default=1, help="迭代编号")
    parser.add_argument("--action", choices=["create-iter", "start-task", "complete-task", "trajectory", "overview"],
                        required=True, help="操作类型")

    parser.add_argument("--task-name", help="任务名称")
    parser.add_argument("--task-type", choices=["design", "planning", "implementation", "verification", "archiving"],
                        help="任务类型")
    parser.add_argument("--status", choices=["Completed", "Failed", "Skipped"], help="任务状态")
    parser.add_argument("--duration", type=float, default=0.0, help="任务耗时（秒）")
    parser.add_argument("--phase", help="阶段名称")
    parser.add_argument("--content", help="轨迹内容")

    args = parser.parse_args()

    collector = EvidenceCollector(args.project_dir)

    if args.action == "create-iter":
        iteration_dir = collector.create_iteration_dir(args.iteration)
        print(f"[Evidence] Iteration {args.iteration} directory created: {iteration_dir}")

    elif args.action == "start-task":
        if not args.task_name or not args.task_type:
            print("[Error] --task-name and --task-type required for start-task")
            return
        collector.record_task_start(args.iteration, args.task_name, args.task_type)

    elif args.action == "complete-task":
        if not args.task_name or not args.status:
            print("[Error] --task-name and --status required for complete-task")
            return
        collector.record_task_complete(args.iteration, args.task_name, args.status, args.duration)

    elif args.action == "trajectory":
        if not args.task_name or not args.phase or not args.content:
            print("[Error] --task-name, --phase, and --content required for trajectory")
            return
        collector.record_trajectory(args.iteration, args.task_name, args.phase, args.content)

    elif args.action == "overview":
        collector.generate_overview(args.iteration)


if __name__ == "__main__":
    main()
