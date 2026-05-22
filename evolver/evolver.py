import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .collector import TraceCollector
from .evidence_distiller import EvidenceDistiller, Evidence
from .evolution_agent import EvolutionAgent
from .manifest import Manifest, load_manifests
from .verifier import Verifier
from .harness_map import HarnessMapper

RESULTS_DIR = Path(__file__).resolve().parent / "history"


class EvolutionLoop:
    def __init__(self):
        self.collector = TraceCollector()
        self.distiller = EvidenceDistiller()
        self.agent = EvolutionAgent()
        self.verifier = Verifier()

    def run(self) -> dict:
        steps = []
        run_id = datetime.now().strftime("%Y%m%dT%H%M%S")

        # 1. collect
        collect_result = self.collector.collect()
        steps.append({"step": "collect", "result": collect_result})

        # 2. distill
        evidences = self.distiller.distill()
        steps.append({"step": "distill", "result": {"evidence_count": len(evidences)}})

        # 3. evolve
        proposals = self.agent.propose(evidences)
        steps.append({"step": "evolve", "result": {"proposals_count": len(proposals)}})

        # 4. apply
        applied = []
        for manifest, instructions in proposals:
            app = self.agent.apply_proposal(manifest, instructions)
            applied.append(app)
        steps.append({"step": "apply", "result": {"applied_count": len(applied)}})

        # 5. verify
        verification = self.verifier.verify_all()
        steps.append({"step": "verify", "result": verification})

        result = {"run_id": run_id, "steps": steps}
        self._save_run(result)
        return result

    def collect(self) -> dict:
        return self.collector.collect()

    def distill(self) -> list[Evidence]:
        return self.distiller.distill()

    def evolve(self, evidences: list[Evidence]) -> list[tuple[Manifest, str]]:
        return self.agent.propose(evidences)

    def verify(self) -> dict:
        return self.verifier.verify_all()

    def record_failure(self, skill_used: str, reason: str) -> str:
        return self.collector.record_failure(skill_used, reason)

    def report(self) -> dict:
        trace_summary = self.collector.count_traces()
        traces_dir = Path(__file__).resolve().parent / "traces"
        trace_files = sorted(traces_dir.glob("*.jsonl")) if traces_dir.exists() else []
        trace_summary["trace_files"] = [f.name for f in trace_files]
        skills_seen = set()
        for tf in trace_files:
            with open(tf, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        t = json.loads(line)
                        if "skill_used" in t:
                            skills_seen.add(t["skill_used"])
                    except json.JSONDecodeError:
                        pass
        trace_summary["skills_seen"] = list(skills_seen)

        from .manifest import evolution_stats as es
        stats = es()

        all_manifests = load_manifests()
        verifier_summary = {
            "total": len(all_manifests),
            "verified": len([m for m in all_manifests if m.verification_status == "verified"]),
            "rolled_back": len([m for m in all_manifests if m.verification_status == "rolled_back"]),
            "pending": len([m for m in all_manifests if m.verification_status == "pending"]),
        }

        history_runs = []
        results_dir = Path(__file__).resolve().parent / "history"
        if results_dir.exists():
            for hf in sorted(results_dir.glob("*.json")):
                try:
                    with open(hf, "r", encoding="utf-8") as f:
                        history_runs.append(json.load(f))
                except (json.JSONDecodeError, OSError):
                    pass

        return {
            "evolution_stats": stats,
            "trace_summary": trace_summary,
            "verifier_summary": verifier_summary,
            "history_runs": history_runs,
        }

    def _save_run(self, result: dict) -> None:
        run_id = result["run_id"]
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        filepath = RESULTS_DIR / f"run-{run_id}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)