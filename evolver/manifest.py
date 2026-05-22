"""
manifest.py — 决策可观测性：Self-Declaration Manifest

AHE 论文第三大支柱：每次编辑 harness 组件时同步记录自我声明 manifest，
包含预测效果和实际效果，验证后更新状态，偏差时触发回滚。

结构：
  Manifest:
    - edit_id: str          # ev-001, ev-002, ...
    - timestamp: str        # ISO 格式
    - component: str        # tools / prompts / middleware / memory / eval / config
    - file_path: str        # 修改的文件路径
    - change_summary: str   # 修改内容描述
    - predicted_impact: dict  # 预测影响 {metric: delta}
    - verification_status: str  # pending / verified / rolled_back
    - actual_impact: dict | None  # 实际影响
    - rollback_reason: str | None  # 回滚原因
"""

import json
import os
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


MANIFESTS_DIR = Path(__file__).resolve().parent / "manifests"
HISTORY_PATH = MANIFESTS_DIR / "history.jsonl"


class Manifest:
    def __init__(
        self,
        edit_id: str,
        component: str,
        file_path: str,
        change_summary: str,
        predicted_impact: dict,
        timestamp: Optional[str] = None,
        verification_status: str = "pending",
        actual_impact: Optional[dict] = None,
        rollback_reason: Optional[str] = None,
    ):
        self.edit_id = edit_id
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.component = component
        self.file_path = file_path
        self.change_summary = change_summary
        self.predicted_impact = predicted_impact
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
    def from_dict(cls, data: dict) -> "Manifest":
        return cls(**data)

    def save(self):
        """保存 manifest 到 manifests/{edit_id}.yaml"""
        MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
        path = MANIFESTS_DIR / f"{self.edit_id}.yaml"
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, allow_unicode=True, default_flow_style=False)
        # 同时追加到 history.jsonl
        with open(HISTORY_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(self.to_dict(), ensure_ascii=False) + "\n")

    def mark_verified(self, actual_impact: dict):
        """验证通过"""
        self.verification_status = "verified"
        self.actual_impact = actual_impact
        self._update_file()

    def mark_rolled_back(self, reason: str):
        """回滚"""
        self.verification_status = "rolled_back"
        self.rollback_reason = reason
        self._update_file()

    def _update_file(self):
        path = MANIFESTS_DIR / f"{self.edit_id}.yaml"
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, allow_unicode=True, default_flow_style=False)


# ============================================================
# 工具函数
# ============================================================

def next_edit_id() -> str:
    """生成下一个 edit_id"""
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
    existing = list(MANIFESTS_DIR.glob("ev-*.yaml"))
    if not existing:
        return "ev-001"
    nums = [int(f.stem.replace("ev-", "")) for f in existing]
    return f"ev-{max(nums) + 1:03d}"


def load_manifests(status: Optional[str] = None) -> list[Manifest]:
    """加载所有 manifest，可选按状态过滤"""
    manifests = []
    for path in sorted(MANIFESTS_DIR.glob("ev-*.yaml")):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data and (status is None or data.get("verification_status") == status):
            manifests.append(Manifest.from_dict(data))
    return manifests


def load_history(limit: int = 50) -> list[dict]:
    """从 history.jsonl 加载历史记录"""
    if not HISTORY_PATH.exists():
        return []
    records = []
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records[-limit:]


def evolution_stats() -> dict:
    """统计进化效果"""
    manifests = load_manifests()
    total = len(manifests)
    verified = sum(1 for m in manifests if m.verification_status == "verified")
    rolled_back = sum(1 for m in manifests if m.verification_status == "rolled_back")
    pending = sum(1 for m in manifests if m.verification_status == "pending")
    return {
        "total_edits": total,
        "verified": verified,
        "rolled_back": rolled_back,
        "pending": pending,
        "success_rate": f"{verified / max(total, 1) * 100:.0f}%",
        "edit_ids": [m.edit_id for m in manifests],
    }
