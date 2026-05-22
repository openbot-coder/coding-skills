import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from .manifest import Manifest, load_manifests

IMPACT_DEVIATION_THRESHOLD = 0.3


class Verifier:
    def __init__(self, repo_dir: Optional[str] = None):
        self.repo_dir = Path(repo_dir) if repo_dir else Path(__file__).resolve().parent.parent

    def verify_all(self, run_benchmark: Optional[Callable[[], dict]] = None) -> dict:
        pending = load_manifests(status="pending")
        if not pending:
            return {"message": "没有待验证的 manifest"}
        results = {"verified": [], "rolled_back": [], "skipped": []}
        for manifest in pending:
            try:
                if run_benchmark:
                    actual_impact = run_benchmark()
                    passed = self.verify_manifest(manifest, actual_impact)
                    if passed:
                        results["verified"].append(manifest.edit_id)
                    else:
                        self.rollback(manifest)
                        results["rolled_back"].append(manifest.edit_id)
                else:
                    manifest.mark_verified({"note": "no benchmark, auto-verified"})
                    results["verified"].append(manifest.edit_id)
            except Exception as e:
                results["skipped"].append(f"{manifest.edit_id}: {str(e)}")
        return results

    def verify_manifest(self, manifest: Manifest, actual_impact: dict, threshold: float = IMPACT_DEVIATION_THRESHOLD) -> bool:
        predicted = manifest.predicted_impact
        if not predicted:
            manifest.mark_verified({"note": "no prediction"})
            return True
        deviations = []
        for key in predicted:
            if key not in actual_impact:
                continue
            pred_val = self._parse_delta(predicted[key])
            actual_val = self._parse_delta(actual_impact[key])
            if pred_val is not None and actual_val is not None:
                if pred_val != 0:
                    deviation = abs(pred_val - actual_val) / abs(pred_val)
                    deviations.append({"metric": key, "predicted": pred_val, "actual": actual_val, "deviation": f"{deviation:.0%}"})
        if not deviations:
            manifest.mark_verified({"note": "no comparable metrics"})
            return True
        avg_deviation = sum(d["predicted"] - d["actual"] for d in deviations) / len(deviations)
        passed = abs(avg_deviation) / max(abs(sum(d["predicted"] for d in deviations) / len(deviations)), 1) <= threshold
        manifest.mark_verified({"comparison": deviations, "avg_deviation": f"{avg_deviation:.2f}", "passed": passed})
        return passed

    def rollback(self, manifest: Manifest, reason: str = "predicted impact does not match actual"):
        file_path = manifest.file_path
        if self._is_git_repo():
            try:
                result = subprocess.run(
                    ["git", "checkout", "HEAD", "--", file_path],
                    cwd=str(self.repo_dir),
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode == 0:
                    manifest.mark_rolled_back(f"git checkout 成功: {reason}")
                    return
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        manifest.mark_rolled_back(f"无法自动回滚: {reason}")

    def _is_git_repo(self) -> bool:
        return (self.repo_dir / ".git").exists()

    def _parse_delta(self, value) -> Optional[float]:
        if isinstance(value, (int, float)):
            return float(value)
        if not isinstance(value, str):
            return None
        s = value.strip().replace("pp", "").replace("%", "").replace("+", "").replace("−", "-")
        range_match = __import__('re').match(r'([+-]?[\d.]+)~([+-]?[\d.]+)', s)
        if range_match:
            return (float(range_match.group(1)) + float(range_match.group(2))) / 2
        try:
            return float(s)
        except ValueError:
            return None

    def report(self) -> dict:
        all_manifests = load_manifests()
        verified = [m for m in all_manifests if m.verification_status == "verified"]
        rolled_back = [m for m in all_manifests if m.verification_status == "rolled_back"]
        pending = [m for m in all_manifests if m.verification_status == "pending"]
        return {
            "total": len(all_manifests),
            "verified": len(verified),
            "rolled_back": len(rolled_back),
            "pending": len(pending),
            "success_rate": f"{len(verified) / max(len(all_manifests), 1) * 100:.0f}%",
        }