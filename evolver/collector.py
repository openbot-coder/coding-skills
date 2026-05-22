import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from .manifest import Manifest

TRACES_DIR = Path(__file__).resolve().parent / "traces"
EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"
HISTORY_DIR = Path(__file__).resolve().parent / "history"


class TraceCollector:
    def __init__(self, traces_dir: Optional[str] = None):
        self.traces_dir = Path(traces_dir) if traces_dir else TRACES_DIR

    def collect(self) -> dict:
        trace_files = sorted(self.traces_dir.glob("*.jsonl"))
        new_traces = 0
        total_fail = 0
        total_success = 0
        skills_seen = set()

        for tf in trace_files:
            with open(tf, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        trace = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    new_traces += 1
                    if trace.get("outcome") == "fail":
                        total_fail += 1
                    else:
                        total_success += 1
                    if "skill_used" in trace:
                        skills_seen.add(trace["skill_used"])

        total = total_fail + total_success
        return {
            "new_traces": new_traces,
            "summary": {
                "total_traces": total,
                "failed_traces": total_fail,
                "success_rate": f"{total_success / max(total, 1) * 100:.0f}%",
                "skills_seen": sorted(skills_seen),
                "trace_files": [f.name for f in trace_files],
            },
        }

    def load_traces(self, filename: str = "manual_traces.jsonl") -> list[dict]:
        filepath = self.traces_dir / filename
        if not filepath.exists():
            return []
        traces = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        traces.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return traces

    def save_trace(self, trace: dict, filename: str = "manual_traces.jsonl") -> None:
        self.traces_dir.mkdir(parents=True, exist_ok=True)
        filepath = self.traces_dir / filename
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace, ensure_ascii=False) + "\n")

    def record_failure(self, skill_used: str, reason: str) -> str:
        trace_id = f"manual-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        trace = {
            "task_id": trace_id,
            "skill_used": skill_used,
            "skill_type": "unknown",
            "conversations": [],
            "outcome": "fail",
            "failure_info": {"reason": reason},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": 0,
        }
        self.save_trace(trace)
        return trace_id

    def get_failed_traces(self) -> list[dict]:
        return self._load_traces_by_outcome("fail")

    def get_success_traces(self) -> list[dict]:
        return self._load_traces_by_outcome("success")

    def _load_traces_by_outcome(self, outcome: str) -> list[dict]:
        results = []
        for tf in sorted(self.traces_dir.glob("*.jsonl")):
            with open(tf, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        trace = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if trace.get("outcome") == outcome:
                        results.append(trace)
        return results

    def count_traces(self) -> dict:
        failed = len(self.get_failed_traces())
        success = len(self.get_success_traces())
        total = failed + success
        return {
            "total_traces": total,
            "failed_traces": failed,
            "success_traces": success,
            "success_rate": f"{success / max(total, 1) * 100:.0f}%" if total > 0 else "N/A",
        }
