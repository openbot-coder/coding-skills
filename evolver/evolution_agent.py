import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .evidence_distiller import Evidence
from .harness_map import HarnessMapper
from .manifest import Manifest, next_edit_id

HARNESS_DIR = Path(__file__).resolve().parent.parent / "harness"

EDIT_TEMPLATES = {
    "安全凭证泄露": {
        "template": "在技能文件中增加安全约束：\n- 禁止在脚本中硬编码密码、API Key、Token 等\n- 必须使用环境变量或 secrets manager\n- 在 scripts/ 中添加安全扫描检查点",
        "predicted_impact": {"security_score": "+10pp", "pass_rate": "+2~3pp"},
    },
    "安全注入风险": {
        "template": "修复代码注入风险：\n- exec()/eval() → 使用 subprocess.run() 或 ast.literal_eval()\n- os.system() → subprocess.run(shell=False)\n- 在 templates/ 中替换危险 API",
        "predicted_impact": {"security_score": "+15pp", "pass_rate": "+1~2pp"},
    },
    "高危操作": {
        "template": "增加安全防护：\n- chmod 777 → chmod 755 或更严格\n- rm -rf → 添加确认提示\n- sudo → 评估是否真正需要提权",
        "predicted_impact": {"security_score": "+8pp", "pass_rate": "+1pp"},
    },
    "指令理解偏差": {
        "template": "优化指令描述：\n- 在 SKILL.md 的 description 中增加 WHEN 触发场景\n- 增加 WHAT 功能动词\n- 使用结构化示例替代纯文本说明\n- frontmatter 必填字段使用占位符",
        "predicted_impact": {"quality_score": "+5pp", "pass_rate": "+3~5pp"},
    },
    "工具缺失": {
        "template": "修复脚本引用：\n- 检查引用的脚本路径是否存在\n- 使用相对路径：scripts/xxx.py 或 ../scripts/xxx.py\n- 在 SKILL.md 中使用绝对路径标注",
        "predicted_impact": {"pass_rate": "+2~4pp"},
    },
    "上下文溢出": {
        "template": "优化上下文管理：\n- 增加分块策略：大文件分段处理\n- 增加 auto-compact 触发条件\n- 在 instructions 中限制单次处理的代码行数",
        "predicted_impact": {"context_efficiency": "+10%", "pass_rate": "+2~3pp"},
    },
    "重复犯相同错误": {
        "template": "增强长期记忆：\n- 在 memory/coding_patterns.md 记录该错误模式\n- 增加 anti-pattern 条目\n- 在 instructions.md 中增加检查点",
        "predicted_impact": {"repeat_error_rate": "-30%", "pass_rate": "+1~2pp"},
    },
    "知识缺失": {
        "template": "补充知识库：\n- 在 memory/ 下增加对应技术文档\n- 记录最佳实践和常见陷阱\n- 作为 reference 供 skill 加载",
        "predicted_impact": {"knowledge_coverage": "+5%", "pass_rate": "+1pp"},
    },
}


class EvolutionAgent:
    def __init__(self, harness_dir: Optional[str] = None):
        self.harness_dir = Path(harness_dir) if harness_dir else HARNESS_DIR
        self.mapper = HarnessMapper(harness_dir=str(self.harness_dir))

    def propose(self, evidences: list[Evidence]) -> list[tuple[Manifest, str]]:
        if not evidences:
            return []
        proposals = []
        seen_files = set()
        sorted_evidences = sorted(
            evidences,
            key=lambda e: ({"high": 0, "medium": 1, "low": 2}[e.severity], -e.frequency),
        )
        for evidence in sorted_evidences:
            if evidence.file_path in seen_files:
                continue
            seen_files.add(evidence.file_path)
            edit_template = EDIT_TEMPLATES.get(
                evidence.failure_type,
                {"template": f"需要调查 {evidence.failure_type} 并制定修改方案", "predicted_impact": {"pass_rate": "+1pp"}},
            )
            manifest = Manifest(
                edit_id=next_edit_id(),
                component=evidence.component,
                file_path=evidence.file_path,
                change_summary=f"修复 {evidence.failure_type}：{evidence.suggestion}",
                predicted_impact=edit_template["predicted_impact"],
            )
            edit_instructions = (
                f"修改文件: {evidence.file_path}\n"
                f"失败类型: {evidence.failure_type}\n"
                f"根因: {evidence.root_cause}\n"
                f"频率: {evidence.frequency} 次\n"
                f"严重度: {evidence.severity}\n\n"
                f"修改指令:\n{edit_template['template']}\n\n"
                f"证据片段:\n" + "\n".join(f"  - {s}" for s in evidence.evidence_snippets[:3])
            )
            proposals.append((manifest, edit_instructions))
        return proposals

    def apply_proposal(self, manifest: Manifest, edit_instructions: str) -> dict:
        manifest.save()
        edit_dir = self.harness_dir / ".evolver_edits"
        edit_dir.mkdir(parents=True, exist_ok=True)
        edit_path = edit_dir / f"{manifest.edit_id}.md"
        with open(edit_path, "w", encoding="utf-8") as f:
            f.write(edit_instructions)
        return {
            "manifest_id": manifest.edit_id,
            "file_path": manifest.file_path,
            "instructions_path": str(edit_path),
            "status": "pending_verification",
        }

    def list_pending(self) -> list[Manifest]:
        from .manifest import load_manifests
        return load_manifests(status="pending")