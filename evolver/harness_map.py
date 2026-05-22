from pathlib import Path
from typing import Optional

HARNESS_DIR = Path(__file__).resolve().parent.parent / "harness"

COMPONENT_TYPES = ["prompts", "tools", "middleware", "memory", "evaluation", "unknown"]

FAILURE_TO_COMPONENT = {
    "指令理解偏差": "prompts",
    "工具缺失": "tools",
    "工具行为错误": "tools",
    "上下文溢出": "middleware",
    "安全凭证泄露": "tools",
    "安全注入风险": "tools",
    "高危操作": "tools",
    "重复犯相同错误": "memory",
    "知识缺失": "memory",
    "prompt注入": "prompts",
    "模型行为异常": "prompts",
    "其他失败": "unknown",
}

FAILURE_TO_FILE = {
    "指令理解偏差": "instructions.md",
    "工具缺失": "skill-components/{skill}.md",
    "工具行为错误": "skill-components/{skill}.md",
    "上下文溢出": "instructions.md",
    "安全凭证泄露": "skill-components/security-audit.md",
    "安全注入风险": "skill-components/security-audit.md",
    "高危操作": "skill-components/security-audit.md",
    "重复犯相同错误": "memory/coding_patterns.md",
    "知识缺失": "memory/{skill}_knowledge.md",
    "prompt注入": "instructions.md",
    "模型行为异常": "instructions.md",
    "其他失败": "unknown.md",
}

FAILURE_TO_SUGGESTION = {
    "指令理解偏差": "修改 instructions 中对应指令段",
    "工具缺失": "在 skill-components/ 下新增或修改对应技能文件",
    "工具行为错误": "修正对应技能文件中的逻辑实现",
    "上下文溢出": "增加分块策略或 auto-compact 触发条件",
    "安全凭证泄露": "修复对应技能的安全问题",
    "安全注入风险": "替换危险 API 调用为安全版本",
    "高危操作": "增加使用确认提示",
    "重复犯相同错误": "在 memory/coding_patterns.md 记录该错误模式",
    "知识缺失": "在 memory/ 下补充对应知识文档",
    "prompt注入": "在 instructions.md 中增加输入过滤",
    "模型行为异常": "评估模型版本切换或增加 fallback",
    "其他失败": "需要人工调查",
}


class HarnessMapper:
    def __init__(self, harness_dir: Optional[str] = None):
        self.harness_dir = Path(harness_dir) if harness_dir else HARNESS_DIR

    def _get_skill_file(self, skill_used: Optional[str], template: str) -> str:
        skill_name = skill_used or "unknown"
        return template.replace("{skill}", skill_name)

    def map_failure(self, failure_type: str, skill_used: Optional[str], context: str = "") -> tuple:
        component = FAILURE_TO_COMPONENT.get(failure_type, "unknown")
        file_template = FAILURE_TO_FILE.get(failure_type, "unknown.md")
        file_path = self._get_skill_file(skill_used, file_template)
        suggestion = FAILURE_TO_SUGGESTION.get(failure_type, "需要调查")
        return component, file_path, suggestion

    def list_components(self) -> list[dict]:
        components = []
        for comp_type in COMPONENT_TYPES:
            if comp_type == "unknown":
                continue
            comp_dir = self.harness_dir / comp_type
            components.append({
                "type": comp_type,
                "path": str(comp_dir),
                "exists": comp_dir.exists(),
            })
        return components

    def get_component_files(self, component: str) -> list[Path]:
        comp_dir = self.harness_dir / component
        if not comp_dir.exists():
            return []
        return sorted(comp_dir.glob("*.md"))