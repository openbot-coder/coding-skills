import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

MANIFEST_DIR = Path(__file__).resolve().parent / "manifests"


class Manifest:
    def __init__(
        self,
        edit_id: str,
        change_summary: str,
        component: str,
        file_path: str,
        predicted_impact: dict,
        timestamp: Optional[str] = None,
        verification_status: str = "pending",
        actual_impact: Optional[dict] = None,
        rollback_reason: Optional[str] = None,
    ):
        self.edit_id = edit_id
        self.change_summary = change_summary
        self.component = component
        self.file_path = file_path
        self.predicted_impact = predicted_impact
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.verification_status = verification_status
        self.actual_impact = actual_impact
        self.rollback_reason = rollback_reason

    def to_dict(self) -> dict:
        return {
            "edit_id": self.edit_id,
            "timestamp": self.timestamp,
            "component": self.component,
            "file_path": self.file_path,
            "change_summary": self.change_summary,
            "predicted_impact": self.predicted_impact,
            "verification_status": self.verification_status,
            "actual_impact": self.actual_impact,
            "rollback_reason": self.rollback_reason,
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            edit_id=d["edit_id"],
            change_summary=d.get("change_summary", ""),
            component=d.get("component", ""),
            file_path=d.get("file_path", ""),
            predicted_impact=d.get("predicted_impact", {}),
            timestamp=d.get("timestamp"),
            verification_status=d.get("verification_status", "pending"),
            actual_impact=d.get("actual_impact"),
            rollback_reason=d.get("rollback_reason"),
        )

    def save(self) -> None:
        MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
        filepath = MANIFEST_DIR / f"{self.edit_id}.yaml"
        import yaml
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        self._append_history()

    def mark_verified(self, actual_impact: dict) -> None:
        self.verification_status = "verified"
        self.actual_impact = actual_impact
        self.update()

    def mark_rolled_back(self, reason: str) -> None:
        self.verification_status = "rolled_back"
        self.rollback_reason = reason
        self.update()

    def update(self) -> None:
        self._append_history()
        self.save()

    def _append_history(self) -> None:
        history_file = MANIFEST_DIR / "history.jsonl"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(self.to_dict(), ensure_ascii=False) + "\n")

    def __repr__(self) -> str:
        return f"<Manifest {self.edit_id} [{self.verification_status}]>"


def load_manifests(status: Optional[str] = None) -> list[Manifest]:
    """加载所有 manifest，可选过滤状态"""
    if not MANIFEST_DIR.exists():
        return []

    manifests = []
    for yaml_file in sorted(MANIFEST_DIR.glob("ev-*.yaml")):
        import yaml
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        m = Manifest.from_dict(data)
        if status is None or m.verification_status == status:
            manifests.append(m)
    return manifests


def evolution_stats() -> dict:
    all_manifests = load_manifests()
    verified = [m for m in all_manifests if m.verification_status == "verified"]
    rolled_back = [m for m in all_manifests if m.verification_status == "rolled_back"]
    pending = [m for m in all_manifests if m.verification_status == "pending"]
    return {
        "total_edits": len(all_manifests),
        "verified": len(verified),
        "rolled_back": len(rolled_back),
        "pending": len(pending),
        "success_rate": f"{len(verified) / max(len(all_manifests), 1) * 100:.0f}%",
    }


def next_edit_id() -> str:
    """生成下一个 edit_id：ev-NNN"""
    existing = load_manifests()
    max_num = 0
    for m in existing:
        parts = m.edit_id.split("-")
        if len(parts) >= 2:
            try:
                num = int(parts[1])
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
    return f"ev-{max_num + 1:03d}"