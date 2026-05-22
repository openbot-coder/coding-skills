import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

from .collector import TraceCollector
from .harness_map import HarnessMapper

EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"


class Evidence:
    def __init__(
        self,
        id: str,
        trace_ids: list[str],
        failure_type: str,
        root_cause: str,
        component: str,
        file_path: str,
        suggestion: str,
        frequency: int = 1,
        severity: str = "low",
        evidence_snippets: Optional[list[str]] = None,
    ):
        self.id = id
        self.trace_ids = trace_ids
        self.failure_type = failure_type
        self.root_cause = root_cause
        self.component = component
        self.file_path = file_path
        self.suggestion = suggestion
        self.frequency = frequency
        self.severity = severity
        self.evidence_snippets = evidence_snippets or []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "trace_ids": self.trace_ids,
            "failure_type": self.failure_type,
            "root_cause": self.root_cause,
            "component": self.component,
            "file_path": self.file_path,
            "suggestion": self.suggestion,
            "frequency": self.frequency,
            "severity": self.severity,
            "evidence_snippets": self.evidence_snippets,
        }


class EvidenceDistiller:
    def __init__(self):
        self.collector = TraceCollector()
        self.mapper = HarnessMapper()
        self.failure_patterns = self._build_failure_patterns()

    def distill(self) -> list[Evidence]:
        failed_traces = self.collector.get_failed_traces()
        if not failed_traces:
            return []
        raw_evidences = self._categorize_failures(failed_traces)
        merged_evidences = self._merge_duplicates(raw_evidences)
        self._save_evidences(merged_evidences)
        return merged_evidences

    def analyze_latest(self):
        collect_result = self.collector.collect()
        evidences = self.distill()
        if not evidences:
            return None
        return evidences

    def _categorize_failures(self, failed_traces: list[dict]) -> list[Evidence]:
        evidences = []
        for trace in failed_traces:
            failure_info = trace.get("failure_info", {})
            reason = failure_info.get("reason", "")
            if not reason:
                continue
            failure_type, severity = self._classify(reason)
            component, file_path, suggestion = self.mapper.map_failure(
                failure_type=failure_type,
                skill_used=trace.get("skill_used"),
                context=reason,
            )
            ev = Evidence(
                id=f"evi-{uuid4().hex[:6]}",
                trace_ids=[trace.get("task_id", "")],
                failure_type=failure_type,
                root_cause=self._infer_root_cause(failure_type),
                component=component,
                file_path=file_path,
                suggestion=suggestion,
                frequency=1,
                severity=severity,
                evidence_snippets=[reason[:200]],
            )
            evidences.append(ev)
        return evidences

    def _classify(self, reason: str) -> tuple[str, str]:
        reason_lower = reason.lower()
        for pattern_info in self.failure_patterns:
            keywords = pattern_info.get("keywords", [])
            for kw in keywords:
                if kw.lower() in reason_lower:
                    return pattern_info["type"], pattern_info["severity"]
        return "其他失败", "low"

    def _infer_root_cause(self, failure_type: str) -> str:
        root_causes = {
            "指令理解偏差": "SKILL.md 的指令描述不够清晰或存在歧义",
            "工具缺失": "技能引用的脚本或资源文件路径错误或不存在",
            "工具行为错误": "技能文件中的实现逻辑与意图不一致",
            "上下文溢出": "token 限制导致上下文被截断",
            "安全凭证泄露": "技能文件中存在安全漏洞，需要修复",
            "其他失败": "未能自动分类的失败",
        }
        return root_causes.get(failure_type, "未知失败类型")

    def _merge_duplicates(self, evidences: list[Evidence]) -> list[Evidence]:
        groups = defaultdict(list)
        for ev in evidences:
            key = (ev.failure_type, ev.component)
            groups[key].append(ev)
        merged = []
        for key, ev_list in groups.items():
            if len(ev_list) == 1:
                merged.append(ev_list[0])
            else:
                reference = ev_list[0]
                all_snippets = []
                all_trace_ids = []
                total_freq = 0
                for ev in ev_list:
                    all_snippets.extend(ev.evidence_snippets)
                    all_trace_ids.extend(ev.trace_ids)
                    total_freq += ev.frequency
                severities = [ev.severity for ev in ev_list]
                sev = "high" if "high" in severities else "medium" if "medium" in severities else "low"
                merged.append(Evidence(
                    id=f"evi-{uuid4().hex[:6]}",
                    trace_ids=list(set(all_trace_ids)),
                    failure_type=reference.failure_type,
                    root_cause=reference.root_cause,
                    component=reference.component,
                    file_path=reference.file_path,
                    suggestion=reference.suggestion,
                    frequency=total_freq,
                    severity=sev,
                    evidence_snippets=list(set(all_snippets)),
                ))
        return merged

    def _save_evidences(self, evidences: list[Evidence]) -> None:
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        filepath = EVIDENCE_DIR / "latest.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in evidences], f, ensure_ascii=False, indent=2)

    def _build_failure_patterns(self) -> list[dict]:
        return [
            {"type": "指令理解偏差", "severity": "high", "keywords": ["指令", "prompt", "提示词", "instruct", "推理错误", "误解", "不理解", "instruction", "role", "角色", "system", "system.md"]},
            {"type": "工具缺失", "severity": "high", "keywords": ["未找到工具", "tool not found", "工具不存在", "引用", "路径错误", "file not found", "module not found", "找不到", "not found", "missing", "不存在", "scripts/", ".py", "import error"]},
            {"type": "工具行为错误", "severity": "medium", "keywords": ["执行失败", "execution failed", "执行错误", "runtime error", "运行时错误", "行为异常", "unexpected", "不符合预期", "unexpected output"]},
            {"type": "上下文溢出", "severity": "medium", "keywords": ["context", "上下文", "token", "溢出", "length", "too long", "超出", "truncated", "截断"]},
            {"type": "安全凭证泄露", "severity": "high", "keywords": ["api key", "api_key", "apikey", "secret", "凭证", "credential", "token", "密码", "password", "泄露", "exposed", "hardcoded", "敏感信息", "sensitive"]},
        ]

    def load_evidences(self) -> list[Evidence]:
        filepath = EVIDENCE_DIR / "latest.json"
        if not filepath.exists():
            return []
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Evidence(**d) for d in data]

    def print_summary(self, evidences: list[Evidence]) -> None:
        if not evidences:
            print("没有 evidence 可供展示")
            return
        for ev in evidences:
            sev_icon = {"high": "🔥", "medium": "👍", "low": "🟨"}.get(ev.severity, "❓")
            print(f"{sev_icon} [{ev.severity}] {ev.failure_type} x{ev.frequency}")
            print(f"    🎯 {ev.component} → {ev.file_path}")
            print(f"    💡 {ev.suggestion}")
            if ev.evidence_snippets:
                print(f"    📝 片段: {ev.evidence_snippets[0][:80]}")
            print()